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

        # self.email_label = QLabel("E-mail do remetente (Gmail):")
        # self.email_input = QLineEdit()
        # layout.addWidget(self.email_label)
        # layout.addWidget(self.email_input)

        # self.password_label = QLabel("Senha de App (Gmail):")
        # self.password_input = QLineEdit()
        # self.password_input.setEchoMode(QLineEdit.Password)
        # layout.addWidget(self.password_label)
        # layout.addWidget(self.password_input)

        self.recipient_label = QLabel("E-mail do destinatário:")
        self.recipient_input = QLineEdit()
        layout.addWidget(self.recipient_label)
        layout.addWidget(self.recipient_input)

        self.validate_button = QPushButton("Validar e Continuar")
        self.validate_button.setFont(QFont("Tahoma", 12))
        self.validate_button.clicked.connect(self.validate_email_settings)
        layout.addWidget(self.validate_button)

