import smtplib
from email.message import EmailMessage

msg = EmailMessage()
msg["From"] = "certificado@leanway.com.br"
msg["To"] = "locoselli2016@gmail.com"
msg["Subject"] = "Teste SMTP Relay"
msg.set_content("Funcionando via SMTP Relay 🎉")

with smtplib.SMTP("leanway-com-br.mail.protection.outlook.com", 25) as smtp:
    smtp.starttls()  # TLS obrigatório
    smtp.send_message(msg)

print("E-mail enviado com sucesso")
