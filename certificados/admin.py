from django.contrib import admin, messages
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings

from .models import Cliente, Curso, Certificado, CursoAgendamento, Inscricao
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
