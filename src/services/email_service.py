from injector import inject
import smtplib
from email.message import EmailMessage
import mimetypes
import os
from PIL import Image
import imagehash


class EmailService:
    @inject
    def __init__(self):
        self.last_image_hash = None
        self.qtdeEnviada = 0
        self.qtdeTotal = 0
        self.qtdeSimilar = 0
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

            if self.is_similar_image(full_image_path):

                return  # Imagem é repetida, não envia o e-mail

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
        


    def is_similar_image(self, image_path, threshold=5):
        """Verifica se a nova imagem é muito semelhante à última enviada"""
        if not os.path.exists(image_path):
            return False
        print(f"Total: {self.qtdeTotal} - Similar: {self.qtdeSimilar} - Enviadas {self.qtdeEnviada}")
       
        self.qtdeTotal += 1
       
        new_hash = imagehash.phash(Image.open(image_path))  # Gera o hash da nova imagem

        if self.last_image_hash is None:
            self.qtdeEnviada +=1; 
            self.last_image_hash = new_hash
            return False  # Primeira imagem, então pode enviar

        # Calcula a diferença entre os hashes (distância de Hamming)
        hash_difference = self.last_image_hash - new_hash

        if hash_difference <= threshold:
            self.qtdeSimilar +=1
            print(f"Imagem muito semelhante à anterior (diferença: {hash_difference}), e-mail não enviado.")
            return True  # A imagem é muito parecida, não precisa enviar

        # Atualiza o último hash enviado
        self.qtdeEnviada +=1; 
        self.last_image_hash = new_hash
        return False  # Imagem diferente, pode enviar