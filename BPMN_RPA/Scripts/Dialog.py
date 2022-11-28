import json
import tkinter
import tkinter.simpledialog
import tkinter.filedialog
import tkinter.colorchooser
import sys
from pathlib import Path

# The BPMN-RPA Dialog module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# The BPMN-RPA Dialog module is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

def inputbox(title: str, message: str, default: str = "", topmost=True) -> str:
    """
    Show a inputbox on the screen with a specific Title, Message and default value.
    :param title: The title of the inputbox.
    :param message: The message of the inputbox.
    :param default: The default value of the inputbox.
    :param topmost: If the messagebox should be placed on top of all other windows.
    :return: The input value.
    """
    root = tkinter.Tk()
    if topmost:
        # set window topmost
        root.wm_attributes("-topmost", 1)
    try:
        root.iconbitmap(default="app.ico")
    except Exception as e:
        pass
    root.withdraw()
    title = str(title)
    message = str(message) + "                                               "
    default = str(default)
    # make the textbox extendable
    retn = tkinter.simpledialog.askstring(title, message, initialvalue=default)
    root.destroy()
    return retn


def user_password_input(title: str, message: str, default: str = "", topmost=True) -> str:
    """
    Show a password inputbox on the screen with a specific Title, Message and default value.
    :param title: The title of the inputbox.
    :param message: The message of the inputbox.
    :param default: The default value of the inputbox.
    :param topmost: If the messagebox should be placed on top of all other windows.
    :return: The input value.
    """
    root = tkinter.Tk()
    if topmost:
        # set window topmost
        root.wm_attributes("-topmost", 1)
    try:
        root.iconbitmap(default="app.ico")
    except Exception as e:
        pass
    root.withdraw()
    title = str(title)
    message = str(message) + "                                               "
    default = str(default)
    retn = tkinter.simpledialog.askstring(title, message, initialvalue=default, show="*")
    root.destroy()
    return retn


def user_select_value(title: str, message: str, values: str, width="300", height="300", x="", y="", topmost=True) -> str:
    """
    Show a Listbox on the screen with a specific Title, Message and default value.
    :param title: The title of the Listbox.
    :param message: The message of the Listbox.
    :param values: The values of the Listbox. This is a comma separated string with values.
    :param width: The width of the Listbox.
    :param height: The height of the Listbox.
    :param x: Optional. The x position of the Listbox. If not set, the Listbox will be centered, regardless of the y position.
    :param y: Optional. The y position of the Listbox. If not set, the Listbox will be centered, regardless of the x position.
    :param topmost: Optional. If True, the Listbox will be on top of all other windows.
    :return: The selected value.
    """
    # Convert json string to list
    root = tkinter.Tk()
    # set standard width x height
    root.geometry(f"{width}x{height}")
    # set window title
    root.title(title)
    if topmost:
        # set window topmost
        root.wm_attributes("-topmost", 1)
    # set window icon
    try:
        root.iconbitmap(default="app.ico")
    except Exception as e:
        pass
    # check x value
    if x == "":
        # place window on center of screen
        root.eval('tk::PlaceWindow . center')
    else:
        # check y value and set y position
        if y != "":
            # set window on xy position
            root.geometry(f"+{x}+{y}")
        else:
            # place window on center of screen
            root.eval('tk::PlaceWindow . center')
    listbox = tkinter.Listbox(root)
    # add scrollbar to listbox
    scrollbar = tkinter.Scrollbar(root, orient="vertical")
    scrollbar.config(command=listbox.yview)
    scrollbar.pack(side="right", fill="y")
    listbox.config(yscrollcommand=scrollbar.set)
    # make listbox just as wide as the window with small margin
    listbox.pack(fill=tkinter.BOTH, expand=1, padx=5, pady=5)
    lst = str(values).split(",")
    for item in lst:
        listbox.insert("end", item)
    listbox.select_set(0)
    listbox.focus_set()

    # Set default listbox value is default is not empty
    def exit_gui():
        global result
        try:
            result = listbox.curselection()
            root.destroy()
        except Exception as e:
            pass

    def cancel():
        global result
        result = ""
        root.destroy()

    # add OK and Cancel buttons
    buttonbox = tkinter.Frame(root)
    tkinter.Button(buttonbox, text="Cancel", width=10, command=cancel).pack(side="left")
    tkinter.Button(buttonbox, text="OK", width=10, command=exit_gui).pack(side="left")
    # put small margin around buttons
    buttonbox.pack(padx=5, pady=5)
    # run the GUI
    root.mainloop()
    # return the selected value
    try:
        return lst[result[0]]
    except Exception as e:
        return ""


def user_browse_for_file_dialog(title: str, filetypes: str = "", initialdir: str = "", topmost=True) -> str:
    """
    Show a file dialog on the screen with a specific Title, Message and default value.
    :param title: The title of the file dialog.
    :param filetypes: The filetypes of the file dialog. This is a comma separated string with values.
    :param initialdir: The initial directory of the file dialog.
    :param topmost: If the messagebox should be placed on top of all other windows.
    :return: The selected file.
    """
    root = tkinter.Tk()
    if topmost:
        # set window topmost
        root.wm_attributes("-topmost", 1)
    try:
        root.iconbitmap(default="app.ico")
    except Exception as e:
        pass
    root.withdraw()
    title = str(title)
    filetypes = str(filetypes)
    initialdir = str(initialdir)
    retn = tkinter.filedialog.askopenfilename(title=title, filetypes=filetypes, initialdir=initialdir)
    root.destroy()
    return retn


