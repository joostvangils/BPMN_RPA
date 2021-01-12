import tkinter, tkinter.messagebox

def main(title: any, message: any, option ="ok") -> int:
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

