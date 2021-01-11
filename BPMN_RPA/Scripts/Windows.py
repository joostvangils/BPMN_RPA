from typing import Any

import win32con
import win32gui


class BPMN_RPA_Window(object):
    """
    Dynamic class for the window object.
    """
    pass


def get_foreground_window() -> Any:
    """
    Get the foreground window object.
    :return: The foreground window object.
    """
    hwnd = win32gui.GetForegroundWindow()
    return get_window_object(hwnd)


def window_enumeration_handler(hwnd: int, top_windows: Any):
    """Add window title and ID to array."""
    top_windows.append((hwnd, win32gui.GetWindowText(hwnd)))


def wait_for_window(window_title: str, case_sensitive: bool = False, destroyed: bool = False) -> Any:
    """
    Wait for a specific window with title to appear on- or disappear from the screen.
    :param window_title: The window title to match.
    :param case_sensitive: Optional. Indicator whether the window title should be matched with case sensitivity.
    :param destroyed: Optional. Boolean: indicator where the window should appear/be created (True) or closed/destroyed (False).
    :return: If the window is created, the window object is returned. Otherwise a True value will be returned.
    """
    while True:
        window = find_window(window_title, case_sensitive)
        if not destroyed:
            if window is not None:
                return window
        else:
            if window is None:
                return True


def find_window(title: str, case_sensitive: bool = False) -> Any:
    """
    Find a window with a specific (part of the) window title.
    :param title: The window title (or: part of) to search for.
    :param case_sensitive: Optional. Indicator whether the window title should be matched with case sensitivity.
    :return: If the window is found, the window object is returned. Otherwise a None value will be returned.
    """
    top_windows = []
    hwnd = win32gui.FindWindow(None, title)
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


def get_window_object(hwnd: int) -> Any:
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
        win.WndProc = win32gui.GetWindowLong(hwnd, win32con.GWL_WNDPROC)
    except:
        pass
    return win


def show_window(window: Any) -> bool:
    """
    Show a window in its normal state.
    :param window: The window object to show.
    :return: True if the window can be showed, False otherwise.
    """
    try:
        win32gui.ShowWindow(window.Hwnd, win32con.SW_SHOWNORMAL)
        return True
    except win32gui.error:
        return False


def hide_window(window: Any) -> bool:
    """
    Hide a window.
    :param window: The window object to hide.
    :return: True if the window can be hidden, False otherwise.
    """
    try:
        win32gui.ShowWindow(window.Hwnd, win32con.SW_HIDE)
        return True
    except win32gui.error:
        return False


def close_window(window: Any) -> bool:
    """
    Close a window.
    :param window: The window object to close.
    :return: True if the window can be closed, False otherwise.
    """
    try:
        win32gui.PostMessage(window.Hwnd, win32con.WM_CLOSE, 0, 0)
        return True
    except win32gui.error:
        return False


def set_foreground_window(window: Any) -> bool:
    """
    Set a window to the foreground position.
    :param window: The window object to set to the foreground.
    :return: True if the window can be set to the foreground, False otherwise.
    """
    try:
        win32gui.SetForegroundWindow(window.Hwnd)
        return True
    except win32gui.error:
        return False


def set_window_position(window: Any, position: Any) -> bool:
    """
    Move a window to a specific position on the screen.
    :param window: The window object to move.
    :return: True if the window can be moved, False otherwise.
    """
    try:
        win32gui.MoveWindow(window.Hwnd, position[0], position[1], position[2] - position[0], position[3] - position[1],
                            True)
        return True
    except win32gui.error:
        return False


def focus_window(window: Any):
    """
    Set the focus to a window.
    :param window: The window object to set focus to.
    """
    win32gui.SetFocus(window.Hwnd)
