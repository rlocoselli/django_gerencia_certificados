from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.urls import reverse
from .models import (Certificado, CursoAgendamento, Inscricao, Cliente, 
                     Questionario, RespostaUsuario, ItemRespostaUsuario)
from .forms import CertificadoForm, InscricaoPublicaForm, QuestionarioForm
from .services import gerar_certificado_pdf_bytes, enviar_certificado_email


def criar_certificado(request):
    if request.method == 'POST':
        form = CertificadoForm(request.POST)
        if form.is_valid():
            certificado = form.save()
            return redirect('certificados:visualizar_certificado', pk=certificado.pk)
    else:
        form = CertificadoForm()
    return render(request, 'certificados/criar_certificado.html', {'form': form})


def listar_certificados(request):
    certificados = Certificado.objects.select_related('cliente', 'curso', 'agendamento').all()
    return render(request, 'certificados/listar_certificados.html', {'certificados': certificados})


def visualizar_certificado(request, pk):
    certificado = get_object_or_404(
        Certificado.objects.select_related('cliente', 'curso', 'agendamento'),
        pk=pk
    )
    return render(request, 'certificados/certificado.html', {'certificado': certificado})


def inscricao_publica(request):
    agendamento_id = request.GET.get('agendamento') or request.POST.get('agendamento')
    agendamento = None

    if agendamento_id:
        agendamento = get_object_or_404(
            CursoAgendamento.objects.select_related('curso'),
            pk=agendamento_id
        )

    if request.method == 'POST':
        form = InscricaoPublicaForm(request.POST)

        # 1) primeiro valida o form
        if not form.is_valid():
            return render(
                request,
                'certificados/inscricao.html',
                {'form': form, 'agendamento': agendamento, 'agendamento_id': agendamento_id}
            )

        # 2) LGPD (agora pode usar cleaned_data e/ou request.POST)
        if not request.POST.get("lgpd_consent"):
            form.add_error(None, "Você precisa aceitar o termo LGPD para concluir a inscrição.")
            return render(
                request,
                'certificados/inscricao.html',
                {'form': form, 'agendamento': agendamento, 'agendamento_id': agendamento_id}
            )

        # 3) garante que agendamento existe antes de criar inscrição/certificado
        if not agendamento:
            messages.error(request, 'Agendamento inválido.')
            return render(
                request,
                'certificados/inscricao.html',
                {'form': form, 'agendamento': agendamento, 'agendamento_id': agendamento_id}
            )

        cpf = form.cleaned_data['cpf']
        email = form.cleaned_data['email']

        # 4) criar ou atualizar cliente corretamente
        cliente, created = Cliente.objects.update_or_create(
            cpf=cpf,
            defaults={
                'nome': form.cleaned_data['nome'],
                'email': email,
                'data_nascimento': form.cleaned_data['data_nascimento'],
                'telefone': form.cleaned_data.get('telefone', ''),
                'endereco': form.cleaned_data.get('endereco', ''),
                'empresa': form.cleaned_data.get('empresa', ''),
            }
        )

        Inscricao.objects.get_or_create(agendamento=agendamento, cliente=cliente)

        certificado, _ = Certificado.objects.get_or_create(
            cliente=cliente,
            curso=agendamento.curso,
            agendamento=agendamento,
        )

        # Após gravar a inscrição, o próximo passo obrigatório é o questionário.
        return redirect('certificados:responder_questionario', certificado_id=certificado.id)

    # GET
    form = InscricaoPublicaForm()
    return render(
        request,
        'certificados/inscricao.html',
        {'form': form, 'agendamento': agendamento, 'agendamento_id': agendamento_id}
    )


@require_http_methods(["GET", "POST"])
def responder_questionario(request, certificado_id):
    """View para responder o questionário após emissão do certificado"""
    certificado = get_object_or_404(
        Certificado.objects.select_related('cliente', 'curso', 'agendamento'),
        pk=certificado_id
    )
    
    # Obter o questionário: primeiro específico do curso, depois global (sem curso)
    from django.db.models import Prefetch
    
    questionario = Questionario.objects.filter(
        curso=certificado.curso,
        ativo=True
    ).prefetch_related(
        Prefetch('perguntas'),
        'perguntas__opcoes'
    ).first()
    
    if not questionario:
        # Buscar questionário global (sem curso associado)
        questionario = Questionario.objects.filter(
            curso__isnull=True,
            ativo=True
        ).prefetch_related(
            Prefetch('perguntas'),
            'perguntas__opcoes'
        ).first()
    
    if not questionario:
        messages.warning(request, 'Não há questionário disponível para este curso.')
        return redirect('certificados:listar_certificados')
    
    # Verificar se usuário já respondeu
    resposta_existente = RespostaUsuario.objects.filter(
        questionario=questionario,
        cliente=certificado.cliente,
        certificado=certificado
    ).first()
    
    if resposta_existente and request.method == 'GET':
        # Redirecionar para página de agradecimento se já respondeu
        return redirect('certificados:agradecimento_questionario', certificado_id=certificado_id)
    
    if request.method == 'POST':
        form = QuestionarioForm(questionario, request.POST)
        
        if form.is_valid():
            # Criar ou atualizar resposta do usuário
            resposta_usuario, created = RespostaUsuario.objects.get_or_create(
                questionario=questionario,
                cliente=certificado.cliente,
                certificado=certificado,
                defaults={'agendamento': certificado.agendamento}
            )
            
            # Salvar respostas individuais
            for field_name, value in form.cleaned_data.items():
                if field_name.startswith('pergunta_'):
                    pergunta_id = int(field_name.split('_')[1])
                    pergunta = questionario.perguntas.get(id=pergunta_id)
                    
                    # Determinar se é opção ou texto
                    opcao_resposta = None
                    resposta_texto = ''
                    
                    if pergunta.tipo == 'aberto':
                        resposta_texto = value
                    else:
                        # Buscar a opção de resposta
                        opcao_resposta = pergunta.opcoes.filter(valor=value).first()
                    
                    # Criar ou atualizar o item de resposta
                    ItemRespostaUsuario.objects.update_or_create(
                        resposta_usuario=resposta_usuario,
                        pergunta=pergunta,
                        defaults={
                            'opcao_resposta': opcao_resposta,
                            'resposta_texto': resposta_texto
                        }
                    )

            # O certificado é enviado somente após o questionário respondido.
            email_status = 'enviado'
            try:
                pdf_bytes = gerar_certificado_pdf_bytes(certificado)
                enviar_certificado_email(certificado, pdf_bytes)
            except Exception:
                email_status = 'pendente'

            agradecimento_url = reverse('certificados:agradecimento_questionario', args=[certificado_id])
            return redirect(f'{agradecimento_url}?email_status={email_status}')
    else:
        form = QuestionarioForm(questionario)
    
    return render(request, 'certificados/questionario.html', {
        'form': form,
        'questionario': questionario,
        'certificado': certificado,
        'cliente': certificado.cliente,
        'curso': certificado.curso
    })


def agradecimento_questionario(request, certificado_id):
    """Página de agradecimento após responder questionário"""
    certificado = get_object_or_404(
        Certificado.objects.select_related('cliente', 'curso', 'agendamento'),
        pk=certificado_id
    )
    email_status = request.GET.get('email_status')
    
    return render(request, 'certificados/agradecimento_questionario.html', {
        'certificado': certificado,
        'cliente': certificado.cliente,
        'curso': certificado.curso,
        'email_status': email_status,
    })
