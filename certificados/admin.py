from django.contrib import admin, messages
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.db.models import Count, Avg
from django.template.response import TemplateResponse

from .models import (Cliente, Curso, Certificado, CursoAgendamento, Inscricao,
                     Questionario, Pergunta, OpcaoResposta, RespostaUsuario, ItemRespostaUsuario)
from .services import gerar_certificado_pdf_bytes, enviar_certificado_email, montar_url_inscricao, gerar_qr_code_base64_png


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cpf', 'email', 'telefone')
    search_fields = ('nome', 'cpf', 'email')


@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'carga_horaria_padrao')
    search_fields = ('nome',)


class InscricaoInline(admin.TabularInline):
    model = Inscricao
    extra = 0
    autocomplete_fields = ('cliente',)
    readonly_fields = ('criado_em', 'btn_gerar_certificado')
    fields = ('cliente', 'criado_em', 'btn_gerar_certificado')

    def btn_gerar_certificado(self, obj):
        if not obj or not obj.pk:
            return '-'
        url = reverse('admin:certificados_cursoagendamento_gerar_certificado', args=[str(obj.agendamento_id), str(obj.pk)])
        return format_html('<a class="button" href="{}">Gerar certificado</a>', url)

    btn_gerar_certificado.short_description = 'Certificado'


@admin.register(CursoAgendamento)
class CursoAgendamentoAdmin(admin.ModelAdmin):
    list_display = ('curso', 'data', 'id', 'qrcode_link')
    list_filter = ('curso', 'data')
    search_fields = ('curso__nome', 'id')
    readonly_fields = ('id', 'qrcode_preview', 'url_inscricao')
    fields = ('id', 'curso', 'data', 'url_inscricao', 'qrcode_preview')
    inlines = [InscricaoInline]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<uuid:agendamento_id>/inscricao-qrcode/',
                self.admin_site.admin_view(self.qrcode_download_view),
                name='certificados_cursoagendamento_qrcode',
            ),
            path(
                '<uuid:agendamento_id>/gerar-certificado/<int:inscricao_id>/',
                self.admin_site.admin_view(self.gerar_certificado_view),
                name='certificados_cursoagendamento_gerar_certificado',
            ),
        ]
        return custom_urls + urls

    def url_inscricao(self, obj):
        if not obj:
            return '-'
        url = montar_url_inscricao(obj.id)
        return format_html('<a href="{0}" target="_blank">{0}</a>', url)

    url_inscricao.short_description = 'URL de inscrição (aberta)'

    def qrcode_preview(self, obj):
        if not obj or not obj.pk:
            return "-"

        url = montar_url_inscricao(obj.id)
        b64 = gerar_qr_code_base64_png(url)
                
        download_url = reverse('admin:certificados_cursoagendamento_qrcode', args=[str(obj.id)])
        return mark_safe(
            f'''
            <div style="display:flex; gap:16px; align-items:center;">
              <img src="data:image/png;base64,{b64}" style="width:160px; height:160px; border:1px solid #ddd; padding:6px; background:white;" />
              <div>
                <div style="margin-bottom:8px;"><a class="button" href="{download_url}">Baixar QR Code</a></div>
                <div><small>Escaneie para abrir o formulário público.</small></div>
              </div>
            </div>
            '''
        )

    qrcode_preview.short_description = 'QR Code'

    def qrcode_link(self, obj):
        if not obj:
            return '-'
        url = montar_url_inscricao(obj.id)
        return format_html('<a href="{0}" target="_blank">Formulário</a>', url)

    qrcode_link.short_description = 'Link'

    def qrcode_download_view(self, request, agendamento_id):
        agendamento = CursoAgendamento.objects.get(pk=agendamento_id)
        url = montar_url_inscricao(agendamento.id)
        png_bytes = gerar_qr_code_base64_png(url, return_bytes=True)

        response = HttpResponse(png_bytes, content_type='image/png')
        response['Content-Disposition'] = f'attachment; filename="qrcode_{agendamento.id}.png"'
        return response

    def gerar_certificado_view(self, request, agendamento_id, inscricao_id):
        inscricao = Inscricao.objects.select_related('agendamento__curso', 'cliente').get(pk=inscricao_id, agendamento_id=agendamento_id)
        agendamento = inscricao.agendamento
        curso = agendamento.curso
        cliente = inscricao.cliente

        certificado, _ = Certificado.objects.get_or_create(
            cliente=cliente,
            curso=curso,
            agendamento=agendamento,
        )

        pdf_bytes = gerar_certificado_pdf_bytes(certificado)

        try:
            enviar_certificado_email(certificado, pdf_bytes)
            messages.success(request, f'Certificado enviado para {cliente.email}.')
        except Exception as exc:
            messages.error(request, f'Falha ao enviar e-mail: {exc}')

        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="certificado_{certificado.codigo}.pdf"'
        return response


@admin.register(Certificado)
class CertificadoAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'curso', 'agendamento', 'data_emissao', 'codigo')
    list_filter = ('curso', 'data_emissao')
    search_fields = ('cliente__nome', 'cliente__cpf', 'cliente__email', 'curso__nome', 'codigo')


