from PySide6.QtMultimedia import QMediaPlayer
from injector import inject
from services.email_service import EmailService
from services.model_predict_service import ModelPredictService
import cv2
from PySide6.QtCore import QTimer, Signal, QObject, QUrl
from PySide6.QtGui import QImage, QPixmap
from datetime import datetime
import os
import threading
from services.file_system_service import DEFAULT_RESOURCES_PATH


class DetectionService(QObject):
    # Sinal para emitir o progresso do processamento do vídeo
    video_progress_updated = Signal(int)
    # Sinal para emitir o frame processado
    frame_processed = Signal(QImage)

    @inject
    def __init__(self, email_service: EmailService, model_predict_service: ModelPredictService):
        super().__init__()
        self.email_service = email_service
        self.model_predict_service = model_predict_service

    def __update_camera_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            self.camera_label.setText("Falha ao capturar o frame da câmera.")
            return

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        detected_objects_frames = self.model_predict_service.predict(frame_rgb, sync=True, source="video")
        if len(detected_objects_frames) > 0:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"{timestamp}.jpg"
            image_path = os.path.join('resources/images', f"{timestamp}.jpg")

            lock = threading.Lock()

            with lock:
                frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
                cv2.imwrite(image_path, frame_bgr)
                threading.Thread(target=self.email_service.send_email_with_image, args=(file_name,)).start()

        h, w, ch = frame_rgb.shape
        bytes_per_line = ch * w
        q_img = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)

        self.camera_label.setPixmap(QPixmap.fromImage(q_img))

    def detect_in_camera(self, camera_id: int = 0, camera_label=None):
        self.camera_label = camera_label
        self.timer = QTimer()

        self.cap = cv2.VideoCapture(camera_id)

        self.timer.timeout.connect(self.__update_camera_frame)
        self.timer.start(20)

    def stop_camera(self):
        self.timer.stop()
        self.cap.release()

    def detect_in_video(self, video_path: str, video_player: QMediaPlayer):
        self.cap = cv2.VideoCapture(video_path)

        # Configura o timer para processar o vídeo em tempo real
        self.__process_video_frame(video_path, video_player)

    def __process_video_frame(self, video_path, video_player: QMediaPlayer):
        ret, frame = self.cap.read()
        if not ret:
            self.cap.release()
            self.video_progress_updated.emit(100)  # Completo
            return

        # Processa o video completo
        processed_video_path = self.model_predict_service.predict(video_path, sync=False, source="video")
        self.cap = cv2.VideoCapture(processed_video_path)
        video_player.setSource(QUrl.fromLocalFile(processed_video_path))
        video_player.play()

    def get_total_frames(self, video_path: str):
        """
        Retorna o número total de frames no vídeo.
        """
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()
        return total_frames


    def detect_in_image(self, image_path: str):
        self.image = cv2.imread(image_path)
        
        if self.image is None:
            print("Erro ao carregar a imagem.")
            return
        

        frame_rgb = cv2.cvtColor( self.image, cv2.COLOR_BGR2RGB)
        detected_objects_frames = self.model_predict_service.predict(frame_rgb)
        

        if len(detected_objects_frames) > 0:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"{timestamp}.jpg"
            image_path_result = os.path.join(DEFAULT_RESOURCES_PATH, file_name)

            lock = threading.Lock()
            frame_bgr = cv2.cvtColor(detected_objects_frames[0], cv2.COLOR_RGB2BGR)
            with lock:
                
                cv2.imwrite(image_path_result, frame_bgr)
                threading.Thread(target=self.email_service.send_email_with_image, args=(file_name,)).start()
            print("tem retorno")
            return  image_path_result
        else:
             print("nao retorno")
             return  image_path
