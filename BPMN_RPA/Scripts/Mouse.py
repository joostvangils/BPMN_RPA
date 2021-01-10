import pyautogui


def get_mouse_position():
    """
    Retrieve the coordinates of the mouse position.
    :return: Point object with X and Y values.
    """
    return pyautogui.position()


def mouse_move(x: int, y: int, duration: int = 0):
    """
    Move the mouse to a specific coordinate on the screen.
    :param x: The horizontal position on the screen to move to.
    :param y: The vertical position on the screen to move to.
    :param duration: Optional. The time to take for the mouse move.
    """
    pyautogui.moveTo(x, y, duration)


def mouse_drag(x: int, y: int):
    """
    Drag the mouse to a specific coordinate on the screen.
    :param x: The horizontal position on the screen.
    :param y: The vertical position on the screen.
    """
    pyautogui.dragTo(100, 200)


def mouse_click(button: str='right', clicks: int=1, interval: float=0.25):
    """
    Simulate a click on a mouse button.
    :param button: Optional. The button to click (left, right).
    :param clicks: Optional. The number of times the button should be clicked.
    :param interval: Optional. The interval between clicks.
    """
    pyautogui.click(button=button,clicks=clicks,interval=interval)


def mouse_doubleclick():
    """
    Simulate a double-click on the left mouse button.
    """
    pyautogui.doubleClick()


def mouse_button_down(button: str='right'):
    """
    Simulate mouse button down.
    :param button: Optional. The button to press (left, right).
    """
    pyautogui.mouseDown(button=button)


def mouse_button_up(button: str='right'):
    """
    Simulate mouse button up.
    :param button: Optional. The button to relesase (left, right).
    """
    pyautogui.mouseUp(button=button)


def mouse_scroll_up(clicks: int):
    """
    Simulate mouse scroll up.
    :param clicks: number of clicks to scroll up.
    """
    pyautogui.scroll(clicks)


def mouse_scroll_down(clicks: int):
    """
    Simulate mouse scroll down.
    :param clicks: number of clicks to scroll down.
    """
    pyautogui.scroll(-clicks)


def mouse_scroll_left(clicks: int):
    """
    Simulate mouse scroll left.
    :param clicks: number of clicks to scroll left.
    """
    pyautogui.hscroll(-clicks)


def mouse_scroll_right(clicks: int):
    """
    Simulate mouse scroll right.
    :param clicks: number of clicks to scroll right.
    """
    pyautogui.hscroll(clicks)