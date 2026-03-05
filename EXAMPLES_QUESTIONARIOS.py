"""
Exemplos de Uso do Sistema de Questionários

Simples exemplos de como usar o sistema programaticamente
"""

from django.shortcuts import render, redirect
from certificados.models import (
    Questionario, Pergunta, OpcaoResposta, RespostaUsuario, ItemRespostaUsuario,
    Cliente, Certificado, CursoAgendamento
)

# ============================================================================
# EXEMPLO 1: Criar um questionário com perguntas via code
# ============================================================================

def criar_questionario_exemplo():
    """Cria um questionário completo programaticamente"""
    
    # Criar o questionário
    questionario = Questionario.objects.create(
        titulo="Avaliação Rápida",
        descricao="Um questionário simples",
        ativo=True
    )
    
    # Criar uma pergunta de escala
    pergunta_escala = Pergunta.objects.create(
        questionario=questionario,
        numero=1,
        texto="Como foi sua experiência?",
        tipo=Pergunta.TIPO_ESCALA,
        obrigatoria=True,
        ordem=1
    )
    
    # Adicionar opções
    OpcaoResposta.objects.create(
        pergunta=pergunta_escala,
        valor="otimo",
        rotulo="Ótimo",
        pontuacao=4,
        ordem=1
    )
    OpcaoResposta.objects.create(
        pergunta=pergunta_escala,
        valor="bom",
        rotulo="Bom",
        pontuacao=3,
        ordem=2
    )
    
    # Criar pergunta aberta
    pergunta_aberta = Pergunta.objects.create(
        questionario=questionario,
        numero=2,
        texto="Deixe seu comentário",
        tipo=Pergunta.TIPO_CAMPO_ABERTO,
        obrigatoria=False,
        ordem=2
    )
    
    return questionario

# ============================================================================
# EXEMPLO 2: Obter um questionário e suas perguntas
# ============================================================================

def obter_questionario_com_perguntas(questionario_id):
    """
    Retorna questionário completo com todas as perguntas e opções
    Útil para construir APIs ou relatórios
    """
    try:
        questionario = Questionario.objects.get(id=questionario_id, ativo=True)
        
        # Obter perguntas ordenadas
        perguntas = questionario.perguntas.all().order_by('ordem', 'numero')
        
        resultado = {
            'id': questionario.id,
            'titulo': questionario.titulo,
            'total_perguntas': perguntas.count(),
            'perguntas': []
        }
        
        for pergunta in perguntas:
            pergunta_data = {
                'id': pergunta.id,
                'numero': pergunta.numero,
                'texto': pergunta.texto,
                'tipo': pergunta.tipo,
                'obrigatoria': pergunta.obrigatoria,
                'opcoes': []
            }
            
            # Se não é pergunta aberta, adicionar opções
            if pergunta.tipo != Pergunta.TIPO_CAMPO_ABERTO:
                opcoes = pergunta.opcoes.all().order_by('ordem')
                pergunta_data['opcoes'] = [
                    {
                        'valor': opt.valor,
                        'rotulo': opt.rotulo,
                        'pontuacao': opt.pontuacao
                    }
                    for opt in opcoes
                ]
            
            resultado['perguntas'].append(pergunta_data)
        
        return resultado
    except Questionario.DoesNotExist:
        return None

# ============================================================================
# EXEMPLO 3: Obter estatísticas de um questionário
# ============================================================================

