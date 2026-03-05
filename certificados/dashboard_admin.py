"""
Admin site customizado para o dashboard de avaliações
"""

from django.contrib import admin
from django.urls import path
from django.template.response import TemplateResponse
from django.db.models import Count

from .models import Questionario, RespostaUsuario, Pergunta


class QuestionarioDashboardAdminSite(admin.AdminSite):
    """Admin site customizado com dashboard de avaliações"""
    
    site_header = "Dashboard de Avaliações"
    site_title = "Dashboard"
    index_title = "Painel de Controle"
    
    def index(self, request, extra_context=None):
        """Página inicial do dashboard"""
        # Estatísticas gerais
        total_questionarios = Questionario.objects.count()
        total_respostas = RespostaUsuario.objects.count()
        total_perguntas = Pergunta.objects.count()
        
        # Respostas por questionário
        respostas_por_questionario = (
            Questionario.objects.annotate(
                num_respostas=Count('respostas_usuarios')
            ).order_by('-num_respostas')[:10]
        )
        
        # Média por questionário
        medias_por_questionario = []
        for q in Questionario.objects.all():
            respostas = q.respostas_usuarios.all()
            if respostas.exists():
                medias = [r.media_geral for r in respostas]
                media_geral = sum(medias) / len(medias) if medias else 0
                medias_por_questionario.append({
                    'questionario': q.titulo,
                    'media': round(media_geral, 2),
                    'total_respostas': respostas.count()
                })
        
        # Últimas respostas
        ultimas_respostas = (
            RespostaUsuario.objects.select_related('cliente', 'questionario')
            .order_by('-respondido_em')[:10]
        )
        
        extra_context = extra_context or {}
        extra_context.update({
            'total_questionarios': total_questionarios,
            'total_respostas': total_respostas,
            'total_perguntas': total_perguntas,
            'respostas_por_questionario': respostas_por_questionario,
            'medias_por_questionario': medias_por_questionario,
            'ultimas_respostas': ultimas_respostas,
        })
        
        return super().index(request, extra_context=extra_context)


# Criar instância do site customizado
dashboard_admin_site = QuestionarioDashboardAdminSite(name='dashboard_questionnaires')
