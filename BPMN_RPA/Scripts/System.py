import os
import time
from typing import Any
import pyautogui


# The BPMN-RPA System module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# The BPMN-RPA System module is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


def screenshot(path: str) -> str:
    """
    Make a screenshot and save it to file as PNG.
    :param path: The full path of the location and filename (including the PNG extension) to save the screenshot.
    :returns: The pathname of the screenshot file.
    """
    my_screenshot = pyautogui.screenshot()
    my_screenshot.save(path)
    return path


def run_python_code(code: str) -> Any:
    """
    Dynamically run Python code.
    :param code: The code to run.
    :return: OK, or exception when an error occurs.
    """
    try:
        ret = exec(code)
        return ret
    except Exception as ex:
        return ex


def rename_file(filepath: str, newname: str):
    """
    Rename a file. The filepath must be the full path to the file. You may use the wildcard * in the filename.
    P.e. if you use c:\temp\my* as the filepath you will rename all files in the temp directory that start with my. If more than one file exists, a number will be added at the end of the filename.
    :param filepath: The path to the file to rename. You may use the wildcard *. if you use c:\temp\my* as the filepath you will rename all files in the temp directory that start with my. If more than one file exists, a number will be added at the end of the filename.
    :param newname: The new name of the file
    """
    root = ""
    name = ""
    c = 0
    rename = newname
    if filepath.__contains__("\\"):
        root = "\\".join(filepath.split("\\")[:-1]) + "\\"
        name = filepath.split("\\")[-1]
    if filepath.__contains__("/"):
        root = "/".join(filepath.split("/")[:-1]) + "/"
        name = filepath.split("/")[-1]
    for filename in os.listdir(root):
        newname = rename
        if name.__contains__("*"):
            n = name.replace("*", "")
            if filename.startswith(n) and filename.split(".")[0][-2] != "_":
                if c > 0:
                    newname = newname.split(".")[0] + "_" + str(c) + "." + "".join(newname.split(".")[1:])
                os.rename(f"{root}{filename}", f"{root}{newname}")
                c += 1
        else:
            if root + filename == filepath:
                os.rename(f"{root}{filename}", f"{root}{newname}")


def start_windows_program(path: str):
    """
    Start a Windows program.
    :param path: The full path to the program to start.
    """
    os.startfile(path)


def wait(seconds: int):
    """
    Wait for a number of seconds.
    :param seconds: The number of seconds to wait (double).
    """
    time.sleep(seconds)


def get_files_in_folder(path: str) -> list:
    """
    Get a list of files in a folder.
    :param path: The full path to the folder.
    :return: A list of files in the folder.
    """
    return os.listdir(path)


def get_files_in_folder_with_extension(path: str, extension: str) -> list:
    """
    Get a list of files in a folder with a specific extension.
    :param path: The full path to the folder.
    :param extension: The extension of the files to return.
    :return: A list of files in the folder.
    """
    files = []
    for file in os.listdir(path):
        if file.endswith(extension):
            files.append(file)
    return files


def get_files_in_folder_with_wildcard(path: str, wildcard: str) -> list:
    """
    Get a list of files in a folder with a specific wildcard.
    :param path: The full path to the folder.
    :param wildcard: The wildcard of the files to return.
    :return: A list of files in the folder.
    """
    files = []
    for file in os.listdir(path):
        if file.startswith(wildcard):
            files.append(file)
    return files


def copy_file(source: str, destination: str):
    """
    Copy a file.
    :param source: The full path to the file to copy.
    :param destination: The full path to the destination.
    """
    import shutil
    shutil.copy(source, destination)


def move_file(source: str, destination: str):
    """
    Move a file.
    :param source: The full path to the file to move.
    :param destination: The full path to the destination.
    """
    import shutil
    shutil.move(source, destination)


def delete_file(path: str):
    """
    Delete a file.
    :param path: The full path to the file to delete.
    """
    os.remove(path)


def delete_folder(path: str):
    """
    Delete a folder with its contents.
    :param path: The full path to the folder to delete.
    """
    import shutil
    shutil.rmtree(path)


def create_folder(path: str):
    """
    Create a folder.
    :param path: The full path to the folder to create.
    """
    os.mkdir(path)


def read_file(path: str) -> str:
    """
    Read a text file.
    :param path: The full path to the file to read.
    :return: The contents of the file.
    """
    with open(path, "r") as f:
        return f.read()


def write_file(path: str, content: str):
    """
    Write a text file.
    :param path: The full path to the file to write.
    :param content: The contents to write to the file.
    """
    with open(path, "w") as f:
        f.write(content)


def append_file(path: str, content: str):
    """
    Append a text file.
    :param path: The full path to the file to append.
    :param content: The contents to append to the file.
    """
    with open(path, "a") as f:
        f.write(content)


def get_file_size(path: str) -> int:
    """
    Get the size of a file.
    :param path: The full path to the file.
    :return: The size of the file in bytes.
    """
    return os.path.getsize(path)


