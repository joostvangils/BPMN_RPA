import json
import os
import time
import winreg

import win32api
import win32con
import win32print
import win32process
import win32service
import win32ts
import winsound


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
#
# The BPMN-RPA Windows module is based on the pywin32 library (copyright Mark Hammond (et al)), which is licensed under the Python Software Foundation License (PSF):
# This LICENSE AGREEMENT is between the Python Software Foundation ("PSF"), and the Individual or Organization ("Licensee") accessing
# and otherwise using this software ("Python") in source or binary form and its associated documentation.
# Subject to the terms and conditions of this License Agreement, PSF hereby grants Licensee a nonexclusive, royalty-free, world-wide
# license to reproduce, analyze, test, perform and/or display publicly, prepare derivative works, distribute, and otherwise use Python
# alone or in any derivative version, provided, however, that PSF's License Agreement and PSF's notice of copyright, i.e., "Copyright (c)
# 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010 Python Software Foundation; All Rights Reserved" are retained in Python
# alone or in any derivative version prepared by Licensee.
# In the event Licensee prepares a derivative work that is based on or incorporates Python or any part thereof, and wants to make the
# derivative work available to others as provided herein, then Licensee hereby agrees to include in any such work a brief summary of
# the changes made to Python.
# PSF is making Python available to Licensee on an "AS IS" basis. PSF MAKES NO REPRESENTATIONS OR WARRANTIES, EXPRESS OR IMPLIED. BY
# WAY OF EXAMPLE, BUT NOT LIMITATION, PSF MAKES NO AND DISCLAIMS ANY REPRESENTATION OR WARRANTY OF MERCHANTABILITY OR FITNESS FOR ANY
# PARTICULAR PURPOSE OR THAT THE USE OF PYTHON WILL NOT INFRINGE ANY THIRD PARTY RIGHTS.
# PSF SHALL NOT BE LIABLE TO LICENSEE OR ANY OTHER USERS OF PYTHON FOR ANY INCIDENTAL, SPECIAL, OR CONSEQUENTIAL DAMAGES OR LOSS AS A
# RESULT OF MODIFYING, DISTRIBUTING, OR OTHERWISE USING PYTHON, OR ANY DERIVATIVE THEREOF, EVEN IF ADVISED OF THE POSSIBILITY THEREOF.
# This License Agreement will automatically terminate upon a material breach of its terms and conditions.
# Nothing in this License Agreement shall be deemed to create any relationship of agency, partnership, or joint venture between PSF and
# Licensee. This License Agreement does not grant permission to use PSF trademarks or trade name in a trademark sense to endorse or
# promote products or services of Licensee, or any third party.
# By copying, installing or otherwise using Python, Licensee agrees to be bound by the terms and conditions of this License Agreement.


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


def get_service_status(service_name: str) -> str:
    """
    Get the status of a Windows service.
    :param service_name: The name of the service to get the status from.
    :return: The status of the service.
    """
    service = win32service.OpenService(win32service.OpenSCManager(None, None, win32service.SC_MANAGER_ALL_ACCESS),
                                       service_name, win32service.SERVICE_ALL_ACCESS)
    status = win32service.QueryServiceStatus(service)
    return status[1]


def start_service(service_name: str) -> bool:
    """
    Start a Windows service.
    :param service_name: The name of the service to start.
    :return: True if the service can be started, False otherwise.
    """
    try:
        service = win32service.OpenService(win32service.OpenSCManager(None, None, win32service.SC_MANAGER_ALL_ACCESS),
                                           service_name, win32service.SERVICE_ALL_ACCESS)
        win32service.StartService(service, None)
        return True
    except:
        return False


def stop_service(service_name: str) -> bool:
    """
    Stop a Windows service.
    :param service_name: The name of the service to stop.
    :return: True if the service can be stopped, False otherwise.
    """
    try:
        service = win32service.OpenService(win32service.OpenSCManager(None, None, win32service.SC_MANAGER_ALL_ACCESS),
                                           service_name, win32service.SERVICE_ALL_ACCESS)
        win32service.ControlService(service, win32service.SERVICE_CONTROL_STOP)
        return True
    except:
        return False


def resume_service(service_name: str) -> bool:
    """
    Resume a Windows service.
    :param service_name: The name of the service to resume.
    :return: True if the service can be resumed, False otherwise.
    """
    try:
        service = win32service.OpenService(win32service.OpenSCManager(None, None, win32service.SC_MANAGER_ALL_ACCESS),
                                           service_name, win32service.SERVICE_ALL_ACCESS)
        win32service.ControlService(service, win32service.SERVICE_CONTROL_CONTINUE)
        return True
    except:
        return False


def log_off_current_user() -> bool:
    """
    Log off the current user.
    :return: True if the user can be logged off, False otherwise.
    """
    try:
        win32ts.WTSLogoffSession(win32ts.WTS_CURRENT_SERVER_HANDLE, win32ts.WTS_CURRENT_SESSION, True)
        return True
    except:
        return False


def shutdown_system() -> bool:
    """
    Shutdown the system.
    :return: True if the system can be shutdown, False otherwise.
    """
    try:
        win32api.InitiateSystemShutdown(None, "Shutdown", 0, True, True)
        return True
    except:
        return False


