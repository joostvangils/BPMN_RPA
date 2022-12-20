import os
import time
from typing import Any
import pyautogui
import matplotlib.pyplot as plt


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
#
# The BPMN-RPA Images module is based on the PyAutoGUI library, which is licensed under the BSD 3-Clause "New" or "Revised" License:
# Copyright (c) 2014, Al Sweigart
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the PyAutoGUI nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# BPMN-RPA makes also use of the Mathplotlib module, copyright John D. Hunter andf Michael Droettboom, 
# which is licensed under the Python Software Foundation License (PSF):
# 1. This LICENSE AGREEMENT is between the Python Software Foundation
# ("PSF"), and the Individual or Organization ("Licensee") accessing and
# otherwise using this software ("Python") in source or binary form and
# its associated documentation.
# 2. Subject to the terms and conditions of this License Agreement, PSF hereby
# grants Licensee a nonexclusive, royalty-free, world-wide license to reproduce,
# analyze, test, perform and/or display publicly, prepare derivative works,
# distribute, and otherwise use Python alone or in any derivative version,
# provided, however, that PSF's License Agreement and PSF's notice of copyright,
# i.e., "Copyright (c) 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010,
# 2011, 2012 Python Software Foundation; All Rights Reserved" are retained in
# Python alone or in any derivative version prepared by Licensee.
# 3. In the event Licensee prepares a derivative work that is based on
# or incorporates Python or any part thereof, and wants to make
# the derivative work available to others as provided herein, then
# Licensee hereby agrees to include in any such work a brief summary of
# the changes made to Python.
# 4. PSF is making Python available to Licensee on an "AS IS"
# basis.  PSF MAKES NO REPRESENTATIONS OR WARRANTIES, EXPRESS OR
# IMPLIED.  BY WAY OF EXAMPLE, BUT NOT LIMITATION, PSF MAKES NO AND
# DISCLAIMS ANY REPRESENTATION OR WARRANTY OF MERCHANTABILITY OR FITNESS
# FOR ANY PARTICULAR PURPOSE OR THAT THE USE OF PYTHON WILL NOT
# INFRINGE ANY THIRD PARTY RIGHTS.
# 5. PSF SHALL NOT BE LIABLE TO LICENSEE OR ANY OTHER USERS OF PYTHON
# FOR ANY INCIDENTAL, SPECIAL, OR CONSEQUENTIAL DAMAGES OR LOSS AS
# A RESULT OF MODIFYING, DISTRIBUTING, OR OTHERWISE USING PYTHON,
# OR ANY DERIVATIVE THEREOF, EVEN IF ADVISED OF THE POSSIBILITY THEREOF.
# 6. This License Agreement will automatically terminate upon a material
# breach of its terms and conditions.

7. Nothing in this License Agreement shall be deemed to create any
relationship of agency, partnership, or joint venture between PSF and
Licensee.  This License Agreement does not grant permission to use PSF
trademarks or trade name in a trademark sense to endorse or promote
products or services of Licensee, or any third party.

8. By copying, installing or otherwise using Python, Licensee
agrees to be bound by the terms and conditions of this License
Agreement.


