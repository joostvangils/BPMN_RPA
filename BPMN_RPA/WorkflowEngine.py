import base64
import copy
import importlib
import inspect
import multiprocessing
import os
import re
import site
import sqlite3
import urllib
import winreg
import socket
import xml.etree.ElementTree as ET
import zlib
from datetime import datetime, timedelta
from inspect import signature
from shutil import copyfile
from typing import List, Any

import xmltodict


class WorkflowEngine():

    def __init__(self, input_parameter: Any = None, pythonpath: str = "", installation_directory: str = ""):
        """
        Class for automating DrawIO diagrams
        :param input_parameter: An object holding arguments to be passed as input to the WorkflowEngine.  in a flow, use get_input_parameter to retreive the value.
        :param pythonpath: The full path to the python.exe file
        :param installation_directory: The folder where your BPMN_RPA files are installed. This folder will be used for the orchestrator database.
        """
        if len(pythonpath) != 0:
            self.set_PythonPath(pythonpath)
        else:
            pythonpath = self.get_pythonPath()
        if len(installation_directory) != 0:
            self.set_dbPath(installation_directory)
            dbFolder = installation_directory
        else:
            dbFolder = self.get_dbPath()
        if dbFolder is None:
            installdir = input(
                "\nYour installation directory is unknown. Please enter the path of your installation directory: ")
            if not str(installdir).endswith("\\"):
                installdir += "\\"
            if not os.path.exists(installdir):
                os.mkdir(installdir)
            if len(installdir) == 0:
                return
            else:
                self.set_dbPath(installdir)
                dbFolder = self.get_dbPath()
        if pythonpath is None:
            pythonpath = input(
                "\nThe path to your Python.exe file is unknown. Please enter the path to your Python.exe file: ")
            if not os.path.exists(pythonpath):
                self.set_PythonPath(pythonpath)
            if len(pythonpath) == 0:
                return
            else:
                self.set_PythonPath(pythonpath)
        if not os.path.exists(f'{dbFolder}\\Registered Flows'):
            os.mkdir(f'{dbFolder}\\Registered Flows')
        self.input_parameter = input_parameter
        self.pythonPath = pythonpath
        self.db = SQL(dbFolder)
        self.db.orchestrator()  # Run the orchestrator database
        self.id = -1  # Holds the ID for our flow
        self.error = False  # Indicator if the flow has any errors in its execution
        self.step_name = None
        self.flowname = None
        self.flowpath = None
        self.loopvariables = []
        self.previous_step = None
        self.step_nr = None
        self.variables = {}  # Dictionary to hold WorkflowEngine variables

    def get_input_parameter(self):
        """
        Returns the input parameter that was given when creating an instance of the WorkflowEngine
        :return: The input_parameter that was given when creating an instance of the WorkflowEngine
        """
        self.print_log(f"Got input parameter {str(self.input_parameter)}")
        return self.input_parameter

    def open(self, filepath: str, as_xml: bool = False) -> Any:
        """
        Open a DrawIO document
        :param filepath: The full path (including extension) of the diagram file
        :param as_xml: Optional. Returns the file content as XML.
        :returns: A DrawIO dictionary object
        """
        # Open an existing document.
        if filepath is not None:
            self.flowpath = filepath
        xml_file = open(filepath, "r")
        self.flowname = filepath.split("\\")[-1].lower().replace(".xml", "")
        xml_root = ET.fromstring(xml_file.read())
        raw_text = xml_root[0].text
        base64_decode = base64.b64decode(raw_text)
        inflated_xml = zlib.decompress(base64_decode, -zlib.MAX_WBITS).decode("utf-8")
        url_decode = urllib.parse.unquote(inflated_xml)
        if as_xml:
            return  url_decode
        retn = xmltodict.parse(url_decode)
        return retn

    def set_dbPath(self, value: str):
        """
        Write the orchestrator database path to the registry.
        :param value: The path of the orchestrator database that has to be written to the registry
        """
        try:
            REG_PATH = r"SOFTWARE\BPMN_RPA"
            winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_PATH)
            registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0,
                                          winreg.KEY_WRITE)
            winreg.SetValueEx(registry_key, "dbPath", 0, winreg.REG_SZ, value)
            winreg.CloseKey(registry_key)
            return True
        except WindowsError:
            return False

    def get_dbPath(self):
        """
        Get the path to the orchestrator database
        :return: The path to the orchestrator database
        """
        try:
            REG_PATH = r"SOFTWARE\BPMN_RPA"
            registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_READ)
            value, regtype = winreg.QueryValueEx(registry_key, 'dbPath')
            winreg.CloseKey(registry_key)
            return value
        except WindowsError:
            return None

    def get_pythonPath(self):
        """
        Get the path to the Python.exe file
        :return: The path to the Python.exe file
        """
        try:
            REG_PATH = r"SOFTWARE\BPMN_RPA"
            registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_READ)
            value, regtype = winreg.QueryValueEx(registry_key, 'PythonPath')
            winreg.CloseKey(registry_key)
            return value
        except WindowsError:
            return None

    def set_PythonPath(self, value: str):
        """
        Write the oPython path to the registry.
        :param value: The path of the Python.exe file that has to be written to the registry
        """
        try:
            REG_PATH = r"SOFTWARE\BPMN_RPA"
            winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_PATH)
            registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0,
                                          winreg.KEY_WRITE)
            winreg.SetValueEx(registry_key, "PythonPath", 0, winreg.REG_SZ, value)
            winreg.CloseKey(registry_key)
            return True
        except WindowsError:
            return False

    def get_flow(self, ordered_dict) -> Any:
        """
        Retreiving the elements of the flow in the Document.
        :param ordered_dict: The document object containing the flow elements.
        :returns: A List of flow elements
        """
        connectors = []
        shapes = []
        connectorvalues = {}
        objects = ordered_dict['mxGraphModel']['root']['object']
        for shape in ordered_dict['mxGraphModel']['root']['mxCell']:
            style = shape.get("@style")
            if style is not None:
                if str(style).__contains__("edgeLabel"):
                    # Save for later
                    connectorvalues.update({shape.get("@parent"): shape.get("@value")})
                step = self.get_step_from_shape(shape)
                if step.type == "connector":
                    connectors.append(step)
                else:
                    shapes.append(step)
        if not isinstance(objects, list):
            # there is only one shape
            step = self.get_step_from_shape(objects)
            self.store_system_variables(step)
            shapes.append(step)
        else:
            for shape in objects:
                step = self.get_step_from_shape(shape)
                self.store_system_variables(step)
                shapes.append(step)
        # Find start shape
        for shape in shapes:
            incoming_connector = None
            outgoing_connector = None
            for conn in connectors:
                if hasattr(conn, "target"):
                    if conn.target == shape.id:
                        incoming_connector = conn
                        break
                    if hasattr(conn, "source"):
                        if conn.source == shape.id:
                            outgoing_connector = conn
                            break
            if incoming_connector is None and outgoing_connector is not None:
                shape.IsStart = True
        for conn in connectors:
            val = connectorvalues.get(conn.id)
            if val is not None:
                conn.value = val
        retn = shapes + connectors
        return retn

    def get_step_from_shape(self, shape):
        """
        Build a Step-object from the Shape-object
        :param shape: The Shape-object
        :returns: A Step-object
        """
        retn = self.dynamic_object()
        row = 0
        retn.id = shape.get("@id")
        for key, value in shape.items():
            attr = str(key).lower().replace("@", "")
            if attr == "class":
                attr = "classname"  # 'çlass' is a reserved keyword, so use 'çlassname'
            setattr(retn, attr, value)
        if shape.get("@source") is not None or shape.get("@target") is not None:
            retn.type = "connector"
        if shape.get("@label") is not None:
            if not hasattr(retn, "name"):
                retn.name = retn.label
        if shape.get("@source") is None and shape.get("@target") is None:
            if hasattr(retn, "type"):
                if not retn.type.lower().__contains__("gateway"):
                    retn.type = "shape"
                else:
                    retn.type = retn.type.lower()
            else:
                retn.type = "shape"
            retn.IsStart = False
        return retn

    def get_variables_from_text(self, text: str) -> List[str]:
        """
        Get variable names (like '%variable%') from text.
        :param text: The text to get the variables from
        :return: A list with variable names.
        """
        if not isinstance(text, str):
            return None
        retn = []
        start = -1
        end = -1
        t = 0
        for c in text:
            if c == "%":
                if start > -1:
                    end = t
                if start == -1:
                    start = t
                if start > -1 and end > -1:
                    retn.append(text[start: end + 1])
                    start = -1
                    end = -1
            t += 1
        if len(retn) == 0:
            retn = None
        return retn

    def get_parameters_from_shapevalues(self, step: Any, signature: Any) -> str:
        """
        If input values are provided in the Shapevalues, then create a mapping
        :param step: The step to use the Shapevalues of to create the mapping
        :param signature: The imput parametes of the function that needs to be called
        :return: A mapping string
        """
        mapping = {}
        returnNone = True
        tmp = None
        if signature is None:
            if hasattr(self.previous_step, "output_variable"):
                var = self.variables.get(self.previous_step.output_variable)
                if var is not None:
                    return var
                else:
                    return None
            return None
        for key, value in signature.parameters.items():
            attr = None
            if str(key).lower() != "self":
                try:
                    val = str(getattr(step, str(key).lower()))
                except Exception as e:
                    if str(value).__contains__("="):
                        val = value.default
                    else:
                        val = None
                if val is not None:
                    if len(str(val)) == 0:
                        if input is not None:
                            val = ""
                        else:
                            if str(value).__contains__("="):
                                val = value.default
                            else:
                                val = "''"
                    else:
                        returnNone = False
                if isinstance(val, str):
                    if val == "True":
                        val = True
                    elif val == "False":
                        val = False
                    else:
                        if val.replace(".", "").isnumeric():
                            if val.__contains__("."):
                                val = float(val)
                            else:
                                val = int(val)
                if not str(key).__contains__("variable"):
                    textvars = self.get_variables_from_text(val)
                    if textvars is not None:
                        # replace textvariables with values
                        for tv in textvars:
                            lst = tv.replace("%", "").split("[")
                            clean_textvar = "%" + lst[0].split(".")[0] + "%"
                            replace_value = self.variables.get(clean_textvar)
                            if replace_value is not None:
                                # variable exists
                                # Check if this is a loop-variable
                                loopvars = [x for x in self.loopvariables if x.name == clean_textvar]
                                if len(loopvars) > 0:
                                    if tv.lower().__contains__(".counter"):
                                        val = loopvars[0].counter
                                    elif tv.lower().__contains__(".object"):
                                        val = loopvars[0]
                                    else:
                                        if isinstance(replace_value, list) and not str(replace_value).__contains__(
                                                "Message(mime_content="):
                                            if not tv.__contains__("."):
                                                if len(replace_value) == 1 and not isinstance(replace_value[0], list):
                                                    val = val.replace(tv, replace_value[0])
                                                else:
                                                    if len(replace_value) == 0:
                                                        self.print_log(status="Ending", result=f"No items to loop...")
                                                        self.exitcode_ok()
                                                    else:
                                                        if loopvars[0].counter < len(replace_value):
                                                            if isinstance(replace_value[loopvars[0].counter], str):
                                                                val = val.replace(tv, replace_value[loopvars[0].counter])
                                                            else:
                                                                val = list(replace_value[loopvars[0].counter])
                                                                if len(lst)>1:
                                                                    for l in lst[1:]:
                                                                        val = val[int(l.replace("]",""))]
                                                        else:
                                                            if isinstance(replace_value[0], str):
                                                                val = val.replace(tv, replace_value[0])
                                                            else:
                                                                val = replace_value[0]
                                                                if len(lst)>1:
                                                                    for l in lst[1:]:
                                                                        val = val[int(l.replace("]",""))]

                                                        if  str(getattr(step, str(key).lower())) != tv:
                                                            if loopvars[0].counter < len(replace_value):
                                                                replace_value = replace_value[loopvars[0].counter]
                                                            else:
                                                                replace_value = replace_value[0]
                                                            if isinstance(replace_value, list):
                                                                repl_list = tv.split("[")
                                                                if tmp is None:
                                                                    tmp = str(getattr(step, str(key).lower()))
                                                                for repl in repl_list:
                                                                    if repl.__contains__("]"):
                                                                        nr = str(repl).replace("]", "").replace("%", "")
                                                                        if nr.isnumeric():
                                                                            tmp = tmp.replace(tv, str(replace_value[int(nr)]))
                                                                    val = tmp

                                            else:
                                                if loopvars[0].counter < len(replace_value):
                                                    replace_value = self.get_attribute_value(lst[0], replace_value[
                                                        loopvars[0].counter])
                                                else:
                                                    replace_value = self.get_attribute_value(lst[0], replace_value[0])
                                                if isinstance(replace_value, str):
                                                    val = val.replace(tv, str(replace_value))
                                                else:
                                                    val = replace_value
                                        else:
                                            if str(replace_value).__contains__("Message(mime_content="):
                                                if isinstance(replace_value, list):
                                                    if tv.__contains__("."):
                                                        attr = str(lst[0].split(".")[1]).replace(".", "")
                                                    if loopvars[0].counter <= len(replace_value) - 1:
                                                        val = replace_value[loopvars[0].counter]
                                                        if len(attr) > 0:
                                                            val = getattr(val, attr)
                                                    else:
                                                        val = replace_value[0]
                                                        if len(attr) > 0:
                                                            val = getattr(val, attr)
                                                else:
                                                    val = replace_value
                                            else:
                                                replace_value = self.get_attribute_value(lst[0], replace_value)
                                                if val is not None and replace_value is not None:
                                                    val = val.replace(tv, replace_value)
                                                else:
                                                    val = replace_value
                                else:
                                    if tv.__contains__("[") and tv.__contains__("]"):
                                        if isinstance(replace_value, list):
                                            if tmp is None:
                                                tmp = str(getattr(step, str(key).lower()))
                                            repl_list = tv.split("[")
                                            for repl in repl_list:
                                                if repl.__contains__("]"):
                                                    nr = str(repl).replace("]", "").replace("%", "")
                                                    if nr.isnumeric():
                                                        if int(nr) < len(replace_value):
                                                            if isinstance(replace_value[int(nr)], str):
                                                                tmp = tmp.replace(tv, replace_value[int(nr)])
                                                            else:
                                                                if tmp is None:
                                                                    tmp = replace_value[int(nr)]
                                                                else:
                                                                    if len(repl_list) > 1:
                                                                        tmp2 = replace_value[int(nr)]
                                                                        for l in repl_list[2:]:
                                                                            tmp2 = tmp2[int(l.replace("]","").replace("%", ""))]
                                                                        if isinstance(tmp, str) and tmp!=tv:
                                                                            tmp = tmp.replace(tv, tmp2)
                                                                        else:
                                                                            tmp = tmp2
                                            val = tmp
                                    elif tv.__contains__("."):
                                        replace_value = self.get_attribute_value(lst[0], replace_value)
                                        if isinstance(replace_value, str):
                                            val = val.replace(tv, str(replace_value))
                                        else:
                                            if val != tv:
                                                val = val.replace(tv, str(replace_value))
                                            else:
                                                val = replace_value
                                    else:
                                        if isinstance(replace_value, list):
                                            val = replace_value
                                        elif isinstance(replace_value, str):
                                            val = val.replace(tv, str(replace_value))
                                        else:
                                            if val != tv:
                                                val = val.replace(tv, str(replace_value))
                                            else:
                                                val = replace_value
                mapping[str(key)] = val
        if returnNone:
            return None
        else:
            return mapping

    def get_attribute_value(self, lst: list, replace_value: Any) -> Any:
        """
        Get an attribute value from a replace value (object)
        :param lst: The attribute list
        :param replace_value: The replace value object
        :return: The attribute value or object
        """
        val = None
        lst_ = lst.split(".")[1:]
        if len(lst_)==0:
            lst_ = lst
        if isinstance(lst_, list):
            for attr in lst_:
                if val is not None:
                    replace_value = val
                if isinstance(replace_value, dict):
                    val = replace_value.get(attr)
                if isinstance(replace_value, object) and not isinstance(replace_value, dict):
                    if hasattr(replace_value, attr):
                        val = getattr(replace_value, attr)
                    else:
                        val = replace_value
        else:
            val = replace_value
        return val

    def step_has_direct_variables(self, step: Any) -> bool:
        """
        Check if a step uses any variables as input for any of the Shapevalue fields
        :param step: The step to check
        :return: True or Flase
       """
        attrs = vars(step)
        col = [key for key, val in attrs.items() if
               str(val).startswith("%") and str(val).endswith("%") and str(key) != "output_variable"]
        if len(col) > 0:
            return True
        else:
            return False

    def run_flow(self, steps):
        """
        Execute a Workflow.
        :params steps: The steps that must be executed in the flow
        """
        dbPath = self.get_dbPath()
        if dbPath == "\\":
            raise Exception('Your installation directory is unknown.')
            self.error = True
            return
        # Register the flow if not already registered
        if not os.path.exists(f'{self.db}\\Registered Flows\\{self.flowname}.xml') and not os.path.exists(
                self.flowpath):
            # Move the file to the registered directory if not exists
            copyfile(self.flowpath, f'{dbPath}\\Registered Flows\\{self.flowname}.xml')
        self.flowpath = f'{dbPath}\\Registered Flows\\{self.flowname}.xml'
        sql = f"SELECT id FROM Registered WHERE name ='{self.flowname}' AND location='{self.flowpath}'"
        registered_id = self.db.run_sql(sql=sql, tablename="Registered")
        if registered_id is None:
            sql = f"INSERT INTO Registered (name, location) VALUES ('{self.flowname}','{self.flowpath}');"
            registered_id = self.db.run_sql(sql=sql, tablename="Registered")
        self.previous_step = None
        output_previous_step = None
        shape_steps = [x for x in steps if x.type == "shape"]
        step = [x for x in shape_steps if x.IsStart == True][0]
        step_time = datetime.now().strftime("%H:%M:%S")

        # Log the start in the orchestrator database
        sql = f"INSERT INTO Workflows (name, registered_id) VALUES ('{self.flowname}', {registered_id});"
        self.id = self.db.run_sql(sql=sql, tablename="Workflows")
        print("\n")
        self.print_log(status="Running", result=f"{datetime.today().strftime('%d-%m-%Y')} Starting flow '{self.flowname}'...")
        self.step_nr = 0
        while True:
            try:
                # to fetch module
                class_object = None
                module_object = None
                method_to_call = None
                sig = None
                input = None
                IsInLoop = False
                if hasattr(step, "name"):
                    step_time = datetime.now().strftime("%H:%M:%S")
                    self.step_nr += 1
                    self.step_name = step.name
                    if len(step.name) == 0:
                        if hasattr(step, "type"):
                            self.print_log(status="Running",
                                           result=f"Passing an {step.type} with value {output_previous_step}...")
                    else:
                        if hasattr(step, "function"):
                            if step.function != "print_log":
                                self.print_log(status="Running", result=f"Executing step '{step.name}'...")
                        else:
                            self.print_log(status="Running", result=f"Executing step '{step.name}'...")
                if step is not None:
                    loopkvp = [kvp for kvp in self.loopvariables if kvp.id == step.id]
                    if loopkvp:
                        if loopkvp[0].counter > 0 and loopkvp[0].counter > loopkvp[0].start:
                            IsInLoop = True
                if hasattr(step, "module"):
                    # region get function call
                    method_to_call = None
                    if self.step_has_direct_variables(step):
                        # Get variable from stack
                        if hasattr(step, "output_variable"):
                            var = self.variables.get(step.output_variable)
                            if inspect.isclass(var):
                                method_to_call = getattr(self.variables.get(step.output_variable), step.function)
                    if method_to_call is None:
                        input = None
                        if hasattr(step, "module"):
                            if not str(step.module).__contains__("\\") and str(step.module).lower().__contains__(".py"):
                                step.module = f"{site.getsitepackages()[1]}\\\BPMN_RPA\\Scripts\\{step.module}"
                            if not str(step.module).__contains__(":") and str(step.module).__contains__("\\") and str(
                                    step.module).__contains__(".py"):
                                step.module = f"{site.getsitepackages()[1]}\\{step.module}"
                            if str(step.module).lower().__contains__(".py"):
                                spec = importlib.util.spec_from_file_location(step.module, step.module)
                                module_object = importlib.util.module_from_spec(spec)
                                if module_object is None:
                                    step_time = datetime.now().strftime("%H:%M:%S")
                                    raise Exception(
                                        f"{step_time}: The module '{step.module}' could not be loaded. Check the path...")
                                spec.loader.exec_module(module_object)
                            else:
                                if len(step.module) == 0:
                                    module_object = self
                                else:
                                    module_object = importlib.import_module(step.module)
                        if hasattr(step, "classname"):
                            if hasattr(module_object, str(step.classname).lower()) or hasattr(module_object,
                                                                                              str(step.classname)):
                                if hasattr(module_object, str(step.classname).lower()):
                                    class_object = getattr(module_object, str(step.classname).lower())
                                else:
                                    class_object = getattr(module_object, str(step.classname))
                                if hasattr(step, "function"):
                                    if len(step.function) > 0:
                                        method_to_call = getattr(class_object, step.function)
                            else:
                                if str(step.classname).startswith("%") and str(step.classname).endswith("%"):
                                    class_object = self.variables.get(step.classname)
                                    if len(step.function) > 0:
                                        method_to_call = getattr(class_object, step.function)

                                else:
                                    if hasattr(step, "function"):
                                        method_to_call = getattr(module_object, step.function)

                        else:
                            method_to_call = getattr(module_object, step.function)
                else:
                    if module_object is None and hasattr(step, "classname"):
                        if str(step.classname).startswith("%") and str(step.classname).endswith("%"):
                            class_object = self.variables.get(step.classname)
                            if len(step.function) > 0:
                                method_to_call = getattr(class_object, step.function)
                    else:
                        if module_object is None:
                            module_object = self
                        if hasattr(step, "function"):
                            method_to_call = getattr(module_object, step.function)

                if method_to_call is not None:
                    input = self.get_input_from_signature(step, method_to_call)
                if method_to_call is None and class_object is not None:
                    input = self.get_input_from_signature(step, class_object)

                # execute function call and get returned values
                if input is not None and not IsInLoop:
                    if hasattr(step, "function"):
                        if len(step.function) > 0:
                            if isinstance(class_object, type):
                                class_object = class_object()
                                method_to_call = getattr(class_object, step.function)
                            if isinstance(input, dict):
                                output_previous_step = method_to_call(**input)
                            else:
                                try:
                                    output_previous_step = method_to_call(input)
                                except Exception as e:
                                    pass
                        else:
                            output_previous_step = class_object(**input)
                    else:
                        output_previous_step = class_object(**input)
                else:
                    if IsInLoop:
                        output_previous_step = [x for x in self.loopvariables if id == step.id]
                    else:
                        if hasattr(step, "function"):
                            called = False
                            if len(step.function) > 0:
                                if method_to_call is not None:
                                    if isinstance(class_object, type):
                                        class_object = class_object()
                                        method_to_call = getattr(class_object, step.function)
                                    output_previous_step = method_to_call()
                                    called = True
                                else:
                                    output_previous_step = class_object()
                                    called = True
                            if output_previous_step is None and called == False:
                                output_previous_step = class_object()
                        else:
                            if class_object is not None:
                                if inspect.isclass(class_object):
                                    output_previous_step = class_object()

                # set loop variable
                this_step = self.loopcounter(step, output_previous_step)
                if IsInLoop:
                    output_previous_step = [this_step]

                # Update the result
                if hasattr(step, "classname"):
                    if len(step.classname) == 0:
                        if hasattr(step, "function"):
                            self.print_log(status="Running", result=f"{method_to_call.__name__} executed.")
                    else:
                        if hasattr(step, "function") and class_object is not None:
                            self.print_log(status="Running",
                                           result=f"{class_object.__class__.__name__}.{method_to_call.__name__} executed.")
                        else:
                            if step.name is not None:
                                if len(step.name) > 0:
                                    self.print_log(status="Running", result=f"{step.name} executed.")
                else:
                    if hasattr(step, "function") and method_to_call is not None:
                        if step.function != "print_log":
                            self.print_log(status="Running", result=f"{method_to_call.__name__} executed.")
                    else:
                        if hasattr(step, "name"):
                            if len(step.name) > 0:
                                self.print_log(status="Running", result=f"{step.name} executed.")
            except Exception as e:
                raise Exception(f"Error: {e}")
            if step is None:
                self.end_flow()
                break
            if output_previous_step is not None:
                if str(output_previous_step).startswith("QuerySet"):
                    # If this is Exchangelib output then turn it into list
                    output_previous_step = list(output_previous_step)
                self.save_output_variable(step, this_step, output_previous_step)
            self.previous_step = copy.deepcopy(step)
            if self.error:
                break
            step = self.get_next_step(step, steps, output_previous_step)
        if output_previous_step is not None:
            return output_previous_step

    def print_log(self, result: str, status: str = ""):
        """
        Log progress to the Orchestrator database and print progress on screen
        :param status: Optional. The status of the step
        :param result: The result of the step
        """
        result = str(result).replace("<br>", " ")
        result = str(result[0]).capitalize()+result[1:]
        ststus = str(status)
        if not result.endswith("."):
            result += "."
        step_time = datetime.now().strftime("%H:%M:%S")
        if self.step_nr is not None:
            print(f"{step_time}: Step {self.step_nr} - {result}")
        else:
            print(f"{step_time}: {result}")
            self.step_nr = ""
        result = result.replace("'", "''")
        if len(status) > 0:
            status = f" - {status}"
        if self.step_name is not None:
            step_name = self.step_name.replace("'", "''")
        else:
            step_name = ""
        sql = f"INSERT INTO Steps (Workflow, name, step, status, result) VALUES ('{self.id}', '{self.flowname}', '{step_name}', '{result}', '{self.step_nr}{status}');"
        self.db.run_sql(sql)

    def exitcode_not_ok(self):
        """
        Exit the flow with exitcode not OK -1
        """
        self.end_flow()
        exit(-1)

    def exitcode_ok(self):
        """
        Exit the flow with exitcode OK 0
        """
        self.end_flow()
        exit(0)

    def end_flow(self):
        """
        Log the end of the flow in the orchestrator database
        """
        # Flow has ended. Log the end in the orchestrator database.
        ok = "The flow has ended."
        if self.error:
            ok = "The flow has ended with ERRORS."
        sql = f"INSERT INTO Steps (Workflow, name, step, status, result) VALUES ('{self.id}', '{self.flowname}', 'End', 'Ended', '{ok}');"
        step_time = datetime.now().strftime("%H:%M:%S")
        end_result = f"{step_time}: Flow '{self.flowname}': {ok}"
        print(end_result)
        self.db.run_sql(sql=sql, tablename="Steps")
        # Update the result of the flow
        sql = f"UPDATE Workflows SET result= '{ok}' where id = {self.id};"
        self.db.run_sql(sql=sql, tablename="Workflows")

    def get_input_from_signature(self, step, method_to_call):
        try:
            sig = signature(method_to_call)
        except Exception as e:
            print(f"Error in getting input from signature: {e}")
        if str(sig) != "()":
            input = self.get_parameters_from_shapevalues(step=step, signature=sig)
            return input
        return None

    def reset_loopcounter(self, reset_for_loop_variable):
        """
        Reset the loopcounter for a loop variable
        :param reset_for_loop_variable: The name of the loop variable.
        """
        loopvars = [x for x in self.loopvariables if x.name == reset_for_loop_variable]
        if loopvars is not None and len(loopvars)>0:
            loopvar = loopvars[0]
        else:
            loopvar = None
            self.print_log(f"Loopcounter '{reset_for_loop_variable}' has not yet been initiated. No reset needed.", "Running")
        if loopvar is not None:
            if loopvar.total_listitems == loopvar.counter:
                self.loopvariables.remove(loopvar)
                self.print_log(f"Loopcounter reset loopvariable '{reset_for_loop_variable}'", "Running")

    def loopcounter(self, step: Any, output_previous_step: Any) -> Any:
        """
        Process steps with a loopcounter
        :param step: The current step object
        :param output_previous_step: The output of the previous step as object
        :return: An item from the list that is looped
        """
        loopvar = None
        if hasattr(step, "loopcounter"):
            # Update the total list count
            try:
                loopvar = [x for x in self.loopvariables if x.id == step.id][0]
                if not hasattr(loopvar, "items"):
                    if str(output_previous_step).startswith("QuerySet"):
                        loopvar.items = list(output_previous_step)
                        loopvar.total_listitems = len(list(output_previous_step))
                    else:
                        if isinstance(output_previous_step, list):
                            loopvar.total_listitems = len(output_previous_step)
                        else:
                            loopvar.total_listitems = 1
                        if loopvar.total_listitems > 0 and type(output_previous_step[0]).__name__ == "Row":
                            for t in range(0, loopvar.total_listitems):
                                output_previous_step[t] = list(output_previous_step[t])
                        if isinstance(output_previous_step, str) and not str(output_previous_step).__contains__("%") and not isinstance(output_previous_step, list):
                            loopvar.items = [output_previous_step]
                        else:
                            loopvar.items = output_previous_step
                    if loopvar.total_listitems == 0:
                        self.print_log("There are no more items to loop", "Ending")
                        self.exitcode_ok()
                    loopvar.start = int(step.loopcounter)  # set start of counter
                if int(loopvar.counter) <= loopvar.start:
                    loopvar.counter = int(loopvar.start)
                    loopvar.name = step.output_variable
                # It's a loop! Overwrite the output_previous_step with the right element
                step_time = datetime.now().strftime("%H:%M:%S")
                if len(loopvar.items) > 0:
                    name = loopvar.items[loopvar.counter]
                    if not isinstance(name, str):
                        if hasattr(name, 'name'):
                            name = name.name
                        elif hasattr(name, 'title'):
                            name = name.title
                        elif hasattr(name, 'titel'):
                            name = name.titel
                        elif hasattr(name, 'naam'):
                            name = name.naam
                        elif hasattr(name, 'subject'):
                            name = name.subject
                        elif hasattr(name, 'onderwerp'):
                            name = name.onderwerp
                        else:
                            name = name.__str__()
                    end_result = f"loopitem '{name}' returned."
                    self.print_log(end_result)
                    return loopvar.items[loopvar.counter]
                else:
                    return output_previous_step
            except Exception as e:
                sql = f"INSERT INTO Steps (Workflow, name, step, status, result) VALUES ('{self.id}', '{self.flowname}', '{step.name}', 'Running', '', 'Error: {e}');"
                self.db.run_sql(sql=sql, tablename="Steps")
                self.error = True
                print(f"Error: {e}")
                return output_previous_step
        else:
            return output_previous_step

    def store_system_variables(self, step):
        for value in vars(step):
            if str(getattr(step, value)).__contains__("%__today__%"):
                self.variables.update({'%__today__%': datetime.today().date()})
            if str(getattr(step, value)).__contains__("%__today_formatted__%"):
                self.variables.update({'%__today_formatted__%': datetime.today().date().strftime("%d-%m-%Y")})
            if str(getattr(step, value)).__contains__("%__month__%"):
                self.variables.update({'%__month__%': datetime.today().month})
            if str(getattr(step, value)).__contains__("%__year__%"):
                self.variables.update({'%__year__%': datetime.today().year})
            if str(getattr(step, value)).__contains__("%__weeknumber__%"):
                self.variables.update({'%__weeknumber__%': datetime.today().strftime("%V")})
            if str(getattr(step, value)).__contains__("%__tomorrow__%"):
                self.variables.update({'%__tomorrow__%': datetime.today() + timedelta(days=1)})
            if str(getattr(step, value)).__contains__("%__tomorrow_formatted__%"):
                self.variables.update({'%__tomorrow_formatted__%': (datetime.today() + timedelta(days=1)).strftime("%d-%m-%Y")})
            if str(getattr(step, value)).__contains__("%__yesterday__%"):
                self.variables.update({'%__yesterday__%': datetime.today() + timedelta(days=-1)})
            if str(getattr(step, value)).__contains__("%__yesterday_formatted__%"):
                self.variables.update({'%__yesterday_formatted__%': (datetime.today() + timedelta(days=-1)).strftime("%d-%m-%Y")})
            if str(getattr(step, value)).__contains__("%__time__%"):
                self.variables.update({'%__time__%': datetime.now().time()})
            if str(getattr(step, value)).__contains__("%__time_fromatted__%"):
                self.variables.update({'%__time_fromatted__%': datetime.now().time().strftime("%H:%M:%S")})
            if str(getattr(step, value)).__contains__("%__now__%"):
                self.variables.update({'%__now__%': datetime.now()})
            if str(getattr(step, value)).__contains__("%__folder_desktop__%"):
                self.variables.update({'%__folder_desktop__%': os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')})
            if str(getattr(step, value)).__contains__("%__folder_downloads__%"):
                self.variables.update({'%__folder_downloads__%': os.path.join(os.path.join(os.environ['USERPROFILE']), 'Downloads')})
            if str(getattr(step, value)).__contains__("%__folder_system__%"):
                self.variables.update({'%__folder_system__%': os.environ['WINDIR'] + "\\System\\"})
            if str(getattr(step, value)).__contains__("%__system_name__%"):
                self.variables.update({'%__system_name__%': socket.getfqdn()})
            if str(getattr(step, value)).__contains__("%__user_name__%"):
                self.variables.update({'%__user_name__%': os.getenv('username')})


    def save_output_variable(self, step, this_step, output_previous_step):
        """
        Save output variable to list
        :param step: The current step object
        :param this_step: The current output variable
        :param output_previous_step: The output of the previous step
        """
        if hasattr(step, "output_variable"):
            if len(step.output_variable) > 0 and str(step.output_variable).startswith("%") and str(
                    step.output_variable).endswith("%"):
                if hasattr(step, "loopcounter"):
                    this_step = output_previous_step
                self.variables.update(
                    {f"{step.output_variable}": this_step})  # Update the variables list


    def loop_items_check(self, loop_variable: str) -> bool:
        """
        Check if there are more items to loop, or it has reached the end
        :param loop_variable: The name of the loopvariable to check.
        :return: True: the variable has more items to loop, False: the loop must end
        """
        retn = None
        try:
            loop = [x for x in self.loopvariables if x.name == loop_variable][0]
            loop.counter += 1
        except:
            print(
                f"Error: probably isn't the variable name '{loop_variable}' the right variable to check for more loop-items...")
            return retn
        if loop is not None:
            if loop.counter < loop.total_listitems:
                retn = True
            else:
                retn = False
        else:
            retn = False
        return retn

    def get_next_step(self, current_step, steps, output_previous_step: Any) -> Any:
        """
        Get the next step in the flow
        :param current_step: The step object of the current step
        :param steps: The steps collection
        :return: The next step object
        """
        retn = None
        col_conn = []
        connectors = [x for x in steps if x.type == "connector"]
        try:
            if str(current_step.type).lower() == "exclusive gateway":
                outgoing_connector = [x for x in connectors if x.source == current_step.id]
            else:
                outgoing_connector = [x for x in connectors if x.source == current_step.id][0]
        except Exception as e:
            return None
        if outgoing_connector is None:
            return None
        if not isinstance(outgoing_connector, list):
            shapes = [x for x in steps if x.type == "shape"]
            col_conn = [x for x in shapes if x.id == outgoing_connector.target]
        if len(col_conn) > 0:
            retn = col_conn[0]
        if retn is None and str(current_step.type).lower() != "exclusive gateway":
            # Next step is a Gateway
            # incoming_connector = [x for x in connectors if x.source == current_step.id][0]
            retn = [x for x in steps if x.id == outgoing_connector.target][0]
        if str(current_step.type).lower() == "exclusive gateway":
            if output_previous_step:
                try:
                    conn = \
                        [x for x in outgoing_connector if
                         (str(x.value).lower() == "true" and x.source == current_step.id)][0]
                except:
                    raise Exception("Your Exclusive Gateway doesn't contain a 'True' or 'False' sequence arrow output.")
            else:
                try:
                    conn = \
                        [x for x in outgoing_connector if
                         (str(x.value).lower() == "false" and x.source == current_step.id)][0]
                except:
                    raise Exception("Your Exclusive Gateway doesn't contain a 'True' or 'False' sequence arrow output.")
            try:
                retn = [x for x in steps if x.id == conn.target][0]
            except:
                print(
                    "Error: probably one of the Exclusive Gateways has some Sequence Flow Arrows that aren't connected properly...")
                return None
        if hasattr(retn, "loopcounter"):
            check_loopvar = [x for x in self.loopvariables if x.id == retn.id]
            if len(check_loopvar) == 0:
                try:
                    loopvar = self.dynamic_object()
                    if hasattr(retn, "output_variable"):
                        loopvar.name = str(retn.output_variable)
                    loopvar.id = retn.id
                    loopvar.start = int(retn.loopcounter)
                    loopvar.counter = loopvar.start
                    loopvar.total_listitems = 0
                    self.loopvariables.append(loopvar)
                except Exception as e:
                    print(f"Error: {e}")
        return retn

    class dynamic_object(object):
        pass


class SQL():

    def __init__(self, dbfolder: str):
        """
        Class for SQLite actions on the Orchestrator database.
        :param dbfolder: The folder of the SQLite orchestrator database
        :param connection: Optional. The sqlite3.connect connection.
        """
        queue = multiprocessing.JoinableQueue()
        if dbfolder == "\\":
            return
        if not dbfolder.endswith("\\"):
            dbfolder += "\\"
        self.connection = sqlite3.connect(f'{dbfolder}orchestrator.db')
        self.connection.execute("PRAGMA foreign_keys = 1")
        self.connection.execute("PRAGMA JOURNAL_MODE = 'WAL'")

    def run_sql(self, sql, tablename: str = ""):
        """
        Run SQL command and commit.
        :param sql: The SQL command to execute.
        :param tablename: Optional. The tablename of the table used in the SQL command, for returning the last id of the primary key column.
        :return: The last inserted id of the primary key column
        """
        if not hasattr(self, "connection"):
            return
        self.connection.execute(sql)
        self.connection.commit()
        if len(tablename) > 0:
            try:
                return self.get_inserted_id(tablename)
            except:
                return None
        else:
            return None

    def get_inserted_id(self, tablename: str) -> int:
        """
        Get the last inserted id of the primary key column of the table
        :param tablename: The name of the table to get the last id of
        :return: The last inserted id of the primary key column
        """
        sql = f"SELECT MAX(id) FROM {tablename};"
        curs = self.connection.cursor()
        curs.execute(sql)
        row = curs.fetchone()
        return int(row[0])

    def commit(self):
        """
        Commit any sql statement
        """
        self.connection.commit()

    def get_registered_flows(self):
        """
        Get a list from all registered flows in the orchestrator database.
        :return: A list of flow names that are registered in the orchestrator database.
        """
        sql = "SELECT name FROM Registered;"
        curs = self.connection.cursor()
        curs.execute(sql)
        rows = curs.fetchall()
        ret = []
        for rw in rows:
            ret.append(f"{rw[0]}.xml")
        return ret

    def remove_registered_flows(self, lst: List = []):
        """
        Removes registered flows from the orchestrator database by maching on the given list of flow-names
        :param lst: The list with flow names to remove from the database
        """
        names = "'" + "', '".join(lst) + "'"
        sql = f"DELETE FROM Registered WHERE name IN ({names});"
        curs = self.connection.cursor()
        curs.execute(sql)
        self.connection.commit()

    def orchestrator(self):
        """
        Create tables for the Orchestrator database
        """
        sql = "CREATE TABLE IF NOT EXISTS Registered (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, location TEXT NOT NULL, description TEXT, timestamp DATE DEFAULT (datetime('now','localtime')));"
        self.run_sql(sql)
        sql = "CREATE TABLE IF NOT EXISTS Workflows (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, registered_id INTEGER NOT NULL, name TEXT NOT NULL, result TEXT, started DATE DEFAULT (datetime('now','localtime')), finished DATE DEFAULT (datetime('now','localtime')), CONSTRAINT fk_Registered FOREIGN KEY (registered_id) REFERENCES Registered (id) ON DELETE CASCADE);"
        self.run_sql(sql)
        sql = "CREATE TABLE IF NOT EXISTS Steps (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, workflow INTEGER NOT NULL, parent TEXT, status TEXT, name TEXT NOT NULL,step TEXT,result TEXT,timestamp DATE DEFAULT (datetime('now','localtime')), CONSTRAINT fk_Workflow FOREIGN KEY (Workflow) REFERENCES Workflows (id) ON DELETE CASCADE);"
        self.run_sql(sql)
        sql = "CREATE TABLE IF NOT EXISTS Triggers (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, registered_id INTEGER NOT NULL, trigger_info, CONSTRAINT fk_Registered_trigger FOREIGN KEY (registered_id) REFERENCES Registered (id) ON DELETE CASCADE);"
        self.run_sql(sql)

# Test
# engine = WorkflowEngine()
# doc = engine.open(fr"c:\\temp\\test2.xml")  # c:\\temp\\test.xml
# steps = engine.get_flow(doc)
# engine.run_flow(steps)