def obter_estatisticas_questionario(questionario_id):
    """
    Retorna estatísticas agregadas sobre respostas
    """
    try:
        questionario = Questionario.objects.get(id=questionario_id)
        
        respostas = questionario.respostas_usuarios.all()
        
        if not respostas.exists():
            return {
                'total_respostas': 0,
                'media_geral': 0,
                'por_pergunta': []
            }
        
        # Calcular estatísticas por pergunta
        por_pergunta = []
        for pergunta in questionario.perguntas.all().order_by('numero'):
            items = ItemRespostaUsuario.objects.filter(pergunta=pergunta)
            
            if pergunta.tipo == Pergunta.TIPO_CAMPO_ABERTO:
                # Para perguntas abertas, apenas contar
                por_pergunta.append({
                    'numero': pergunta.numero,
                    'texto': pergunta.texto,
                    'tipo': 'aberto',
                    'total_respostas': items.count(),
                    'media': None
                })
            else:
                # Para múltipla/escala, calcular média
                pontuacoes = [
                    item.opcao_resposta.pontuacao 
                    for item in items 
                    if item.opcao_resposta
                ]
                
                media = (
                    sum(pontuacoes) / len(pontuacoes) 
                    if pontuacoes 
                    else 0
                )
                
                por_pergunta.append({
                    'numero': pergunta.numero,
                    'texto': pergunta.texto,
                    'tipo': pergunta.tipo,
                    'total_respostas': len(pontuacoes),
                    'media': round(media, 2)
                })
        
        # Calcular média geral
        medias_geral = [r.media_geral for r in respostas]
        media_geral = (
            sum(medias_geral) / len(medias_geral) 
            if medias_geral 
            else 0
        )
        
        return {
            'total_respostas': respostas.count(),
            'media_geral': round(media_geral, 2),
            'por_pergunta': por_pergunta
        }
    except Questionario.DoesNotExist:
        return None

# ============================================================================
# EXEMPLO 4: Obter respostas de um usuário
# ============================================================================

def obter_respostas_usuario(cliente_id, questionario_id=None):
    """
    Retorna todas as respostas de um usuário
    Opcionalmente filtrado por questionário
    """
    try:
        cliente = Cliente.objects.get(id=cliente_id)
        
        respostas = RespostaUsuario.objects.filter(cliente=cliente)
        
        if questionario_id:
            respostas = respostas.filter(questionario_id=questionario_id)
        
        resultado = []
        for resposta in respostas:
            resposta_data = {
                'id': resposta.id,
                'questionario': resposta.questionario.titulo,
                'respondido_em': resposta.respondido_em,
                'media': resposta.media_geral,
                'itens': []
            }
            
            for item in resposta.itens.all().order_by('pergunta__numero'):
                item_data = {
                    'pergunta_numero': item.pergunta.numero,
                    'pergunta_texto': item.pergunta.texto,
                }
                
                if item.opcao_resposta:
                    item_data['resposta'] = item.opcao_resposta.rotulo
                    item_data['pontuacao'] = item.opcao_resposta.pontuacao
                else:
                    item_data['resposta'] = item.resposta_texto
                    item_data['pontuacao'] = None
                
                resposta_data['itens'].append(item_data)
            
            resultado.append(resposta_data)
        
        return resultado
    except Cliente.DoesNotExist:
        return []

# ============================================================================
# EXEMPLO 5: Exportar respostas para CSV
# ============================================================================

import csv
from io import StringIO
from django.http import HttpResponse

def exportar_respostas_csv(questionario_id):
    """
    Exporta todas as respostas de um questionário para CSV
    """
    try:
        questionario = Questionario.objects.get(id=questionario_id)
        respostas = questionario.respostas_usuarios.all()
        
        # Criar CSV em memória
        output = StringIO()
        writer = csv.writer(output)
        
        # Header
        header = ['Aluno', 'Email', 'Data de Resposta', 'Média']
        # Adicionar cabeçalho de perguntas
        perguntas = questionario.perguntas.all().order_by('numero')
        for p in perguntas:
            header.append(f"Q{p.numero}")
        
        writer.writerow(header)
        
        # Dados
        for resposta in respostas:
            row = [
                resposta.cliente.nome,
                resposta.cliente.email,
                resposta.respondido_em.strftime('%d/%m/%Y %H:%M'),
                f"{resposta.media_geral:.2f}"
            ]
            
            # Adicionar respostas por pergunta
            for pergunta in perguntas:
                item = ItemRespostaUsuario.objects.filter(
                    resposta_usuario=resposta,
                    pergunta=pergunta
                ).first()
                
                if item:
                    if item.opcao_resposta:
                        row.append(item.opcao_resposta.rotulo)
                    else:
                        row.append(item.resposta_texto[:50])  # Primeiros 50 chars
                else:
                    row.append('N/A')
            
            writer.writerow(row)
        
        # Retornar como arquivo
        response = HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="respostas_{questionario_id}.csv"'
        return response
    
    except Questionario.DoesNotExist:
        return HttpResponse("Questionário não encontrado", status=404)

