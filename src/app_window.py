import sys
import re
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QTabWidget,
    QListView,
    QFileDialog,
    QLineEdit,
    QMessageBox,
    QFormLayout,
    QCheckBox,
    QProgressBar,
)
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtCore import Qt, QThread, Signal, QSettings,QStringListModel
from PySide6.QtGui import QFont, QImage, QPixmap
from injector import inject
from services.detection_service import DetectionService
from services.email_service import EmailService
from PySide6.QtCore import QStandardPaths


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
        self.path_video = ''

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

        self.recipient_input = QLineEdit(self)
        self.recipient_input.setPlaceholderText("Digite o Email de Destinatário e pressione Enter...")
       
        # Caixa de seleção "Lembrar"
        form_layout.addRow("Add E-mail dos destinatários:", self.recipient_input)

        self.list_view = QListView(self)
        self.model = QStringListModel()  # Modelo para armazenar a lista de dados
        self.list_view.setModel(self.model)  # Atribui o modelo ao QListView
        form_layout.addRow("Destinatários:\nClique 2x para Remover", self.list_view)

        email_layout.addLayout(form_layout)

        # Botão de validação
        self.validate_button = QPushButton("Validar e Continuar")
        self.validate_button.setFont(QFont("Tahoma", 11))
        self.validate_button.clicked.connect(self.__validate_email_settings, )
        email_layout.addWidget(self.validate_button)

        self.layout.addWidget(self.email_config_widget)

        #add list
        self.recipient_input.returnPressed.connect(self.add_to_list)
        #remove list
        self.list_view.doubleClicked.connect(self.remove_from_list)
        self.__load_saved_settings()

    # Carrega as configurações salvas
    def __load_saved_settings(self):

        #recipient = self.settings.value("recipient", "")
        remember = self.settings.value("remember", True, type=bool)
        emails = self.settings.value("emails", [])
        self.model.setStringList(emails)  # Preenche o modelo com os e-mails salvos


    # Valida as configurações de e-mail
    def __validate_email_settings(self):

        if len(self.model.stringList()) == 0:
            QMessageBox.warning(self, "Destinatários", "Precisa de ao menos 1 E-mail como destinatário")
            return

        self.email_config_widget.setVisible(False)
        self.tabs.setVisible(True)

        email_list = self.model.stringList()

        # Converte a lista em uma string separada por ";"
       
        self.email_service.email_receiver = ", ".join(email_list)

    def add_to_list(self):

        email = self.recipient_input.text()
        if not self.is_valid_email(email):
            QMessageBox.warning(self, "E-mail inválido", "Por favor, digite um e-mail válido.")
        elif self.is_duplicate(email):
            QMessageBox.warning(self, "E-mail Duplicado","Este e-mail já está na lista.")
        else:
            current_list = self.model.stringList()
            current_list.append(email)
            self.model.setStringList(current_list)
            self.save_emails()  # Salva os e-mails na configuração
            self.recipient_input.clear()
           
     
    def is_valid_email(self, email):
        """Valida se o texto é um e-mail válido"""
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(email_regex, email) is not None
    def is_duplicate(self, email):
        """Verifica se o e-mail já está na lista"""
        current_list = self.model.stringList()
        return email in current_list

    def remove_from_list(self, index):
        """Remove o e-mail da lista ao clicar duplo"""
        row = index.row()
        current_list = self.model.stringList()
        current_list.pop(row)  # Remove o item na posição
        self.model.setStringList(current_list)  # Atualiza a lista
        self.save_emails()  # Salva os e-mails após remoção

    def save_emails(self):
        """Salva a lista de e-mails usando QSettings"""
        emails = self.model.stringList()
        self.settings.setValue("emails", emails)  # Salva a lista como valor


        
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
            self.video_player = QMediaPlayer()
            self.video_label = QVideoWidget()
            self.video_player.setVideoOutput(self.video_label)
            video_container_layout.addWidget(self.video_label)

            # Adiciona o container ao layout principal
            video_layout.addWidget(video_container)

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
        exit_button = QPushButton("Sair")
        exit_button.setFont(QFont("Tahoma", 12))
        exit_button.clicked.connect(self.__quit_app)
        about_layout.addWidget(exit_button)

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
                # Cria e inicia a thread de carregamento
                self.path_video = video_path
                self.__start_video_processing()


    # Inicia o processamento do vídeo
    def __start_video_processing(self):
        if hasattr(self.detection_service, 'camera_frame_size'):
            width, height = self.detection_service.camera_frame_size
            self.video_label.setFixedSize(width, height)
        else:
            # Tamanho padrão caso o frame da câmera não esteja disponível
            self.video_label.setFixedSize(640, 480)

        self.video_label.setVisible(True)
        self.detection_service.detect_in_video(self.path_video, self.video_player)


    # Atualiza o frame do vídeo
    def __update_video_frame(self, q_img):
        self.video_label.setPixmap(QPixmap.fromImage(q_img))

    # Finaliza o processamento do vídeo
    def __finish_video_processing(self):
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
        self.email_config_widget.setVisible(True)
        self.tabs.setVisible(False)
        #self.close()

        