class RiskMatrix:

    def __init__(self, title="Risk Matrix", x_label='probability', y_label='Impact'):
        self.plt = plt
        self.fig = self.plt.figure()
        self.plt.subplots_adjust(wspace=0, hspace=0)
        self.plt.xticks([])
        self.plt.yticks([])
        self.plt.xlim(0, 5)
        self.plt.ylim(0, 5)
        self.plt.xlabel(x_label)
        self.plt.ylabel(y_label)
        self.plt.title(title)
        nrows = 5
        ncols = 5
        self.axes = [self.fig.add_subplot(nrows, ncols, r * ncols + c + 1) for r in range(0, nrows) for c in
                     range(0, ncols)]
        for ax in self.axes:
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_xlim(0, 5)
            ax.set_ylim(0, 5)
        self.green = [10, 15, 16, 20, 21]  # Green boxes
        self.yellow = [0, 5, 6, 11, 17, 22, 23]  # yellow boxes
        self.orange = [1, 2, 7, 12, 13, 18, 19, 24]  # orange boxes
        self.red = [3, 4, 8, 9, 14]  # red boxes
        for _ in self.green:
            self.axes[_].set_facecolor('green')
        for _ in self.yellow:
            self.axes[_].set_facecolor('yellow')
        for _ in self.orange:
            self.axes[_].set_facecolor('orange')
        for _ in self.red:
            self.axes[_].set_facecolor('red')

    def plot(self, text, kans=3, effect=3):
        color = 'black'
        if kans == 1 and effect == 1:
            cell = 20
            color = 'white'
        if kans == 1 and effect == 2:
            cell = 21
            color = 'white'
        if kans == 1 and effect == 3:
            cell = 22
        if kans == 1 and effect == 4:
            cell = 23
        if kans == 1 and effect == 5:
            cell = 24
        if kans == 2 and effect == 1:
            cell = 15
            color = 'white'
        if kans == 2 and effect == 2:
            cell = 16
            color = 'white'
        if kans == 2 and effect == 3:
            cell = 17
        if kans == 2 and effect == 4:
            cell = 18
        if kans == 2 and effect == 5:
            cell = 19
        if kans == 3 and effect == 1:
            cell = 10
            color = 'white'
        if kans == 3 and effect == 2:
            cell = 11
        if kans == 3 and effect == 3:
            cell = 12
        if kans == 3 and effect == 4:
            cell = 13
        if kans == 3 and effect == 5:
            cell = 14
            color = 'white'
        if kans == 4 and effect == 1:
            cell = 5
        if kans == 4 and effect == 2:
            cell = 6
        if kans == 4 and effect == 3:
            cell = 7
        if kans == 4 and effect == 4:
            cell = 8
            color = 'white'
        if kans == 4 and effect == 5:
            cell = 9
            color = 'white'
        if kans == 5 and effect == 1:
            cell = 0
        if kans == 5 and effect == 2:
            cell = 1
        if kans == 5 and effect == 3:
            cell = 2
        if kans == 5 and effect == 4:
            cell = 3
            color = 'white'
        if kans == 5 and effect == 5:
            cell = 4
            color = 'white'
        self.axes[cell].text(x=1, y=2.5, s=text, ha='center', va='center', c=color)

    def show(self, bitmap_icon_path=''):
        if len(bitmap_icon_path) > 0:
            thismanager = self.plt.get_current_fig_manager()
            thismanager.window.wm_iconbitmap(bitmap_icon_path)
        self.plt.show()

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
    f = open(path, "r")
    retn = f.read()
    f.close()
    return retn


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


def convert_timezone_to_utc(date: str, timezone="Europe/Amsterdam") -> str:
    """
    Convert a date from my timezone to UTC.
    :param date: The date to convert.
    :param timezone: Optional. The timezone to convert from. Default is Europe/Amsterdam.
    :return: The converted date.
    """
    import datetime
    import pytz
    return datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.timezone(timezone)).astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")


def base64encode(string: str) -> str:
    """
    Encode a string to base64.
    :param string: The string to encode.
    :return: The encoded string.
    """
    import base64
    return base64.b64encode(string.encode()).decode()


def base64decode(string: str) -> str:
    """
    Decode a string from base64.
    :param string: The string to decode.
    :return: The decoded string.
    """
    import base64
    return base64.b64decode(string.encode()).decode()


def string_to_json(string: str) -> dict:
    """
    Convert a string to a JSON object.
    :param string: The string to convert.
    :return: The JSON object.
    """
    import json
    return json.loads(string)


def json_to_string(json_object: dict) -> str:
    """
    Convert a JSON object to a string.
    :param json_object: The JSON object to convert.
    :return: The string.
    """
    import json
    return json.dumps(json_object)


def html_to_plain_text(html: str, strip: bool=True) -> str:
    """
    Convert HTML to plain text.
    :param html: The HTML to convert.
    :param strip: Optional. Whether to strip the text after converting to html. Default is True.
    :return: The plain text.
    """
    # import beautifulsoup4
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text()
    if strip:
        return text.strip()
    return text
