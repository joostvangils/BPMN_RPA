import pyautogui
import keyboard


# The BPMN-RPA Keyboard module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# The BPMN-RPA Keyboard module is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


def sendkeys(text: str, interval: float = 0.05):
    """
    Send keys to the foreground window.
    :param text: the text to send to the foreground window.
    :param interval: The text to send to the foreground window.
    """
    pyautogui.write(text, interval=interval)


def press_key(key: str, presses: int = 3, interval: float = 0.05):
    """
    Press a specific key on the keyboard.
    :param key: The key to press.
    :param presses: The number of times the key should be pressed.
    :param interval: The interval between keypresses.
    """
    pyautogui.press(key, presses=presses, interval=interval)


def wait_for_hotkey(key: str, ctrl: bool = False, alt: bool = False, shift: bool = False):
    """
    Wait for a specific hotkey to be pressed.
    :param key: The key on the keyboard.
    :param ctrl: Optional. Boolean: indicator whether the control button should be pressed.
    :param alt: Optional. Boolean: indicator whether the alt button should be pressed.
    :param shift: Optional. Boolean: indicator whether the shift button should be pressed.
    """
    hotkey = key
    if ctrl:
        hotkey += "+ctrl"
    if alt:
        hotkey += "+alt"
    if shift:
        hotkey += "+shift"
    while True:
        if keyboard.is_pressed(hotkey):
            return True


def wait_for_key_release(key: str):
    """
    Wait for a specific key to be released.
    :param key: The key on the keyboard.
    """
    while True:
        if keyboard.is_pressed(key):
            return False


def wait_for_key_press(key: str):
    """
    Wait for a specific key to be pressed.
    :param key: The key on the keyboard.
    """
    while True:
        if keyboard.is_pressed(key):
            return True


def wait_for_key_combination_release(key: str, ctrl: bool = False, alt: bool = False, shift: bool = False):
    """
    Wait for a specific key combination to be released.
    :param key: The key on the keyboard.
    :param ctrl: Optional. Boolean: indicator whether the control button should be pressed.
    :param alt: Optional. Boolean: indicator whether the alt button should be pressed.
    :param shift: Optional. Boolean: indicator whether the shift button should be pressed.
    """
    while True:
        if keyboard.is_pressed(key):
            if ctrl:
                if keyboard.is_pressed("ctrl"):
                    return False
            if alt:
                if keyboard.is_pressed("alt"):
                    return False
            if shift:
                if keyboard.is_pressed("shift"):
                    return False


def wait_for_key_combination_press(key: str, ctrl: bool = False, alt: bool = False, shift: bool = False):
    """
    Wait for a specific key combination to be pressed.
    :param key: The key on the keyboard.
    :param ctrl: Optional. Boolean: indicator whether the control button should be pressed.
    :param alt: Optional. Boolean: indicator whether the alt button should be pressed.
    :param shift: Optional. Boolean: indicator whether the shift button should be pressed.
    """
    while True:
        if keyboard.is_pressed(key):
            if ctrl:
                if keyboard.is_pressed("ctrl"):
                    return True
            if alt:
                if keyboard.is_pressed("alt"):
                    return True
            if shift:
                if keyboard.is_pressed("shift"):
                    return True
