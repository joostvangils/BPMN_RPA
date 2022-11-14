import os
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