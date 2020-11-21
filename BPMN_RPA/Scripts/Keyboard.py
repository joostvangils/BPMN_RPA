import pyautogui


def sendkeys(text: str, interval: float = 0.05):
    pyautogui.write(text, interval=interval)


def press_key(key: str, presses: int = 3, interval: float = 0.05):
    pyautogui.press(key, presses=presses, interval=interval)