def restart_system() -> bool:
    """
    Restart the system.
    :return: True if the system can be restarted, False otherwise.
    """
    try:
        win32api.InitiateSystemShutdown(None, "Restart", 0, True, False)
        return True
    except:
        return False


def get_current_user() -> str:
    """
    Get the name of the current user.
    :return: The name of the current user.
    """
    return win32api.GetUserName()


def play_sound(sound_path: str) -> bool:
    """
    Play a sound file.
    :param sound_path: The path to the sound file.
    :return: True if the sound can be played, False otherwise.
    """
    try:
        winsound.PlaySound(sound_path, winsound.SND_FILENAME)
        return True
    except:
        return False


def get_current_volume() -> int:
    """
    Get the current volume.
    :return: The current volume.
    """
    return win32api.GetVolumeInformation(None)[1]


def set_current_volume(volume: int) -> bool:
    """
    Set the current volume.
    :param volume: The volume to set.
    :return: True if the volume can be set, False otherwise.
    """
    try:
        win32api.SetVolume(volume, None)
        return True
    except:
        return False


def get_running_applications() -> list:
    """
    Get a list of running applications.
    :return: A list of running applications.
    """
    return win32process.EnumProcesses()


def kill_running_application(application: str):
    """
    Kill a running application.
    :param application: The name of the application to kill.
    """
    for process in win32process.EnumProcesses():
        if process[1] == application:
            win32process.TerminateProcess(process[0], 0)
            break


def pause_service(service_name: str) -> bool:
    """
    Pause a Windows service.
    :param service_name: The name of the service to pause.
    :return: True if the service can be paused, False otherwise.
    """
    try:
        service = win32service.OpenService(win32service.OpenSCManager(None, None, win32service.SC_MANAGER_ALL_ACCESS),
                                           service_name, win32service.SERVICE_ALL_ACCESS)
        win32service.ControlService(service, win32service.SERVICE_CONTROL_PAUSE)
        return True
    except:
        return False


def wait_for_service(service_name: str, timeout: int = 10) -> bool:
    """
    Wait for a Windows service to start.
    :param service_name: The name of the service to wait for.
    :param timeout: The timeout in seconds.
    :return: True if the service started, False otherwise.
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        if get_service_status(service_name) == win32service.SERVICE_RUNNING:
            return True
        time.sleep(1)
    return False


def get_default_printer() -> str:
    """
    Get the default printer.
    :return: The default printer.
    """
    return win32print.GetDefaultPrinter()


def set_default_printer(printer_name: str) -> bool:
    """
    Set the default printer.
    :param printer_name: The name of the printer to set as default.
    :return: True if the printer can be set as default, False otherwise.
    """
    try:
        win32print.SetDefaultPrinter(printer_name)
        return True
    except:
        return False


def show_desktop() -> bool:
    """
    Show the desktop.
    :return: True if the desktop can be shown, False otherwise.
    """
    try:
        win32gui.PostMessage(win32con.HWND_BROADCAST, win32con.WM_SYSCOMMAND, win32con.SC_MONITORPOWER, 2)
        return True
    except:
        return False


def lock_desktop() -> bool:
    """
    Lock the desktop.
    :return: True if the desktop can be locked, False otherwise.
    """
    try:
        win32gui.PostMessage(win32con.HWND_BROADCAST, win32con.WM_SYSCOMMAND, win32con.SC_MONITORPOWER, 2)
        return True
    except:
        return False


def get_screen_resolution() -> tuple:
    """
    Get the screen resolution.
    :return: The screen resolution.
    """
    return win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1)


def set_screen_resolution(width: int, height: int) -> bool:
    """
    Set the screen resolution.
    :param width: The width of the screen resolution.
    :param height: The height of the screen resolution.
    :return: True if the screen resolution can be set, False otherwise.
    """
    try:
        win32api.ChangeDisplaySettings((width, height), 0)
        return True
    except:
        return False


def control_screensaver(action: int) -> bool:
    """
    Control the screensaver.
    :param action: The action to perform.
    :return: True if the screensaver can be controlled, False otherwise.
    """
    try:
        win32gui.PostMessage(win32con.HWND_BROADCAST, win32con.WM_SYSCOMMAND, win32con.SC_MONITORPOWER, action)
        return True
    except:
        return False


def get_screensaver_status() -> bool:
    """
    Get the screensaver status.
    :return: True if the screensaver is active, False otherwise.
    """
    return win32gui.GetForegroundWindow() == win32gui.GetDesktopWindow()


def open_terminal() -> bool:
    """
    Open a terminal.
    :return: True if a terminal can be opened, False otherwise.
    """
    try:
        os.system("start cmd")
        return True
    except:
        return False


def close_terminal() -> bool:
    """
    Close a terminal.
    :return: True if a terminal can be closed, False otherwise.
    """
    try:
        os.system("taskkill /f /im cmd.exe")
        return True
    except:
        return False


def move_cursor_in_terminal(x: int, y: int) -> bool:
    """
    Move the cursor in a terminal.
    :param x: The x position of the cursor.
    :param y: The y position of the cursor.
    :return: True if the cursor can be moved, False otherwise.
    """
    try:
        win32api.SetCursorPos((x, y))
        return True
    except:
        return False


def get_terminal_cursor_position() -> tuple:
    """
    Get the cursor position in a terminal.
    :return: The cursor position.
    """
    return win32api.GetCursorPos()
