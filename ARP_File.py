import os
import shutil


class ARP_File:

    def delete_file(self, fullpath: str):
        os.remove(fullpath)

    def delete_folder(self, fullpath: str):
        os.rmdir(fullpath)

    def move_file(self, source_path: str, destination_path: str):
        shutil.move(source_path, destination_path)