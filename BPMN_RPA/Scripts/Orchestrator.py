from tkinter import *
from tkinter import filedialog, messagebox
from tkinter.filedialog import askopenfile
from tkinter.font import Font
from tkinter.ttk import *
from BPMN_RPA.WorkflowEngine import WorkflowEngine, SQL


window = Tk()
window.title("BPMN-RPA Orchestrator")
# window.iconphoto(False, PhotoImage(file='icon.png'))

# Devide window with grid
# window.columnconfigure([0, 1, 2, 3], minsize=10)
# window.rowconfigure([0, 1, 2, 3, 4, 5], minsize=10)

# tabControl = Notebook(window)
# tab1 = Frame(tabControl)
# tabControl.add(tab1, text='Flows')
# tabControl.grid(row=1, column=1)

def donothing():
   x = 0



def MultiColumnListbox(parent):
    tree = Treeview(parent)
    s = "History of runned flows:"
    msg = Label(wraplength="4i", justify="left", anchor="n", padding=(10, 2, 10, 6), text=s)
    msg.pack(fill='x')
    run_container = Frame()
    run_container.pack(fill='both', expand=True)
    # create a treeview with dual scrollbars
    tree = Treeview(columns=runned_header, show="headings")
    vsb = Scrollbar(orient="vertical", command=tree.yview)
    hsb = Scrollbar(orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    tree.grid(column=0, row=0, sticky='nsew', in_=run_container)
    vsb.grid(column=1, row=0, sticky='ns', in_=run_container)
    hsb.grid(column=0, row=1, sticky='ew', in_=run_container)
    run_container.grid_columnconfigure(0, weight=1)
    run_container.grid_rowconfigure(0, weight=1)
    return run_container

def _build_tree(self):
    for col in runned_header:
        self.tree.heading(col, text=col.title(), command=lambda c=col: sortby(self.tree, c, 0))
        # adjust the column's width to the header string
        self.tree.column(col, width=Font().measure(col.title()))

    for item in runned_list:
        flow = self.tree.insert('', 'end', values=item)
        # for chld in sql.get_runned_flows(item[0]):
        #     runs = self.tree.insert(flow, 'end', values=chld)
        # adjust column's width if necessary to fit each value
        idx = 0
        for itm in enumerate(item):
             col_w = Font().measure(itm)
             self.tree.column(runned_header[idx], width=col_w)
             idx += 1

def sortby(tree, col, descending):
    """sort tree contents when a column header is clicked on"""
    # grab values to sort
    data = [(tree.set(child, col), child) for child in tree.get_children('')]
    # if the data to be sorted is numeric change to float
    # data =  change_numeric(data)
    # now sort the data in place
    data.sort(reverse=descending)
    for ix, item in enumerate(data):
        tree.move(item[1], '', ix)
    # switch the heading so it will sort in the opposite direction
    tree.heading(col, command=lambda col=col: sortby(tree, col, int(not descending)))


engine = WorkflowEngine()
pythonpath = engine.get_python_path()
sql = SQL(engine.get_db_path())

# Create Panedwindow
panedwindow = Panedwindow(window, orient=VERTICAL)
panedwindow.pack(fill=BOTH, expand=True)

# region Flows listbox
flow_container = Frame()
lblFlows = Label(flow_container, text="Known flows:", justify=LEFT, anchor="w")
flows = Listbox(flow_container,width=120)
idx = 0
for rw in sorted(sql.get_flows()):
    flows.insert(idx, rw[1])
flow_container.pack(fill=BOTH, expand=True)
panedwindow.add(flow_container, weight=10)

# flows.pack(fill="both", expand=True)
# endregion

runned_header = ['id', 'flow id', 'name', 'result', 'started', 'ended']

runned_list = sql.get_runned_flows()


menubar = Menu(window)
filemenu = Menu(menubar, tearoff=0)
# filemenu.add_command(label="New", command=donothing)
# filemenu.add_command(label="Open", command=donothing)
# filemenu.add_command(label="Save", command=donothing)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=window.quit)
menubar.add_cascade(label="File", menu=filemenu)

helpmenu = Menu(menubar, tearoff=0)
helpmenu.add_command(label="Help Index", command=donothing)
helpmenu.add_command(label="About...", command=donothing)
menubar.add_cascade(label="Help", menu=helpmenu)


runned = MultiColumnListbox(window)
panedwindow.add(runned, weight=3)
window.config(menu=menubar)
window.mainloop()