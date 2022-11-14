import json
import os
import sys
import winreg
from pathlib import Path

# The BPMN-RPA Windows module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# The BPMN-RPA Windows module is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


def get_python_path() -> any:
    """
    Get the path to the Python.exe file
    :return: The path to the Python.exe file
    """
    if os.name == 'nt':
        try:
            reg_path = r"SOFTWARE\BPMN_RPA"
            registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ)
            value, regtype = winreg.QueryValueEx(registry_key, 'PythonPath')
            winreg.CloseKey(registry_key)
            return value
        except WindowsError:
            return None
    else:
        json_file = open('/etc/BPMN_RPA_settings', 'r')
        data = json.load(json_file)
        json_file.close()
        return data["pythonpath"]

GWL_WNDPROC = (-4)
SW_HIDE = 0
SW_SHOWNORMAL = 1
WM_CLOSE = 16
# C:\Python\Lib\site-packages\pywin32_system32
curwd = get_python_path().replace('\\python.exe', '')
os.add_dll_directory(rf"{curwd}\Lib\site-packages\pywin32_system32")
import win32gui

class BPMN_RPA_Window(object):
    """
    Dynamic class for the window object.
    """
    pass


def get_foreground_window() -> any:
    """
    Get the foreground window object.
    :return: The foreground window object.
    The window object contains the following properties:
    - Hwnd: The window handle.
    - Title: The window title.
    - Rect: The window rectangle.
    - ClassName: The window class name.
    - ParentHwnd: The parent window handle.
    - WndProc: The window procedure.
    You can reference these properties by using the dot notation, e.g.: window.Hwnd
    """
    hwnd = win32gui.GetForegroundWindow()
    return get_window_object(hwnd)


def window_enumeration_handler(hwnd: int, top_windows: any):
    """Add window title and ID to array."""
    top_windows.append((hwnd, win32gui.GetWindowText(hwnd)))


def wait_for_window(window_title: str, case_sensitive: bool = False, destroyed: bool = False) -> any:
    """
    Wait for a specific window with title to appear on- or disappear from the screen.
    :param window_title: The window title to match.
    :param case_sensitive: Optional. Indicator whether the window title should be matched with case sensitivity.
    :param destroyed: Optional. Boolean: indicator where the window should appear/be created (True) or closed/destroyed (False).
    :return: If the window is created, the window object is returned. Otherwise a True value will be returned.
    The window object contains the following properties:
    - Hwnd: The window handle.
    - Title: The window title.
    - Rect: The window rectangle.
    - ClassName: The window class name.
    - ParentHwnd: The parent window handle.
    - WndProc: The window procedure.
    You can reference these properties by using the dot notation, e.g.: window.Hwnd
    """
    while True:
        window = find_window(window_title, case_sensitive)
        if not destroyed:
            if window is not None:
                return window
        else:
            if window is None:
                return True


def find_window(title: str, case_sensitive: bool = False) -> any:
    """
    Find a window with a specific (part of the) window title.
    :param title: The window title (or: part of) to search for.
    :param case_sensitive: Optional. Indicator whether the window title should be matched with case sensitivity.
    :return: If the window is found, the window object is returned. Otherwise a None value will be returned.
    The window object contains the following properties:
    - Hwnd: The window handle.
    - Title: The window title.
    - Rect: The window rectangle.
    - ClassName: The window class name.
    - ParentHwnd: The parent window handle.
    - WndProc: The window procedure.
    You can reference these properties by using the dot notation, e.g.: window.Hwnd
    """
    top_windows = []
    win32gui.EnumWindows(window_enumeration_handler, top_windows)
    if case_sensitive:
        windows = [window for window in top_windows if title in window[1]]
    else:
        windows = [window for window in top_windows if title.lower() in window[1].lower()]
    candidates = []
    if len(windows) > 1:
        for window in windows:
            candidates.append(get_window_object(window[0]))
        return candidates
    else:
        if len(windows) > 0:
            return get_window_object(windows[0][0])
        else:
            return None


def get_window_object(hwnd: int) -> any:
    """
    Retrieve the window object from the window handle.
    :param hwnd: The window handle.
    :return: A window object.
    """
    win = BPMN_RPA_Window()
    win.Hwnd = hwnd
    win.Title = win32gui.GetWindowText(hwnd)
    try:
        win.Rect = win32gui.GetWindowPlacement(hwnd)
        win.ClassName = win32gui.GetClassName(hwnd)
        win.ParentHwnd = win32gui.GetParent(hwnd)
        win.WndProc = win32gui.GetWindowLong(hwnd, GWL_WNDPROC)
    except:
        pass
    return win


def show_window(window: any) -> bool:
    """
    Show a window in its normal state.
    :param window: The window object to show.
    :return: True if the window can be showed, False otherwise.
    """
    try:
        win32gui.ShowWindow(window.Hwnd, SW_SHOWNORMAL)
        return True
    except:
        return False


def hide_window(window: any) -> bool:
    """
    Hide a window.
    :param window: The window object to hide.
    :return: True if the window can be hidden, False otherwise.
    """
    try:
        win32gui.ShowWindow(window.Hwnd, SW_HIDE)
        return True
    except:
        return False


def close_window(window: any) -> bool:
    """
    Close a window.
    :param window: The window object to close.
    :return: True if the window can be closed, False otherwise.
    """
    try:
        win32gui.PostMessage(window.Hwnd, WM_CLOSE, 0, 0)
        return True
    except:
        return False


def set_foreground_window(window: any) -> bool:
    """
    Set a window to the foreground position.
    :param window: The window object to set to the foreground.
    :return: True if the window can be set to the foreground, False otherwise.
    """
    try:
        win32gui.SetForegroundWindow(window.Hwnd)
        return True
    except:
        return False


def set_window_position(window: any, position: any) -> bool:
    """
    Move a window to a specific position on the screen.
    :param window: The window object to move.
    :return: True if the window can be moved, False otherwise.
    """
    try:
        win32gui.MoveWindow(window.Hwnd, position[0], position[1], position[2] - position[0], position[3] - position[1],
                            True)
        return True
    except:
        return False


def focus_window(window: any):
    """
    Set the focus to a window.
    :param window: The window object to set focus to.
    """
    win32gui.SetFocus(window.Hwnd)