def user_browse_for_folder_dialog(title: str, initialdir: str = "", topmost=True) -> str:
    """
    Show a folder dialog on the screen with a specific Title, Message and default value.
    :param title: The title of the folder dialog.
    :param initialdir: The initial directory of the folder dialog.
    :param topmost: If the messagebox should be placed on top of all other windows.
    :return: The selected folder.
    """
    root = tkinter.Tk()
    if topmost:
        # set window topmost
        root.wm_attributes("-topmost", 1)
    try:
        root.iconbitmap(default="app.ico")
    except Exception as e:
        pass
    root.withdraw()
    title = str(title)
    initialdir = str(initialdir)
    retn = tkinter.filedialog.askdirectory(title=title, initialdir=initialdir)
    root.destroy()
    return retn


def user_select_color_dialog(title: str, initialcolor: str = "", topmost=True) -> str:
    """
    Show a color dialog on the screen with a specific Title, Message and default value.
    :param title: The title of the color dialog.
    :param initialcolor: The initial color of the color dialog.
    :param topmost: If the messagebox should be placed on top of all other windows.
    :return: The selected color in hex format.
    """
    root = tkinter.Tk()
    if topmost:
        # set window topmost
        root.wm_attributes("-topmost", 1)
    root.withdraw()
    title = str(title)
    initialcolor = str(initialcolor)
    try:
        root.iconbitmap(default="app.ico")
    except Exception as e:
        pass
    retn = tkinter.colorchooser.askcolor(title=title, initialcolor=initialcolor)
    root.destroy()
    return retn[1]


def user_input_from_json_with_labels_and_textboxes(title: str, json_string: str, width: int = 300, x: str = "",
                                                   y: str = "", topmost=True) -> str:
    """
    Show a JSON input dialog on the screen with a specific Title, Message and default value.
    :param title: The title of the JSON input dialog.
    :param json_string: The JSON string to be used for the input dialog.
    :param width: The width of the JSON input dialog.
    :param x: Optional. The x position of the JSON input dialog. If not set, the JSON input dialog will be centered, regardless of the y position.
    :param y: Optional. The y position of the JSON input dialog. If not set, the JSON input dialog will be centered, regardless of the x position.
    :param topmost: Optional. If True, the JSON input dialog will be on top of all other windows.
    :return: The selected value.
    """
    # Convert json string to list
    root = tkinter.Tk()
    # set standard width x height
    root.geometry(f"{width}x300")
    # set window title
    root.title(title)
    if topmost:
        # set window topmost
        root.wm_attributes("-topmost", 1)
    # set window icon
    try:
        root.iconbitmap(default="app.ico")
    except Exception as e:
        pass
    # check x value
    if x == "":
        # place window on center of screen
        root.eval('tk::PlaceWindow . center')
    else:
        # check y value and set y position
        if y != "":
            # set window on xy position
            root.geometry(f"+{x}+{y}")
        else:
            # place window on center of screen
            root.eval('tk::PlaceWindow . center')
    # convert jsonstring to dict
    json_dict = json.loads(json_string)
    # colomnconfigure a grid that holds just as many rows as there are items in the json dict and make sure the grid has two columns
    root.grid_columnconfigure(0, weight=0)
    root.grid_columnconfigure(1, weight=1)
    # for each keyvalue pair in json, add a label and a textbox
    row = 0
    height_required_list = []
    for key, value in json_dict.items():
        # add label left to the textbox
        lbl = tkinter.Label(root, text=key)
        lbl.grid(row=row, column=0, sticky="w", padx=5, pady=5)
        # add textbox that fills the rest of the frame
        entry = tkinter.Entry(root, textvariable=value)
        entry.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
        height_required_list.append(int(entry.winfo_reqheight() + 12))
        row += 1
    # add OK and Cancel buttons
    buttonbox = tkinter.Frame(root)

    def exit_gui():
        global result
        try:
            result = json.dumps(json_dict)
            # loop through all textboxes of the window and build a json string
            result = "{"
            for child in root.winfo_children():
                if isinstance(child, tkinter.Entry):
                    result += f'"{child["textvariable"]}": "{child.get()}",'
            result = result[:-1] + "}"
            root.destroy()
        except Exception as e:
            result = ""
            root.destroy()

    def cancel_gui():
        global result
        try:
            result = ""
            root.destroy()
        except Exception as e:
            result = ""
            root.destroy()

    buttonbox.grid(row=row, column=1, columnspan=2, sticky="e", padx=5, pady=5)
    ok_button = tkinter.Button(buttonbox, text="OK", command=exit_gui)
    ok_button.pack(side="left", padx=5, pady=5)
    height_required_list.append(45)
    cancel_button = tkinter.Button(buttonbox, text="Cancel", command=cancel_gui)
    cancel_button.pack(side="left", padx=5, pady=5)
    minimum_height = 0
    minimum_width = 0
    for height in height_required_list:
        minimum_height += height
    # Make window correct size make window require the correct sizing
    root.geometry("{}x{}".format(width, minimum_height))
    root.minsize(0, minimum_height)
    root.maxsize(0, minimum_height)
    # start GUI
    root.mainloop()
    try:
        # return dict
        return json.loads(result)
    except Exception as e:
        return ""
