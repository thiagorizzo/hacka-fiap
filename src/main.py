from injector import Injector
from app_configuration import AppConfiguration
from app_window import AppWindow
from PySide6.QtWidgets import QApplication
import sys

injector = Injector(AppConfiguration.configure)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    app_window = injector.get(AppWindow)
    app_window.show()

    sys.exit(app.exec())

    
    
    