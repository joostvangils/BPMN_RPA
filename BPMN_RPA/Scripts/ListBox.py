from tkinter import Tk, Listbox, LEFT, BOTH, RIGHT, END, Scrollbar, PhotoImage, Label, Button, ACTIVE


def let_user_select_from_listbox(title: str, subtitle: str = ""):
    """
    Let the user create a listbox, choose an item from it and return the selected value.
    :param title: The title of the window.
    :param subtitle: Optional. The explaining text above the listbox.
    :return: The selected item in the listbox.
    """
    # Creating the root window
    root = Tk()
    root.title(title)
    # root.iconphoto(False, PhotoImage(file='icon.png'))
    # Devide window with grid
    root.columnconfigure([0, 1, 2, 3], minsize=40)
    root.rowconfigure([0, 1, 2, 3, 4, 5], minsize=40)

    lbl = Label(root, text = subtitle)
    lbl.grid(row=0, column=1, sticky="w")

    listbox = Listbox(root, width=40)
    listbox.grid(row=1, column=1)

    scrollbar = Scrollbar(root)
    scrollbar.grid(row=1, column=2, sticky="ns")

    retval = None
    def __returnvalue__():
        global retval
        retval = str((listbox.get(ACTIVE)))


    btnCancel = Button(root, text='Cancel', width=10, command=lambda: root.quit()).grid(row=3, column=1)
    btnSelect = Button(root, text='OK', width = 10, command=lambda: __returnvalue__()).grid(row=3, column=1, sticky="e")

    # listbox.pack(side=LEFT, fill=BOTH)

    for values in range(100):
        listbox.insert(END, values)

    listbox.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=listbox.yview)
    root.mainloop()
    return retval



print(let_user_select_from_listbox("test","dit is een test"))