# ============================================================================
# EXEMPLO 6: Filtrar respostas por critérios
# ============================================================================

from django.db.models import Q, Avg

def filtrar_respostas_avancado(
    questionario_id=None,
    curso_id=None,
    data_inicio=None,
    data_fim=None,
    media_minima=None,
):
    """
    Filtro avançado para respostas
    """
    from django.utils import timezone
    from datetime import timedelta
    
    respostas = RespostaUsuario.objects.all()
    
    if questionario_id:
        respostas = respostas.filter(questionario_id=questionario_id)
    
    if curso_id:
        respostas = respostas.filter(agendamento__curso_id=curso_id)
    
    if data_inicio:
        respostas = respostas.filter(respondido_em__gte=data_inicio)
    
    if data_fim:
        respostas = respostas.filter(respondido_em__lte=data_fim)
    
    # Aplicar filtro de média após obter todas
    if media_minima is not None:
        respostas_filtradas = []
        for r in respostas:
            if r.media_geral >= media_minima:
                respostas_filtradas.append(r)
        return respostas_filtradas
    
    return respostas.order_by('-respondido_em')

# ============================================================================
# EXEMPLO 7: Usar no template (context)
# ============================================================================

def view_com_questionario(request, questionario_id):
    """
    View que passa dados do questionário para o template
    """
    questionario = Questionario.objects.get(id=questionario_id, ativo=True)
    
    # Se já respondeu
    ja_respondeu = RespostaUsuario.objects.filter(
        questionario=questionario,
        cliente_id=request.user.id  # Adjust conforme sua autenticação
    ).exists()
    
    context = {
        'questionario': questionario,
        'perguntas': questionario.perguntas.all().order_by('ordem'),
        'ja_respondeu': ja_respondeu,
        'total_respostas': questionario.respostas_usuarios.count(),
    }
    
    return render(request, 'questionario.html', context)

# ============================================================================
# EXEMPLO 8: Análise por opção (para escala/múltipla)
# ============================================================================

def analisar_opcoes_pergunta(pergunta_id):
    """
    Retorna distribuição de respostas para uma pergunta
    """
    try:
        pergunta = Pergunta.objects.get(id=pergunta_id)
        
        if pergunta.tipo == Pergunta.TIPO_CAMPO_ABERTO:
            return None  # Não se aplica a perguntas abertas
        
        resultado = {
            'pergunta': pergunta.texto,
            'tipo': pergunta.tipo,
            'opcoes': {}
        }
        
        for opcao in pergunta.opcoes.all().order_by('ordem'):
            total = ItemRespostaUsuario.objects.filter(
                pergunta=pergunta,
                opcao_resposta=opcao
            ).count()
            
            resultado['opcoes'][opcao.rotulo] = {
                'total': total,
                'percentual': f"{(total / pergunta.questionario.respostas_usuarios.count() * 100):.1f}%" if pergunta.questionario.respostas_usuarios.count() > 0 else "0%"
            }
        
        return resultado
    except Pergunta.DoesNotExist:
        return None

# ============================================================================
# TESTES
# ============================================================================

if __name__ == "__main__":
    # Para testar localmente
    import os
    import django
    
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
    django.setup()
    
    # Testar função 1
    print("Criando questionário...")
    q = criar_questionario_exemplo()
    print(f"Questionário: {q.titulo}")
    
    # Testar função 2
    print("\nObtendo questionário com perguntas...")
    dados = obter_questionario_com_perguntas(q.id)
    print(f"Total de perguntas: {dados['total_perguntas']}")
    
    print("\nExemplos executados com sucesso!")
