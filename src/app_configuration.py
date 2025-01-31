from injector import Module, singleton
from services.email_service import EmailService
from services.detection_service import DetectionService
from services.model_predict_service import ModelPredictService
from app_window import AppWindow

class AppConfiguration(Module):
    def configure(binder):
        # Main App Window
        binder.bind(AppWindow, to=AppWindow, scope=singleton)
        
        # Services
        binder.bind(EmailService, to=EmailService, scope=singleton)        
        binder.bind(DetectionService, to=DetectionService, scope=singleton)
        binder.bind(ModelPredictService, to=ModelPredictService, scope=singleton)