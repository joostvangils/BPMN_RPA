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
