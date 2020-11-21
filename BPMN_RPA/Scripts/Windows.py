import win32gui, win32con, win32api


class BPMN_RPA_Window(object):
    pass


def get_foreground_window():
    hwnd = win32gui.GetForegroundWindow()
    return get_window_object(hwnd)


def window_enumeration_handler(hwnd, top_windows):
    """Add window title and ID to array."""
    top_windows.append((hwnd, win32gui.GetWindowText(hwnd)))


def find_window(title, case_sensitive=True):
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
        return get_window_object(windows[0][0])


def get_window_object(hwnd):
    win = BPMN_RPA_Window()
    win.Hwnd = hwnd
    win.Title = win32gui.GetWindowText(hwnd)
    win.Rect = win32gui.GetWindowPlacement(hwnd)
    win.ClassName = win32gui.GetClassName(hwnd)
    win.ParentHwnd = win32gui.GetParent(hwnd)
    win.WndProc = win32gui.GetWindowLong(hwnd, win32con.GWL_WNDPROC)
    return win


def show_window(win):
    try:
        win32gui.ShowWindow(win.Hwnd, win32con.SW_SHOWNORMAL)
        return True
    except win32gui.error:
        return False


def hide_window(win):
    try:
        win32gui.ShowWindow(win.Hwnd, win32con.SW_HIDE)
        return True
    except win32gui.error:
        return False


def close_window(win):
    try:
        win32gui.PostMessage(win.Hwnd, win32con.WM_CLOSE, 0, 0)
        return True
    except win32gui.error:
        return False


def set_foreground_window(win):
    try:
        win32gui.SetForegroundWindow(win.Hwnd)
        return True
    except win32gui.error:
        return False


def set_window_position(win, position):
    try:
        win32gui.MoveWindow(win.Hwnd, position[0], position[1], position[2] - position[0], position[3] - position[1], True)
        return True
    except win32gui.error:
        return False


def focus_window(win):
    win32gui.SetFocus(win.Hwnd)
