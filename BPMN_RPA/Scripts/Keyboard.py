import pyautogui
import keyboard


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
    if ctrl: hotkey += "+ctrl"
    if alt: hotkey += "+alt"
    if shift: hotkey += "+shift"
    while True:
        if keyboard.is_pressed(hotkey):
            return True
    return False
