from tkinter import *
from tkinter import filedialog, messagebox
from tkinter.filedialog import askopenfile
from tkinter.ttk import *
from BPMN_RPA.Scripts.Code import Code

window = Tk()
window.title("Module to DrawIO Library")
# window.iconphoto(False, PhotoImage(file='icon.png'))
window.resizable(0, 0)


def get_file():
    fl = askopenfile(mode='r', filetypes=[('Python Files', '*.py')])
    if fl is not None:
        if len(fl.name) > 0:
            textEntry.set(fl.name)


def execute():
    cod = Code()
    if len(textEntry.get()) > 0 and len(txtLib.get()) > 0:
        cod.module_to_library(textEntry.get(), txtLib.get())
        messagebox.showinfo("Done", f"DrawIO Library created for {textEntry.get()} in {txtLib.get()}.")


def select_folder():
    fldr = filedialog.askdirectory()
    if fldr is not None:
        if len(fldr) > 0:
            txtLib.set(fldr)


# Devide window with grid
window.columnconfigure([0, 1, 2, 3], minsize=10)
window.rowconfigure([0, 1, 2, 3, 4, 5], minsize=10)

lblselect = Label(text="Select the Python file:", justify=LEFT).grid(row=1, column=1)
textEntry = StringVar()
file_path = Entry(text="", width=30, textvariable=textEntry).grid(row=2, column=1)
txtLib = StringVar()
lib_folder = Entry(text="", width=30, textvariable=txtLib).grid(row=3, column=1)
btn_open = Button(window, text='Open', command=lambda: get_file()).grid(row=2, column=2)
btn_folder = Button(window, text='Select folder', command=lambda: select_folder()).grid(row=3, column=2)
btn_execute = Button(window, text='Create DrawIo Library for module', command=lambda: execute()).grid(row=4, column=1)

window.mainloop()