def get_file_modification_date(path: str) -> str:
    """
    Get the modification date of a file.
    :param path: The full path to the file.
    :return: The modification date of the file.
    """
    return time.ctime(os.path.getmtime(path))


def get_file_extension(path: str) -> str:
    """
    Get the extension part of a file.
    :param path: The full path to the file.
    :return: The extension of the file.
    """
    return path.split(".")[-1]


def empty_folder(path: str):
    """
    Empty a folder.
    :param path: The full path to the folder.
    """
    for file in os.listdir(path):
        os.remove(f"{path}{file}")


def move_folder(source: str, destination: str):
    """
    Move a folder.
    :param source: The full path to the folder to move.
    :param destination: The full path to the destination.
    """
    import shutil
    shutil.move(source, destination)


def copy_folder(source: str, destination: str):
    """
    Copy a folder.
    :param source: The full path to the folder to copy.
    :param destination: The full path to the destination.
    """
    import shutil
    shutil.copytree(source, destination)


def get_folder_size(path: str) -> int:
    """
    Get the size of a folder.
    :param path: The full path to the folder.
    :return: The size of the folder in bytes.
    """
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size


def get_folder_modification_date(path: str) -> str:
    """
    Get the modification date of a folder.
    :param path: The full path to the folder.
    :return: The modification date of the folder.
    """
    return time.ctime(os.path.getmtime(path))


def rename_folder(path: str, new_name: str):
    """
    Rename a folder.
    :param path: The full path to the folder.
    :param new_name: The new name of the folder.
    """
    os.rename(path, new_name)


def zip_file(path: str, destination: str):
    """
    Zip a file.
    :param path: The full path to the file to zip.
    :param destination: The full path to the destination.
    """
    import zipfile
    with zipfile.ZipFile(destination, "w") as f:
        f.write(path)


def zip_folder(path: str, destination: str):
    """
    Zip a folder.
    :param path: The full path to the folder to zip.
    :param destination: The full path to the destination.
    """
    import zipfile
    with zipfile.ZipFile(destination, "w") as f:
        for file in os.listdir(path):
            f.write(f"{path}{file}")


def unzip_file(path: str, destination: str):
    """
    Unzip a file.
    :param path: The full path to the file to unzip.
    :param destination: The full path to the destination.
    """
    import zipfile
    with zipfile.ZipFile(path, "r") as f:
        f.extractall(destination)


def unzip_folder(path: str, destination: str):
    """
    Unzip a folder.
    :param path: The full path to the folder to unzip.
    :param destination: The full path to the destination.
    """
    import zipfile
    with zipfile.ZipFile(path, "r") as f:
        f.extractall(destination)


def set_clipboard(content: str):
    """
    Set the clipboard content.
    :param content: The content to set the clipboard to.
    """
    import pyperclip
    pyperclip.copy(content)


def get_clipboard() -> str:
    """
    Get the clipboard content.
    :return: The content of the clipboard.
    """
    import pyperclip
    return pyperclip.paste()


def clear_clipboard():
    """
    Clear the clipboard.
    """
    import pyperclip
    pyperclip.copy("")


def get_current_folder() -> str:
    """
    Get the current folder.
    :return: The current folder.
    """
    return os.getcwd()


def change_folder(path: str):
    """
    Change the current folder.
    :param path: The full path to the folder to change to.
    """
    os.chdir(path)


def does_folder_contain_file(path: str, file_name: str) -> bool:
    """
    Check if a folder contains a file.
    :param path: The full path to the folder.
    :param file_name: The name of the file to check for.
    :return: True if the folder contains the file, False otherwise.
    """
    return file_name in os.listdir(path)


def does_folder_contain_folder(path: str, folder_name: str) -> bool:
    """
    Check if a folder contains a folder.
    :param path: The full path to the folder.
    :param folder_name: The name of the folder to check for.
    :return: True if the folder contains the folder, False otherwise.
    """
    for file in os.listdir(path):
        if os.path.isdir(file) and file == folder_name:
            return True
    return False


def does_folder_contain_file_with_extension(path: str, extension: str) -> bool:
    """
    Check if a folder contains a file with a specific extension.
    :param path: The full path to the folder.
    :param extension: The extension to check for.
    :return: True if the folder contains a file with the extension, False otherwise.
    """
    for file in os.listdir(path):
        if file.split(".")[-1] == extension:
            return True
    return False


def get_folder_permissions(path: str) -> str:
    """
    Get the permissions of a folder.
    :param path: The full path to the folder.
    :return: The permissions of the folder.
    """
    return oct(os.stat(path).st_mode)[-3:]


def set_folder_permissions(path: str, permissions: str):
    """
    Set the permissions of a folder.
    :param path: The full path to the folder.
    :param permissions: The permissions to set the folder to.
    """
    os.chmod(path, int(permissions, 8))
