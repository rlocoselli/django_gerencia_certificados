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
import requests
import msal
from datetime import date
import locale



from .models import Certificado


def montar_url_inscricao(agendamento_id):
    base = getattr(settings, 'SITE_URL', 'https://leanway-consultores.eastus2.cloudapp.azure.com/').rstrip('/')
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
    try:
        locale.setlocale(locale.LC_TIME, "pt_BR.UTF-8")
    except locale.Error:
        pass

    data_atual = date.today()
    data_formatada = data_atual.strftime("%d de %B de %Y")

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

    # DATA ATUAL
    c.setFont("Helvetica", 14)
    c.drawCentredString(page_w / 2, 235, f"Data: {data_formatada}")

    c.showPage()
    c.save()
    return buffer.getvalue()


def _graph_get_token() -> str:
    tenant_id = getattr(settings, "MS_GRAPH_TENANT_ID", None)
    client_id = getattr(settings, "MS_GRAPH_CLIENT_ID", None)
    client_secret = getattr(settings, "MS_GRAPH_CLIENT_SECRET", None)

    if not all([tenant_id, client_id, client_secret]):
        raise RuntimeError(
            "Configure MS_GRAPH_TENANT_ID, MS_GRAPH_CLIENT_ID, MS_GRAPH_CLIENT_SECRET no settings.py"
        )

    app = msal.ConfidentialClientApplication(
        client_id=client_id,
        authority=f"https://login.microsoftonline.com/{tenant_id}",
        client_credential=client_secret,
    )

    result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    if "access_token" not in result:
        raise RuntimeError(f"Erro ao obter token Graph: {result}")
    return result["access_token"]


def enviar_certificado_email(certificado: Certificado, pdf_bytes: bytes) -> None:
    """
    Envia e-mail via Microsoft Graph (OAuth2) com PDF anexado.
    Requer permission: Microsoft Graph -> Application -> Mail.Send + admin consent.
    """
    cliente = certificado.cliente
    curso = certificado.curso

    sender = getattr(settings, "MS_GRAPH_SENDER", None) or getattr(settings, "DEFAULT_FROM_EMAIL", None)
    if not sender:
        raise RuntimeError("Configure MS_GRAPH_SENDER (ou DEFAULT_FROM_EMAIL) no settings.py")

    assunto = f"Seu certificado - {curso.nome}"
    corpo_texto = (
        f"Olá, {cliente.nome}!\n\n"
        f"Segue em anexo o seu certificado do curso {curso.nome}.\n"
    )

    token = _graph_get_token()

    # Graph sendMail exige anexos em base64
    attachment_b64 = base64.b64encode(pdf_bytes).decode("utf-8")
    filename = f"certificado_{certificado.codigo}.pdf"

    payload = {
        "message": {
            "subject": assunto,
            "body": {
                "contentType": "Text",
                "content": corpo_texto,
            },
            "toRecipients": [
                {"emailAddress": {"address": cliente.email}}
            ],
            "attachments": [
                {
                    "@odata.type": "#microsoft.graph.fileAttachment",
                    "name": filename,
                    "contentType": "application/pdf",
                    "contentBytes": attachment_b64,
                }
            ],
        },
        "saveToSentItems": True,
    }

    url = f"https://graph.microsoft.com/v1.0/users/{sender}/sendMail"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    r = requests.post(url, headers=headers, json=payload, timeout=30)

    # 202 = OK (Accepted)
    if r.status_code != 202:
        raise RuntimeError(f"Graph sendMail falhou: {r.status_code} - {r.text}")
