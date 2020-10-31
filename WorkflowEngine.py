import base64
import importlib
import inspect
import os
import site
import copy
import sqlite3
import urllib
import uuid
import xml.etree.ElementTree as ET
import zlib
from inspect import signature
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
        self.loopvariables = []
        self.previous_step = None
        self.variables = {}  # Dictionary to hold WorkflowEngine variables

    def open(self, filepath: str) -> Any:
        """
        Open a DrawIO document

        :param filepath: The full path (including extension) of the diagram file
        :returns: A DrawIO dictionary object
        """
        # Open an existing document.
        xml_file = open(filepath, "r")
        self.name = filepath.split("\\")[-1].lower().replace(".xml", "")
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
            shapes.append(step)
        else:
            for shape in objects:
                step = self.get_step_from_shape(shape)
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
        if signature is None:
            if hasattr(self.previous_step, "output_variable"):
                var = self.variables.get(self.previous_step.output_variable)
                if var is not None:
                    return var
                else:
                    return None
            return None
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
                            val = ""
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
                                        val = val.replace(tv, replace_value[loopvars[0].counter])
                                else:
                                    if tv.__contains__("[") and tv.__contains__("]"):
                                        if isinstance(replace_value, list):
                                            nr = str(lst[1]).replace("]", "")
                                            if nr.isnumeric():
                                                val = val.replace(tv, replace_value[int(nr)])
                                    elif tv.__contains__("."):
                                        attr = str(lst[0].split(".")[1]).replace(".", "")
                                        if isinstance(replace_value, dict):
                                            val = replace_value.get(attr)
                                        if isinstance(replace_value, object) and not isinstance(replace_value, dict):
                                            val = getattr(replace_value, attr)
                                    else:
                                        val = val.replace(tv, str(replace_value))
                mapping[str(key).lower()] = val
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
        self.previous_step = None
        output_previous_step = None
        shape_steps = [x for x in steps if x.type == "shape"]
        step = [x for x in shape_steps if x.IsStart == True][0]
        while True:
            try:
                # to fetch module
                class_object = None
                module_object = self
                method_to_call = None
                sig = None
                input = None
                if hasattr(step, "module"):
                    # Create a record in the orchestrator database
                    sql = f"INSERT INTO Workflows (uid, name, current_step) VALUES ('{self.uid}', '{self.name}', '{step.name}')"
                    id = self.db.run_sql(sql=sql, tablename="Workflows")  # execute, commit and return the inserted id

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
                                step.module = f"{os.getcwd()}\\Scripts\\{step.module}"
                            if not str(step.module).__contains__(":") and str(step.module).__contains__("\\") and str(
                                    step.module).__contains__(".py"):
                                step.module = f"{site.getsitepackages()[1]}\\{step.module}"
                            if str(step.module).lower().__contains__(".py"):
                                spec = importlib.util.spec_from_file_location(step.module, step.module)
                                module_object = importlib.util.module_from_spec(spec)
                                spec.loader.exec_module(module_object)
                            else:
                                if len(step.module) == 0:
                                    module_object = self
                                else:
                                    module_object = importlib.import_module(step.module)
                        if hasattr(step, "classname"):
                            if hasattr(module_object, step.classname):
                                class_object = getattr(module_object, step.classname)
                                if len(step.function) > 0:
                                    method_to_call = getattr(class_object, step.function)
                            else:
                                method_to_call = getattr(module_object, step.function)
                        else:
                            method_to_call = getattr(module_object, step.function)
                else:
                    if hasattr(step, "function"):
                        method_to_call = getattr(module_object, step.function)

                if method_to_call is not None:
                    try:
                        sig = signature(method_to_call)
                    except Exception as e:
                        print(e)
                    if str(sig) != "()":
                        input = self.get_parameters_from_shapevalues(step=step, signature=sig)

                # execute function call and get returned values
                if input is not None:
                    if len(step.function) > 0:
                        if isinstance(input, dict):
                            output_previous_step = method_to_call(**input)
                        else:
                            try:
                                output_previous_step = method_to_call(input)
                            except:
                                pass
                    else:
                        output_previous_step = class_object(**input)
                else:
                    if hasattr(step, "function"):
                        if len(step.function) > 0:
                            output_previous_step = method_to_call()
                        if output_previous_step is None:
                            output_previous_step = class_object()
                    else:
                        if class_object is not None:
                            output_previous_step = class_object()

                    # set loop variable
                    if hasattr(step, "loopcounter"):
                        # Update the total list count
                        try:
                            loopvar = [x for x in self.loopvariables if x.id == step.id][0]
                            loopvar.start = int(step.loopcounter)  # set start of counter
                            if int(loopvar.counter) <= loopvar.start:
                                loopvar.counter = int(loopvar.start)
                                loopvar.total_listitems = len(output_previous_step) - 2
                                loopvar.name = step.output_variable
                        except Exception as e:
                            print(f"Error: {e}")
                    if hasattr(step, "loopcounter") and loopvar is not None:
                        # It's a loop! Overwrite the output_previous_step with the right element
                        output_previous_step = output_previous_step[loopvar.counter]
                    # Update the result
                    sql_out = str(output_previous_step).replace("\'", "\'\'")
                    if sql_out != 'None':
                        sql = f"UPDATE Workflows SET result ='{sql_out}' WHERE id={id};"
                        self.db.run_sql(sql)
                    if hasattr(step, "classname"):
                        if len(step.classname) == 0:
                            if hasattr(step, "function"):
                                print(f"{step.function} executed.")
                        else:
                            if hasattr(step, "function"):
                                print(f"{step.classname}.{step.function} executed.")
                    else:
                        if hasattr(step, "function"):
                            print(f"{step.function} executed.")
            except Exception as e:
                print(f"Error: {e}")

                pass
            if step is None:
                break
            self.save_output_variable(step, output_previous_step)
            self.previous_step = copy.deepcopy(step)
            step = self.get_next_step(step, steps, output_previous_step)

    def save_output_variable(self, step, output_previous_step):
        """
        Save output variable to list
        :param step: The current step object
        :param output_previous_step: The output of the previous step
        """
        if hasattr(step, "output_variable"):
            if len(step.output_variable) > 0 and str(step.output_variable).startswith("%") and str(
                    step.output_variable).endswith("%"):
                self.variables.update(
                    {f"{step.output_variable}": output_previous_step})  # Update the variables list

    def loop_items_check(self, loop_variable: str) -> bool:
        """
        Check if there are more items to loop, or it has reached the end
        :param loop_variable: The name of the loopvariable to check.
        :return: True: the variable has more items to loop, False: the loop must end
        """
        loop = [x for x in self.loopvariables if x.name == loop_variable][0]
        if loop.counter <= loop.total_listitems:
            retn = True
        else:
            retn = False
        loop.counter += 1
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
            if current_step.type == "exclusive gateway":
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
        if retn is None and current_step.type != "exclusive gateway":
            # Next step is a Gateway
            # incoming_connector = [x for x in connectors if x.source == current_step.id][0]
            retn = [x for x in steps if x.id == outgoing_connector.target][0]
        if current_step.type == "exclusive gateway":
            if output_previous_step:
                conn = \
                [x for x in outgoing_connector if (str(x.value).lower() == "true" and x.source == current_step.id)][0]
            else:
                conn = \
                [x for x in outgoing_connector if (str(x.value).lower() == "false" and x.source == current_step.id)][0]
            retn = [x for x in steps if x.id == conn.target][0]
        if hasattr(retn, "loopcounter"):
            check_loopvar = [x for x in self.loopvariables if x.id == retn.id]
            if len(check_loopvar) == 0:
                try:
                    loopvar = self.dynamic_object()
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
        sql = "CREATE TABLE IF NOT EXISTS Workflows (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,uid TEXT NOT NULL, parent TEXT, name TEXT NOT NULL,current_step TEXT,result TEXT,timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);"
        self.run_sql(sql)


# Test
engine = WorkflowEngine("c:\\python\\python.exe")
engine.db.orchestrator()
doc = engine.open(fr"C:\Users\joost\Desktop\test.xml")  # c:\\temp\\test.xml
steps = engine.get_flow(doc)
engine.run_flow(steps)
