import sys
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QTabWidget,
    QFileDialog,
    QLineEdit,
    QMessageBox,
    QFormLayout,
    QCheckBox,
    QProgressBar,
)
from PySide6.QtCore import Qt, QThread, Signal, QSettings
from PySide6.QtGui import QFont, QImage, QPixmap
from injector import inject
from services.detection_service import DetectionService
from services.email_service import EmailService
from PySide6.QtCore import QStandardPaths


# Thread para carregar o vídeo
class VideoLoaderThread(QThread):
    loading_progress_updated = Signal(int)  # Sinal para atualizar o progresso de carregamento
    loading_finished = Signal(str)  # Sinal para indicar que o carregamento foi concluído

    def __init__(self, video_path):
        super().__init__()
        self.video_path = video_path

    def run(self):
        # Simula o carregamento do vídeo
        for i in range(101):
            self.msleep(50)  # Simula um atraso no carregamento
            self.loading_progress_updated.emit(i)  # Atualiza a barra de progresso
        self.loading_finished.emit(self.video_path)  # Emite o sinal de conclusão


# Thread para processar o vídeo
class VideoProcessorThread(QThread):
    processing_progress_updated = Signal(int)  # Sinal para atualizar o progresso de processamento
    processing_finished = Signal()  # Sinal para indicar que o processamento foi concluído

    def __init__(self, video_path, detection_service):
        super().__init__()
        self.video_path = video_path
        self.detection_service = detection_service

    def run(self):
        # Processa o vídeo e atualiza o progresso
        total_frames = self.detection_service.get_total_frames(self.video_path)
        for frame_count in range(total_frames):
            self.msleep(50)  # Simula o processamento de cada frame
            progress = int((frame_count + 1) / total_frames * 100)
            self.processing_progress_updated.emit(progress)
        self.processing_finished.emit()  # Emite o sinal de conclusão


