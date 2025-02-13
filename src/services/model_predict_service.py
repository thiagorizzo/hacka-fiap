import cv2
from ultralytics import YOLO
import torch

class ModelPredictService:

    def __init__(self):
        self.model = YOLO("resources/model/model.pt")

    def predict(self, frame, ):
       
        # if torch.cuda.is_available():
        #     print(f"CUDA está disponível! Usando GPU: {torch.cuda.get_device_name(0)}")
        # else:
        #     print("CUDA não está disponível.")   
        # Run inference on 'bus.jpg' with arguments
        # results = self.model(frame, mgsz=320, conf=0.17, half=True, iou=0.7, device=0)
        #1280 640

        results = self.model.predict(frame, imgsz=640, conf=0.17,  device=0 if torch.cuda.is_available() else "cpu",  )
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