# ========== Questionário e Avaliações ==========

class OpcaoRespostaInline(admin.TabularInline):
    model = OpcaoResposta
    extra = 1
    fields = ('valor', 'rotulo', 'pontuacao', 'ordem')


class PerguntaInline(admin.TabularInline):
    model = Pergunta
    extra = 1
    fields = ('numero', 'texto', 'tipo', 'obrigatoria', 'ordem')


@admin.register(Questionario)
class QuestionarioAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'curso', 'ativo', 'total_perguntas', 'total_respostas')
    list_filter = ('ativo', 'curso', 'criado_em')
    search_fields = ('titulo', 'descricao', 'curso__nome')
    readonly_fields = ('criado_em', 'atualizado_em', 'total_respostas')
    fields = ('titulo', 'descricao', 'curso', 'ativo', 'criado_em', 'atualizado_em', 'total_respostas')
    inlines = [PerguntaInline]
    
    def total_perguntas(self, obj):
        return obj.perguntas.count()
    total_perguntas.short_description = 'Total de Perguntas'
    
    def total_respostas(self, obj):
        return obj.respostas_usuarios.count()
    total_respostas.short_description = 'Total de Respostas'


@admin.register(Pergunta)
class PerguntaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'questionario', 'tipo', 'obrigatoria', 'ordem')
    list_filter = ('tipo', 'obrigatoria', 'questionario')
    search_fields = ('texto', 'questionario__titulo')
    readonly_fields = ('questionario',)
    fields = ('questionario', 'numero', 'texto', 'tipo', 'obrigatoria', 'ordem')
    inlines = [OpcaoRespostaInline]


@admin.register(OpcaoResposta)
class OpcaoRespostaAdmin(admin.ModelAdmin):
    list_display = ('pergunta', 'rotulo', 'valor', 'pontuacao', 'ordem')
    list_filter = ('pergunta__questionario', 'pergunta')
    search_fields = ('rotulo', 'valor', 'pergunta__texto')
    readonly_fields = ('pergunta',)
    fields = ('pergunta', 'valor', 'rotulo', 'pontuacao', 'ordem')


class ItemRespostaUsuarioInline(admin.TabularInline):
    model = ItemRespostaUsuario
    extra = 0
    readonly_fields = ('pergunta', 'opcao_resposta', 'resposta_texto')
    fields = ('pergunta', 'opcao_resposta', 'resposta_texto')
    can_delete = False


@admin.register(RespostaUsuario)
class RespostaUsuarioAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'questionario', 'agendamento', 'media_geral', 'respondido_em')
    list_filter = ('questionario', 'agendamento', 'respondido_em')
    search_fields = ('cliente__nome', 'cliente__email', 'cliente__cpf', 'questionario__titulo')
    readonly_fields = ('questionario', 'cliente', 'certificado', 'agendamento', 'respondido_em', 'media_display')
    fields = ('questionario', 'cliente', 'certificado', 'agendamento', 'respondido_em', 'media_display')
    inlines = [ItemRespostaUsuarioInline]
    can_delete = False
    
    def media_display(self, obj):
        media = obj.media_geral
        if media == 0:
            return "Questionário com respostas abertas apenas"
        return format_html('<strong style="color: green; font-size: 1.2em;">{:.2f}</strong>', media)
    media_display.short_description = 'Média Geral'


@admin.register(ItemRespostaUsuario)
class ItemRespostaUsuarioAdmin(admin.ModelAdmin):
    list_display = ('resposta_usuario', 'pergunta', 'opcao_resposta', 'resposta_texto_preview')
    list_filter = ('pergunta__questionario', 'resposta_usuario__respondido_em')
    search_fields = ('resposta_usuario__cliente__nome', 'pergunta__texto', 'resposta_texto')
    readonly_fields = ('resposta_usuario', 'pergunta', 'opcao_resposta', 'resposta_texto')
    can_delete = False
    
    def resposta_texto_preview(self, obj):
        if obj.resposta_texto:
            preview = obj.resposta_texto[:50]
            if len(obj.resposta_texto) > 50:
                preview += "..."
            return preview
        return "-"
    resposta_texto_preview.short_description = 'Resposta (Preview)'


# ========== Dashboard Customizado ==========

class DashboardQuestionarioAdmin(admin.AdminSite):
    site_header = "Dashboard de Avaliações"
    site_title = "Dashboard"
    index_title = "Painel de Controle"
    
    def index(self, request, extra_context=None):
        """Exibe o dashboard customizado"""
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
        
        # Média por questionário (apenas perguntas com opções)
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


# Registrar sites customizados
questionnaire_admin_site = DashboardQuestionarioAdmin(name='dashboard')

@admin.action(description="Ver Dashboard de Avaliações")
def view_dashboard(modeladmin, request, queryset):
    """Action para redirecionar para o dashboard"""
    return HttpResponseRedirect('/admin/dashboard/')
