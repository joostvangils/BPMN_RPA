from tkinter import *
from tkinter import filedialog, messagebox
from tkinter.filedialog import askopenfile
from tkinter.ttk import *
from BPMN_RPA.Scripts.Code import Code

window = Tk()
window.title("Sort DrawIO Library")
window.iconphoto(False, PhotoImage(file='icon.png'))
window.resizable(0, 0)


def get_file():
    fl = askopenfile(mode='r', filetypes=[('XML files', '*.xml')])
    if fl is not None:
        if len(fl.name) > 0:
            textEntry.set(fl.name)


def execute():
    cod = Code()
    if len(textEntry.get()) > 0:
        cod.sort_library(textEntry.get())
        messagebox.showinfo("Done", f"DrawIO Library {textEntry.get()} sorted.")





# Devide window with grid
window.columnconfigure([0, 1, 2, 3], minsize=10)
window.rowconfigure([0, 1, 2, 3, 4, 5], minsize=10)

lblselect = Label(text="Select the DrawIO Library file:", justify=LEFT).grid(row=1, column=1)
textEntry = StringVar()
file_path = Entry(text="", width=30, textvariable=textEntry).grid(row=2, column=1)

btn_open = Button(window, text='Open', command=lambda: get_file()).grid(row=2, column=2)
btn_execute = Button(window, text='Sort DrawIo Library', command=lambda: execute()).grid(row=4, column=1)

window.mainloop()
