from injector import inject
import smtplib
from email.message import EmailMessage
import mimetypes
import os

class EmailService:
    @inject
    def __init__(self):
        self.email_sender = None
        self.email_receiver = None
        self.email_password = None
        self.smtp_server = 'smtp.gmail.com'
        self.smtp_port = 587
        self.resources_images_path = 'src/resources/images'

    def __send_email(self, image_path: str):
        email_server = smtplib.SMTP(self.smtp_server, self.smtp_port)
        email_server.starttls()
        email_server.login(self.email_sender, self.email_password)

        email_subject = 'Alerta: Objeto perigoso foi detectado!'
        email_body = 'Um objeto perigoso foi detectado. Verifique a imagem em anexo.'

        mime_type, _ = mimetypes.guess_type(image_path)
        if mime_type is None:
            mime_type = 'application/octet-stream'

        msg = EmailMessage()
        msg['Subject'] = email_subject
        msg['From'] = self.email_sender
        msg['To'] = self.email_receiver
        msg.set_content(email_body)

        with open(image_path, 'rb') as img:
            maintype, subtype = mime_type.split('/', 1)
            msg.add_attachment(
                img.read(),
                maintype=maintype,
                subtype=subtype,
                filename=os.path.basename(image_path)
            )

        email_server.send_message(msg)
        email_server.quit()

    def send_email_with_image(self, image_file: str):
        try:
            full_image_path = os.path.join(self.resources_images_path, image_file)
            #self.__send_email(full_image_path)
            print(f'Email enviado para {self.email_receiver} com sucesso.')
        except Exception as e:
            print(f'Erro ao enviar e-mail: {str(e)}')

    def validate_email(self, email_sender: str, email_password: str) -> (bool, str):
        try:
            email_server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            email_server.starttls()
            email_server.login(email_sender, email_password)            
            email_server.quit()
            return (True, None)
        except smtplib.SMTPAuthenticationError:
            return (False, "Falha na autenticação. Verifique seu e-mail e senha de app.")
        except smtplib.SMTPException as e:
            return (False, f"Erro ao conectar ao servidor SMTP: {e}")