import pyautogui
import keyboard


def sendkeys(text: str, interval: float = 0.05):
    pyautogui.write(text, interval=interval)


def press_key(key: str, presses: int = 3, interval: float = 0.05):
    pyautogui.press(key, presses=presses, interval=interval)


def wait_for_hotkey(key: str, ctrl: bool = False, alt: bool = False, shift: bool = False):
    hotkey = key
    if ctrl: hotkey += "+ctrl"
    if alt: hotkey += "+alt"
    if shift: hotkey += "+shift"
    while True:
        if keyboard.is_pressed(hotkey):
            return True
    return False
