import tkinter
import tkinter.messagebox
import tkinter.simpledialog

# The BPMN-RPA MessageBox module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# The BPMN-RPA MessageBox module is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


def main(title: any, message: any, option="ok") -> int:
    """
    Show a Messagebox on the screen with a specific Title, Message and buttons.
    :param title: The title of the MessageBox.
    :param message: The message of the MessageBox.
    :param option: Optional: 'ok', 'warning', 'error', 'yesno', 'yesnocancel', 'retrycancel', 'askyesnocancel', 'askokcancel'.
    :return: The pushed button.
    """
    root = tkinter.Tk()
    root.withdraw()
    title = str(title)
    message = str(message)
    option = option.lower()
    if option == "ok":
        retn = tkinter.messagebox.showinfo(title, message)
    elif option == "warning":
        retn = tkinter.messagebox.showwarning(title, message)
    elif option == "error":
        retn = tkinter.messagebox.showerror(title, message)
    elif option == "yesno":
        retn = tkinter.messagebox.askyesno(title, message)
    elif option == "yesnocancel":
        retn = tkinter.messagebox.askyesnocancel(title, message)
    elif option == "retrycancel":
        retn = tkinter.messagebox.askretrycancel(title, message)
    elif option == "askyesnocancel":
        retn = tkinter.messagebox.askyesnocancel(title, message)
    elif option == "askokcancel":
        retn = tkinter.messagebox.askokcancel(title, message)
    else:
        retn = None
    root.destroy()
    return retn


def show(title: str, message: str, option: str = "ok") -> int:
    """
    Show a Messagebox on the screen with a specific Title, Message and buttons.
    :param title: The title of the MessageBox.
    :param message: The message of the MessageBox.
    :param option: The icon and buttons of the MessageBox. Options: ok, warning, error, yesno, yesnocancel, retrycancel, askyesnocancel, askokcancel.
    :return: The pushed button.
    """
    root = tkinter.Tk()
    root.withdraw()
    title = str(title)
    message = str(message)
    option = option.lower()
    if option == "ok":
        retn = tkinter.messagebox.showinfo(title, message)
    elif option == "warning":
        retn = tkinter.messagebox.showwarning(title, message)
    elif option == "error":
        retn = tkinter.messagebox.showerror(title, message)
    elif option == "yesno":
        retn = tkinter.messagebox.askyesno(title, message)
    elif option == "yesnocancel":
        retn = tkinter.messagebox.askyesnocancel(title, message)
    elif option == "retrycancel":
        retn = tkinter.messagebox.askretrycancel(title, message)
    elif option == "askyesnocancel":
        retn = tkinter.messagebox.askyesnocancel(title, message)
    elif option == "askokcancel":
        retn = tkinter.messagebox.askokcancel(title, message)
    else:
        retn = None
    root.destroy()
    return retn

def inputbox(title: str, message: str, default: str = "") -> str:
    """
    Show a inputbox on the screen with a specific Title, Message and default value.
    :param title: The title of the inputbox.
    :param message: The message of the inputbox.
    :param default: The default value of the inputbox.
    :return: The input value.
    """
    root = tkinter.Tk()
    root.withdraw()
    title = str(title)
    message = str(message) + "                                               "
    default = str(default)
    retn = tkinter.simpledialog.askstring(title, message, initialvalue=default)
    root.destroy()
    return retn
