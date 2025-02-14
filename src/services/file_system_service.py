import os
from datetime import datetime
import shutil


DEFAULT_RESOURCES_PATH=os.path.join("resources", "images")


class FileSystemService:
    def __init__(self):
        self.check_folder()

    def check_folder(self):
        if not os.path.exists(DEFAULT_RESOURCES_PATH):
            os.makedirs(DEFAULT_RESOURCES_PATH)

    def copy_file(self, source):
        source_filename = os.path.basename(source)
        filename = f'{datetime.timestamp(datetime.now())}_{source_filename}'
        full_destination_path = os.path.join(DEFAULT_RESOURCES_PATH, filename)
        shutil.copy(source, full_destination_path)
        return full_destination_path