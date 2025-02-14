import os
from datetime import datetime
import cv2
from ultralytics import YOLO
import torch
from file_system_service import FileSystemService, DEFAULT_RESOURCES_PATH


class ModelPredictService:

    def __init__(self):
        self.model = YOLO("resources/model/model.pt")
        self.fs_service = FileSystemService()

    def predict(self, frame, sync = True, source = None):
        size = 640
        conf = 0.1 if source == "video" else 0.4
        device = 0 if torch.cuda.is_available() else "cpu"
        classes = [1,2,3]
        if sync:
            results = self.model.predict(frame, imgsz=size, conf=conf, device=device, classes=classes)
        else:
            path = self.fs_service.copy_file(frame)
            prediction = str(datetime.timestamp(datetime.now()))
            results = self.model.predict(path, imgsz=size, conf=conf, name=prediction, project=DEFAULT_RESOURCES_PATH, save=True, stream=True, device=device, classes=classes)
            [r for r in results]
            prediction_folder_path = os.path.join(DEFAULT_RESOURCES_PATH, prediction)
            [prediction_file] = os.listdir(prediction_folder_path)
            return os.path.join(prediction_folder_path, prediction_file)

        detected_objects_frames = []

        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                confidence = box.conf[0].cpu().numpy()
                cls = box.cls[0].cpu().numpy()
                    
                label = f"{self.model.names[int(cls)]} {confidence:.2f}"
                
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 2)
                cv2.putText(frame, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                detected_objects_frames.append(frame)

        return detected_objects_frames
