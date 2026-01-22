import base64
from io import BytesIO
from django.conf import settings
from django.core.mail import EmailMessage
from django.urls import reverse

from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

from django.contrib.staticfiles import finders

import qrcode

from .models import Certificado


def montar_url_inscricao(agendamento_id):
    base = getattr(settings, 'SITE_URL', 'http://localhost:8000').rstrip('/')
    return f"{base}{reverse('certificados:inscricao')}?agendamento={agendamento_id}"


def gerar_qr_code_base64_png(texto, return_bytes=False):
    qr = qrcode.QRCode(box_size=8, border=2)
    qr.add_data(texto)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')

    buff = BytesIO()
    img.save(buff, format='PNG')
    png_bytes = buff.getvalue()

    if return_bytes:
        return png_bytes
    return base64.b64encode(png_bytes).decode('utf-8')


def gerar_certificado_pdf_bytes(certificado: Certificado) -> bytes:
    """
    Gera PDF do certificado usando o template:
    static/certificados/img/certificado_base.png
    e escreve SOMENTE: nome, curso e carga horária.
    """
    buffer = BytesIO()

    # O template fornecido é horizontal (paisagem)
    page_w, page_h = landscape(A4)
    c = canvas.Canvas(buffer, pagesize=(page_w, page_h))

    cliente = certificado.cliente
    curso = certificado.curso
    carga = curso.carga_horaria_padrao or 0

    # 1) Background (template)
    template_rel = "certificados/img/certificado_base.png"
    template_path = finders.find(template_rel)
    if not template_path:
        raise FileNotFoundError(
            f"Template não encontrado em static: {template_rel}. "
            f"Verifique se o arquivo existe e se STATICFILES está configurado."
        )

    bg = ImageReader(template_path)
    c.drawImage(bg, 0, 0, width=page_w, height=page_h, mask="auto")

    # 2) Textos por cima (AJUSTE FINO DE POSIÇÃO AQUI)
    # Observação: (0,0) é canto inferior esquerdo.

    # NOME (bem grande, centralizado)
    c.setFont("Helvetica-Bold", 34)
    c.drawCentredString(page_w / 2, 330, cliente.nome)

    # CURSO
    c.setFont("Helvetica", 18)
    c.drawCentredString(page_w / 2, 290, f"Curso: {curso.nome}")

    # CARGA HORÁRIA
    c.setFont("Helvetica", 16)
    c.drawCentredString(page_w / 2, 265, f"Carga horária: {carga} horas")

    c.showPage()
    c.save()
    return buffer.getvalue()


def enviar_certificado_email(certificado: Certificado, pdf_bytes: bytes) -> None:
    cliente = certificado.cliente
    curso = certificado.curso

    assunto = f"Seu certificado - {curso.nome}"
    corpo = (
        f"Olá, {cliente.nome}!\n\n"
        f"Segue em anexo o seu certificado do curso {curso.nome}.\n"
    )

    email_from = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or getattr(settings, 'EMAIL_HOST_USER', None)
    if not email_from:
        raise RuntimeError('Configure DEFAULT_FROM_EMAIL (ou EMAIL_HOST_USER) no settings.py para enviar e-mails.')

    msg = EmailMessage(
        subject=assunto,
        body=corpo,
        from_email=email_from,
        to=[cliente.email],
    )
    msg.attach(f"certificado_{certificado.codigo}.pdf", pdf_bytes, 'application/pdf')
    msg.send(fail_silently=False)
