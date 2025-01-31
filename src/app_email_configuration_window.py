import sys
import smtplib
from email.mime.text import MIMEText
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QTabWidget,
    QFileDialog,
    QLineEdit,
    QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from injector import inject
from services.detection_service import DetectionService

class EmailConfigWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Configuração de E-mail")
        self.setGeometry(300, 300, 400, 250)

        layout = QVBoxLayout(self)

        self.email_label = QLabel("E-mail do remetente (Gmail):")
        self.email_input = QLineEdit()
        layout.addWidget(self.email_label)
        layout.addWidget(self.email_input)

        self.password_label = QLabel("Senha de App (Gmail):")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)

        self.recipient_label = QLabel("E-mail do destinatário:")
        self.recipient_input = QLineEdit()
        layout.addWidget(self.recipient_label)
        layout.addWidget(self.recipient_input)

        self.validate_button = QPushButton("Validar e Continuar")
        self.validate_button.setFont(QFont("Tahoma", 12))
        self.validate_button.clicked.connect(self.validate_email_settings)
        layout.addWidget(self.validate_button)

    def validate_email_settings(self):
        sender_email = self.email_input.text().strip()
        app_password = self.password_input.text().strip()
        recipient_email = self.recipient_input.text().strip()

        if not sender_email or not app_password or not recipient_email:
            QMessageBox.warning(self, "Erro", "Todos os campos devem ser preenchidos.")
            return

        SMTP_SERVER = "smtp.gmail.com"
        SMTP_PORT = 587

        try:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(sender_email, app_password)
            server.quit()

            QMessageBox.information(self, "Sucesso", "E-mail de teste enviado com sucesso.")

            self.open_main_window(sender_email, app_password, recipient_email)

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao validar e-mail: {e}")

