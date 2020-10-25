from ctypes import byref

from pywinauto import mouse, keyboard
from pywinauto.win32functions import windll
from pywinauto.win32structures import POINT

class RPA_mouse_keyboard:

    def get_mouse_position(self):
        pt = POINT()
        windll.user32.GetCursorPos(byref(pt))
        return [pt.x, pt.y]

    def move_mouse(self, x: int, y: int):
        mouse.move((x, y))

    def mouse_click(self):
        mouse.click("left")

    def mouse_click_right(self):
        mouse.click("right")

    def mouse_double_click(self):
        mouse.double_click("left")

    def send_keys(self, text: str):
        keyboard.send_keys(text)