# Janela principal da aplicação
class AppWindow(QMainWindow):
    @inject
    def __init__(self, detection_service: DetectionService, email_service: EmailService):
        super().__init__()
        self.detection_service = detection_service
        self.email_service = email_service
        self.is_camera_started = False

        # Configurações iniciais da janela
        self.setWindowTitle("FIAP VisionGuard")
        self.setGeometry(100, 100, 800, 600)

        # Widget central e layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)

        # Tabs (abas)
        self.tabs = QTabWidget()
        self.tabs.setVisible(False)
        self.layout.addWidget(self.tabs)

        # Carrega as configurações salvas
        self.settings = QSettings("FIAP", "VisionGuard")

        # Adiciona as abas e configurações de e-mail
        self.__add_email_configuration()
        self.__add_image_tab()
        self.__add_video_tab()
        self.__add_camera_tab()
        self.__add_about_tab()

    # Configuração de e-mail
    def __add_email_configuration(self):
        self.email_config_widget = QWidget()
        email_layout = QVBoxLayout(self.email_config_widget)

        # Formulário de e-mail
        form_layout = QFormLayout()
        form_layout.setSpacing(8)

        self.email_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.recipient_input = QLineEdit()

        self.password_label = QLabel(
            '<a href="https://myaccount.google.com/apppasswords">Senha de App (Gmail) 🔗</a>'
        )
        self.password_label.setOpenExternalLinks(True)

        form_layout.addRow("E-mail do remetente:", self.email_input)
        form_layout.addRow(self.password_label, self.password_input)
        form_layout.addRow("E-mail do destinatário:", self.recipient_input)

        # Caixa de seleção "Lembrar"
        self.remember_checkbox = QCheckBox("Lembrar e-mail e senha")
        form_layout.addRow(self.remember_checkbox)

        email_layout.addLayout(form_layout)

        # Botão de validação
        self.validate_button = QPushButton("Validar e Continuar")
        self.validate_button.setFont(QFont("Tahoma", 11))
        self.validate_button.clicked.connect(self.__validate_email_settings)
        email_layout.addWidget(self.validate_button)

        self.layout.addWidget(self.email_config_widget)

        # Carrega os dados salvos, se existirem
        self.__load_saved_settings()

    # Carrega as configurações salvas
    def __load_saved_settings(self):
        email = self.settings.value("email", "")
        password = self.settings.value("password", "")
        recipient = self.settings.value("recipient", "")
        remember = self.settings.value("remember", False, type=bool)

        # Preenche os campos com os dados salvos
        self.email_input.setText(email)
        self.password_input.setText(password)
        self.recipient_input.setText(recipient)
        self.remember_checkbox.setChecked(remember)

    # Valida as configurações de e-mail
    def __validate_email_settings(self):
        sender_email = self.email_input.text().strip()
        app_password = self.password_input.text().strip()
        recipient_email = self.recipient_input.text().strip()

        if not sender_email or not app_password or not recipient_email:
            QMessageBox.warning(self, "Erro", "Todos os campos devem ser preenchidos!")
            return

        (result, error_message) = self.email_service.validate_email(sender_email, app_password)
        if not result:
            QMessageBox.critical(self, "Erro", error_message)
            return

        # Salva os dados se a caixa "Lembrar" estiver marcada
        if self.remember_checkbox.isChecked():
            self.settings.setValue("email", sender_email)
            self.settings.setValue("password", app_password)
            self.settings.setValue("recipient", recipient_email)
            self.settings.setValue("remember", True)
        else:
            # Remove os dados salvos se a caixa "Lembrar" não estiver marcada
            self.settings.remove("email")
            self.settings.remove("password")
            self.settings.remove("recipient")
            self.settings.remove("remember")

        self.email_config_widget.setVisible(False)
        self.tabs.setVisible(True)

        self.email_service.email_sender = sender_email
        self.email_service.email_receiver = recipient_email
        self.email_service.email_password = app_password

    # Aba de imagem
    def __add_image_tab(self):
        image_tab = QWidget()
        self.tabs.addTab(image_tab, "Imagem")

        image_layout = QVBoxLayout(image_tab)

        label = QLabel("Selecione uma imagem:")
        label.setFont(QFont("Tahoma", 12))
        label.setAlignment(Qt.AlignCenter)
        image_layout.addWidget(label)

        image_button = QPushButton("Abrir Imagem")
        image_button.setFont(QFont("Tahoma", 12))
        image_button.clicked.connect(self.__open_image)
        image_layout.addWidget(image_button)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setFixedSize(640, 480)
        self.image_label.setVisible(False)
        image_layout.addWidget(self.image_label)

        image_layout.addStretch()

            # Aba de vídeo
    def __add_video_tab(self):
            video_tab = QWidget()
            self.tabs.addTab(video_tab, "Vídeo")

            # Layout principal da aba de vídeo
            video_layout = QVBoxLayout(video_tab)

            label = QLabel("Selecione um vídeo:")
            label.setFont(QFont("Tahoma", 12))
            label.setAlignment(Qt.AlignCenter)
            video_layout.addWidget(label)

            video_button = QPushButton("Abrir Vídeo")
            video_button.setFont(QFont("Tahoma", 12))
            video_button.clicked.connect(self.__open_video)
            video_layout.addWidget(video_button)

            # Container para centralizar o QLabel do vídeo
            video_container = QWidget()
            video_container_layout = QVBoxLayout(video_container)
            video_container_layout.setAlignment(Qt.AlignCenter)  # Centraliza o conteúdo

            # QLabel para exibir o vídeo
            self.video_label = QLabel()
            self.video_label.setAlignment(Qt.AlignCenter)  # Centraliza o conteúdo dentro do QLabel
            self.video_label.setVisible(False)
            video_container_layout.addWidget(self.video_label)

            # Adiciona o container ao layout principal
            video_layout.addWidget(video_container)

            # Barra de progresso para carregamento do vídeo
            self.loading_progress_bar = QProgressBar()
            self.loading_progress_bar.setVisible(False)
            video_layout.addWidget(self.loading_progress_bar)

            # Barra de progresso para processamento do vídeo
            self.processing_progress_bar = QProgressBar()
            self.processing_progress_bar.setVisible(False)
            video_layout.addWidget(self.processing_progress_bar)

            video_layout.addStretch()

    # Aba de câmera
    def __add_camera_tab(self):
        camera_tab = QWidget()
        self.tabs.addTab(camera_tab, "Câmera")

        camera_layout = QVBoxLayout(camera_tab)

        label = QLabel("Câmera:")
        label.setFont(QFont("Tahoma", 12))
        label.setAlignment(Qt.AlignCenter)
        camera_layout.addWidget(label)

        camera_button = QPushButton("Iniciar/Parar Câmera")
        camera_button.setFont(QFont("Tahoma", 12))
        camera_button.clicked.connect(self.__click_camera)
        camera_layout.addWidget(camera_button)

        self.camera_label = QLabel()
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setVisible(False)
        camera_layout.addWidget(self.camera_label)

        camera_layout.addStretch()

    # Aba "Sobre"
    def __add_about_tab(self):
        about_tab = QWidget()
        self.tabs.addTab(about_tab, "Sobre")

        about_layout = QVBoxLayout(about_tab)

        about_label = QLabel("FIAP VisionGuard\n\nVersão 1.0")
        about_label.setFont(QFont("Tahoma", 12))
        about_label.setAlignment(Qt.AlignCenter)
        about_layout.addWidget(about_label)

        about_layout.addStretch()

    # Abre uma imagem
    def __open_image(self):
        downloads_path = QStandardPaths.writableLocation(QStandardPaths.DownloadLocation)
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("Arquivos de imagem (*.png *.jpg *.jpeg *.webp)")
        file_dialog.setDirectory(downloads_path)

        if file_dialog.exec():
            file_paths = file_dialog.selectedFiles()
            if len(file_paths) > 0:
                image_path = file_paths[0]
                print(f"Selecionado arquivo de imagem: {image_path}")




                result = self.detection_service.detect_in_image(image_path)
                # Exibe a imagem
                self.image_label.setAlignment(Qt.AlignCenter)
                self.image_label.setFixedSize(640, 480)
                image = QImage(result)
                pixmap = QPixmap.fromImage(image)
                #self.image_label.setPixmap(QPixmap.fromImage(image))
                self.image_label.setPixmap(pixmap)
                self.image_label.setScaledContents(True)
                self.image_label.setVisible(True)

                

    # Abre um vídeo
    def __open_video(self):
        downloads_path = QStandardPaths.writableLocation(QStandardPaths.DownloadLocation)
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("Arquivos de vídeo (*.mp4 *.avi)")
        file_dialog.setDirectory(downloads_path)

        if file_dialog.exec():
            file_paths = file_dialog.selectedFiles()
            if len(file_paths) > 0:
                video_path = file_paths[0]
                print(f"Selecionado arquivo de vídeo: {video_path}")

                # Mostra a barra de progresso de carregamento
                self.loading_progress_bar.setVisible(True)
                self.loading_progress_bar.setValue(0)

                # Cria e inicia a thread de carregamento
                self.video_loader_thread = VideoLoaderThread(video_path)
                self.video_loader_thread.loading_progress_updated.connect(self.__update_loading_progress)
                self.video_loader_thread.loading_finished.connect(self.__start_video_processing)
                self.video_loader_thread.start()

    # Atualiza o progresso de carregamento
    def __update_loading_progress(self, value):
        self.loading_progress_bar.setValue(value)

    # Inicia o processamento do vídeo
    def __start_video_processing(self, video_path):
        self.loading_progress_bar.setVisible(False)
        self.processing_progress_bar.setVisible(True)
        self.processing_progress_bar.setValue(0)

        if hasattr(self.detection_service, 'camera_frame_size'):
            width, height = self.detection_service.camera_frame_size
            self.video_label.setFixedSize(width, height)
        else:
            # Tamanho padrão caso o frame da câmera não esteja disponível
            self.video_label.setFixedSize(640, 480)

        # Garante que o vídeo seja redimensionado corretamente
        self.video_label.setScaledContents(True)


        self.video_label.setVisible(True)

        # Conecta os sinais do DetectionService
        self.detection_service.video_progress_updated.connect(self.__update_processing_progress)
        self.detection_service.frame_processed.connect(self.__update_video_frame)

        # Inicia o processamento do vídeo
        self.detection_service.detect_in_video(video_path)

    # Atualiza o progresso de processamento
    def __update_processing_progress(self, value):
        self.processing_progress_bar.setValue(value)

    # Atualiza o frame do vídeo
    def __update_video_frame(self, q_img):
        self.video_label.setPixmap(QPixmap.fromImage(q_img))

    # Finaliza o processamento do vídeo
    def __finish_video_processing(self):
        self.processing_progress_bar.setVisible(False)
        QMessageBox.information(self, "Concluído", "Processamento do vídeo finalizado!")

    # Inicia/para a câmera
    def __click_camera(self):
        if self.is_camera_started:
            self.__stop_camera()
        else:
            self.is_camera_started = True
            self.camera_label.setVisible(True)
            self.detection_service.detect_in_camera(camera_id=0, camera_label=self.camera_label)

    # Para a câmera
    def __stop_camera(self):
        self.camera_label.setVisible(False)
        self.detection_service.stop_camera()
        self.is_camera_started = False

    # Fecha o aplicativo
    def __quit_app(self):
        self.close()