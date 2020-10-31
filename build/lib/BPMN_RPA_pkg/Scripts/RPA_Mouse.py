import pyautogui


def get_mouse_position():
    return pyautogui.position()


def mouse_move(x: int, y: int, duration: int = 0):
    pyautogui.moveTo(x, y, duration)


def mouse_drag(x: int, y: int):
    pyautogui.dragTo(100, 200)


def mouse_click(button: str='right', clicks: int=1, interval: float=0.25):
    pyautogui.click(button=button,clicks=clicks,interval=interval)


def mouse_doubleclick():
    pyautogui.doubleClick()


def mouse_button_down(button: str='right'):
    pyautogui.mouseDown(button=button)


def mouse_button_up(button: str='right'):
    pyautogui.mouseUp(button=button)


def mouse_scroll_up(clicks: int):
    pyautogui.scroll(clicks)


def mouse_scroll_down(clicks: int):
    pyautogui.scroll(-clicks)


def mouse_scroll_left(clicks: int):
    pyautogui.hscroll(-clicks)


def mouse_scroll_right(clicks: int):
    pyautogui.hscroll(clicks)