from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Certificado, CursoAgendamento, Inscricao, Cliente
from .forms import CertificadoForm, InscricaoPublicaForm
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
            }
        )

        Inscricao.objects.get_or_create(agendamento=agendamento, cliente=cliente)

        certificado, _ = Certificado.objects.get_or_create(
            cliente=cliente,
            curso=agendamento.curso,
            agendamento=agendamento,
        )

        pdf_bytes = gerar_certificado_pdf_bytes(certificado)

        try:
            enviar_certificado_email(certificado, pdf_bytes)
            messages.success(request, 'Inscrição realizada! Enviamos o certificado por e-mail.')
        except Exception:
            messages.warning(request, 'Inscrição realizada, mas não foi possível enviar o e-mail agora.')

        return render(
            request,
            'certificados/inscricao_sucesso.html',
            {'agendamento': agendamento, 'cliente': cliente, 'certificado': certificado}
        )

    # GET
    form = InscricaoPublicaForm()
    return render(
        request,
        'certificados/inscricao.html',
        {'form': form, 'agendamento': agendamento, 'agendamento_id': agendamento_id}
    )
