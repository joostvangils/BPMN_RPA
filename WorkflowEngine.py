import base64
import importlib
import inspect
import os
import site
import sqlite3
import urllib
import uuid
import zlib
from inspect import signature
import xml.etree.ElementTree as ET
import typing
from operator import attrgetter

import win32com.client
from typing import List, Any

import xmltodict


class WorkflowEngine():

    def __init__(self, pythonpath: str):
        """
        Class for automating DrawIO diagrams
        :param pythonpath: The full path to the python.exe file
        """
        self.pythonPath = pythonpath
        self.db = SQL()
        self.uid = uuid.uuid1()  # Generate a unique ID for our flow
        self.name = None
        self.variables = {}  # Dictionary to hold WorkflowEngine variables

    def open(self, path: str) -> Any:
        """
        Open a DrawIO document

        :param name: The full path (including extension) of the diagram file
        :returns: A DrawIO dictionary object
        """
        # Open an existing document.
        xml_file = open(path, "r")
        self.name = path.split("\\")[-1].lower().replace(".xml", "")
        xml_root = ET.fromstring(xml_file.read())
        raw_text = xml_root[0].text
        base64_decode = base64.b64decode(raw_text)
        inflated_xml = zlib.decompress(base64_decode, -zlib.MAX_WBITS).decode("utf-8")
        url_decode = urllib.parse.unquote(inflated_xml)
        retn = xmltodict.parse(url_decode)
        return retn

    def get_flow(self, ordered_dict) -> Any:
        """
        Retreiving the elements of the flow in the Document.

        :param ordered_dict: The document object containing the flow elements.
        :returns: A List of flow elements
        """
        connectors = []
        shapes = []
        objects = ordered_dict['mxGraphModel']['root']['object']
        for shape in ordered_dict['mxGraphModel']['root']['mxCell']:
            style = shape.get("@style")
            if style is not None:
                step = self.get_step_from_shape(shape)
                if step.type == "connector":
                    connectors.append(step)
                else:
                    shapes.append(step)
        if not isinstance(objects, list):
            # there is only one shape
            step = self.get_step_from_shape(objects)
            shapes.append(step)
        else:
            for shape in objects:
                step = self.get_step_from_shape(shape)
                shapes.append(step)
        # Find start shape
        for shape in shapes:
            incoming_connector = None
            for conn in connectors:
                if hasattr(conn, "target"):
                    if conn.target == shape.id:
                        incoming_connector = conn
                        break
            if incoming_connector is None:
                shape.IsStart = True
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
            retn.type = "shape"
            retn.IsStart = False
        return retn

    def get_parameters_from_shapevalues(self, step: Any, signature: Any, input: Any) -> str:
        """
        If input values are provided in the Shapevalues, then create a mapping
        :param step: The step to use the Shapevalues of to create the mapping
        :param signature: The imput parametes of the function that needs to be called
        :param input: The inputs from the previous step
        :return: A mapping string
        """
        mapping = {}
        returnNone = True
        for key, value in signature.parameters.items():
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
                            val = input.get(str(value))
                        else:
                            if str(value).__contains__("="):
                                val = value.default
                            else:
                                val = "''"
                    else:
                        returnNone = False
                if isinstance(val, str):
                    if val.replace(".", "").isnumeric():
                        if val.__contains__("."):
                            val = float(val)
                        else:
                            val = int(val)
                mapping[str(key).lower()]=val
        if returnNone:
            return None
        else:
            return mapping

    def step_has_direct_variables(self, step: Any) -> bool:
        """
        Check if a step uses any variables as input for any of the Shapevalue fields
        :param step: The step to check
        :return: True or Flase
        """
        attrs = vars(step)
        col = [key for key,val in attrs.items() if str(val).startswith("%") and str(val).endswith("%") and str(key) != "output_variable"]
        if len(col) > 0:
            return True
        else:
            return False

    def run_flow(self, steps):
        """
        Execute a Workflow.

        :params steps: The steps that must be executed in the flow
        """
        previous_step = None
        output_previous_step = None
        shape_steps = [x for x in steps if x.type == "shape"]
        step = [x for x in shape_steps if x.IsStart == True][0]
        while True:
            try:
                # to fetch module
                if hasattr(step, "module"):
                    class_object = None
                    # Create a record in the orchestrator database
                    sql = f"INSERT INTO Workflows (uid, name, current_step) VALUES ('{self.uid}', '{self.name}', '{step.name}')"
                    id = self.db.run_sql(sql=sql, tablename="Workflows")  # execute, commit and return the inserted id

                    # region get function call
                    method_to_call = None
                    if self.step_has_direct_variables(step):
                        # Get variable from stack
                        var = self.variables.get(step.output_variable)
                        if inspect.isclass(var):
                            method_to_call = getattr(self.variables.get(step.output_variable), step.function)
                    if method_to_call is None:
                        input = None
                        if not str(step.module).__contains__("\\") and str(step.module).lower().__contains__(".py"):
                            step.module = f"{os.getcwd()}\\Scripts\\{step.module}"
                        if not str(step.module).__contains__(":") and str(step.module).__contains__("\\") and str(step.module).__contains__(".py"):
                            step.module = f"{site.getsitepackages()[1]}\\{step.module}"
                        if str(step.module).lower().__contains__(".py"):
                            spec = importlib.util.spec_from_file_location(step.module, step.module)
                            module_object = importlib.util.module_from_spec(spec)
                            spec.loader.exec_module(module_object)
                        else:
                            module_object = importlib.import_module(step.module)
                        if hasattr(module_object, step.classname):
                            class_object = getattr(module_object, step.classname)
                            if len(step.function) > 0:
                                method_to_call = getattr(class_object, step.function)
                        else:
                            method_to_call = getattr(module_object, step.function)
                    # endregion

                    if method_to_call is not None:
                        sig = signature(method_to_call)
                        if str(sig) != "()" and sig is not None:
                            input = self.get_input_parameters(step=step, method_to_call=method_to_call, signature=sig,
                                                              output_previous_step=output_previous_step)
                    else:
                        sig = None

                    # region get input
                    # Get input-parameters from Shapevalues and overwrite Input if any values are given
                    mapping = None
                    if hasattr(step, "mapping"):
                        mapping = step.mapping
                        if len(mapping) == 0:
                            mapping = None
                    else:
                        mapping = None
                    shapevalues = self.get_parameters_from_shapevalues(step=step, signature=sig, input=input)
                    if shapevalues is not None:
                        input = shapevalues
                    # endregion

                    # region execute function call and get returned values
                    if input is not None:
                        if len(step.function) > 0:
                            if class_object is None:
                                output_previous_step = method_to_call(**input)
                            else:
                                output_previous_step = method_to_call(**input)
                        else:
                            output_previous_step = class_object(**input)
                    else:
                        if len(step.function) > 0:
                            if class_object is None:
                                output_previous_step = method_to_call()
                            else:
                                output_previous_step = method_to_call()
                            if output_previous_step is None:
                                output_previous_step = class_object()
                        else:
                            output_previous_step = class_object()
                    # endregion

                    # region set Output variable
                        if len(step.output_variable) > 0 and str(step.output_variable).startswith("%") and str(step.output_variable).endswith("%"):
                            self.variables.update({f"{step.output_variable}": output_previous_step})  # Update the variables list
                    # endregion

                    previous_step = step
                    # Update the result
                    sql_out = str(output_previous_step).replace("\'", "\'\'")
                    sql = f"UPDATE Workflows SET result ='{sql_out}' WHERE id={id};"
                    self.db.run_sql(sql)
                    if len(step.classname) == 0:
                        print(f"{step.function} executed.")
                    else:
                        print(f"{step.classname}.{step.function} executed.")
            except Exception as e:
                print(f"Error: {e}")
                pass
            step = self.get_next_step(step, steps, output_previous_step)
            if step is None:
                break
            previous_step = step

    def get_next_step(self, current_step, steps, output_previous_step):
        """
        Get the next step in the flow

        :param current_step: The step object of the current step
        :param steps: The steps collection
        :return: The next step object
        """
        connectors = [x for x in steps if x.type == "connector"]
        try:
            my_connector = [x for x in connectors if x.source == current_step.id][0]
        except Exception as e:
            return None
        if my_connector is None:
            return None
        shapes = [x for x in steps if x.type == "shape"]
        retn = [x for x in shapes if x.id == my_connector.target][0]
        if hasattr(retn, "name"):
            if str(retn.name).lower() == "exclusive gateway":
                connectors = [x for x in connectors if x.source == retn.id]
                if output_previous_step.get("result"):
                    conn = [x for x in connectors if str(x.name).lower() == "true"]
                else:
                    conn = [x for x in connectors if str(x.name).lower() == "false"]
                retn = [x for x in shapes if x.id == conn[0].target][0]
        return retn

    def build_dict_from_mapping(self, mapping: str) -> typing.Dict[str, str]:
        """
        Create a dictionary from a mapping string

        :param mapping: The mapping string that must be converted to a dictionary
        :returns: The dictionary
        """
        retn = {}
        for map in mapping.split(";"):
            retn[map.split("=")[0].strip()] = map.split("=")[1].strip()
        return retn

    def get_input_parameters(self, step: Any, method_to_call: Any, signature: Any, output_previous_step: Any) -> \
    typing.Dict[str, Any]:
        """
        Fetching parameters to create a dynamic function

        :param step: The current step object
        :param method_to_call: The object of the function that must be called
        :param signature: The signature object of the function that must be called
        :param output_previous_step: The output-object of the previous step
        :returns: A dictionary that can be used as direct input for parameters in a function call
        """
        retn = {}
        mapping = None
        if hasattr(step, "mapping"):
            if len(step.mapping) > 0 and str(step.mapping) != "full_object":
                mapping = self.build_dict_from_mapping(step.mapping)
        if mapping is not None:
            for key, value in mapping.items():
                if output_previous_step is not None:
                    if str(value).startswith("%") and str(value).endswith("%"):
                        var = value.replace("%", "")
                        nr = None
                        attr = None
                        var = var.split("[")[0]
                        if value.__contains__("[") and value.__contains__("]"):
                            nr = int(str(value.replace("%", "").split("[")[1]).replace("]", ""))
                        if value.__contains__(".") and not value.__contains__("["):
                            attr = value.replace("%", "").split(".")[1]
                        var_val = self.variables.get(f"%{var}%")
                        if (isinstance(var_val, list) or isinstance(var_val, tuple)) and nr is not None:
                            retn[key] = var_val[nr]
                        if isinstance(var_val, dict) and attr is not None:
                            retn[key] = var_val.get(attr)
                        if isinstance(var_val, object) and attr is not None:
                            retn[key] = getattr(var_val, attr)
                        if inspect.isclass(var_val):
                            retn[key] = var_val
                    else:
                        retn[key] = output_previous_step.get("result")[int(value)]
                else:
                    return None
            return retn
        else:
            return None

    class dynamic_object(object):
        pass


class SQL():

    def __init__(self):
        """
        Class for SQLite actions on the Orchestrator database.
        """
        self.connection = sqlite3.connect('orchestrator.db')

    def run_sql(self, sql, tablename: str = ""):
        """
        Run SQL command and commit.
        :param sql: The SQL command to execute.
        :param tablename: Optional. The tablename of the table used in the SQL command, for returning the last id of the primary key column.
        :return: The last inserted id of the primary key column
        """
        self.connection.execute(sql)
        self.connection.commit()
        if len(tablename) > 0:
            return self.get_inserted_id("Workflows")
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

    def orchestrator(self):
        """
        Create tables for the Orchestrator database
        """
        sql = "CREATE TABLE IF NOT EXISTS Workflows (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,uid TEXT NOT NULL,name TEXT NOT NULL,current_step TEXT,result TEXT,timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);"
        self.run_sql(sql)


# Test
engine = WorkflowEngine("c:\\python\\python.exe")
engine.db.orchestrator()
doc = engine.open(f"c:\\temp\\test_system.xml")  # c:\\temp\\test.xml
steps = engine.get_flow(doc)
engine.run_flow(steps)
