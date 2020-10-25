import tkinter, tkinter.messagebox

def main(title, message):
    root = tkinter.Tk()
    root.withdraw()
    tkinter.messagebox.showinfo(title, message)
    root.destroy()
