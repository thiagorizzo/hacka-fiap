from injector import Injector
from app_configuration import AppConfiguration
from app_window import AppWindow
from PySide6.QtWidgets import QApplication
import sys, os
import gdown

injector = Injector(AppConfiguration.configure)

# Caminho para salvar o modelo
MODEL_DIR = "resources/model"
MODEL_PATH = os.path.join(MODEL_DIR, "model.pt")
MODEL_URL = "https://drive.google.com/uc?id=1-eiFluZMyC33URgVPVAJSlB1_sWaUQVD"

if __name__ == '__main__':
    if not os.path.exists(MODEL_PATH):
        gdown.download(MODEL_URL, MODEL_PATH)
        print("Modelo baixado com sucesso!")
    app = QApplication(sys.argv)

    app_window = injector.get(AppWindow)
    app_window.show()

    sys.exit(app.exec())