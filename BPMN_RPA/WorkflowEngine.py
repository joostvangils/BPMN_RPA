import base64
import copy
import defusedxml.ElementTree
import importlib
import importlib.util as util
import inspect
import json
import math
import os
import sys

from werkzeug.utils import secure_filename

if os.name == 'nt':
    import winreg
else:
    import site
import xml.etree.ElementTree as ElTree
import zipfile
import zlib
from datetime import datetime, timedelta
from inspect import signature
from sqlite3 import connect
from pyodbc import connect as connectSQL
from urllib import parse

import xmltodict


# The BPMN-RPA WorkflowEngine is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# The BPMN-RPA WorkflowEngine is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# Copyright 2020-2021 Joost van Gils (J.W.N.M. van Gils)


class WorkflowEngine:

    def __init__(self, input_parameter: any = None, pythonpath: str = "", installation_directory: str = "",
                 delete_records_older_than_days=0, subflow: bool = False, use_sql_server: bool = False):
        """
        Class for automating DrawIO diagrams
        :param input_parameter: An object holding arguments to be passed as input to the WorkflowEngine. In a flow, use get_input_parameter to retrieve the value.
        :param pythonpath: The full path to the python.exe file.
        :param installation_directory: The folder where your BPMN_RPA files are installed. This folder will be used for the orchestrator database.
        :param delete_records_older_than_days: The number of days after which the orchestrator database will clean up records. Default is 0, which means no cleanup.
        :param use_sql_server: Optional. This parameter is used to indicate that the SQLserver on the localhost will be used with a trusted connection. Default is False.
        :param subflow: Optional. This parameter is used to indicate that the flow is a subflow (started from another flow). This is used to make a distinction between the logging of the original flow and the instance of the flow. Default is False.
        """
        settings = {}
        self.subflow = subflow
        self.use_sql_server = use_sql_server
        self.information = ""
        self.db_folder = ""
        if input_parameter is None:
            input_parameter = ""
        if len(pythonpath) != 0:
            if os.name == 'nt':
                self.set_python_path(pythonpath)
            else:
                settings.update({'pythonpath': pythonpath})
        else:
            if os.name == 'nt':
                pythonpath = self.get_python_path()
                pythonpath = pythonpath.replace("/", "\\")
            else:
                sett = '/etc/BPMN_RPA_settings'
                if not os.path.exists(sett):
                    file = open(sett, "w")
                    file.write("{\"pythonpath\": \"\", \"dbpath\":\"\"}")
                    file.close()
                json_file = open(sett, "r")
                data = json.load(json_file)
                json_file.close()
                pythonpath = data["pythonpath"]
        if len(installation_directory) != 0:
            self.set_db_path(installation_directory)
            self.db_folder = installation_directory
        else:
            self.db_folder = self.get_db_path()
        if self.db_folder is not None:
            db_folder = self.db_folder.replace("/", "\\")
        if self.db_folder is None or len(self.db_folder) == 0:
            if os.name == 'nt':
                message = "\nYour installation directory is unknown. Please enter the path of your installation directory: "
            else:
                message = "\nYour installation folder is unknown. Please enter the path of your installation folder: "
            installdir = input(message)
            if os.name == 'nt':
                if not str(installdir).endswith("\\"):
                    installdir += "\\"
            else:
                if not str(installdir).endswith("/"):
                    installdir += "/"
            if not os.path.exists(installdir):
                os.makedirs(installdir)
            if len(installdir) == 0:
                return
            else:
                self.set_db_path(installdir)
                self.db_folder = installdir
        if pythonpath is None or len(pythonpath) == 0:
            if os.name == 'nt':
                message = "\nThe path to your Python.exe file is unknown. Please enter the path to your Python.exe file: "
            else:
                message = "\nEnter the full path of your Python installation:"
            pythonpath = input(message)
            if not os.path.exists(pythonpath):
                self.set_python_path(pythonpath)
            if len(pythonpath) == 0:
                return
            else:
                self.set_python_path(pythonpath)
        if os.name != 'nt':
            settings.update({'dbpath': self.db_folder})
            settings.update({'pythonpath': pythonpath})
            with open('/etc/BPMN_RPA_settings', 'w') as outfile:
                json.dump(settings, outfile)
        self.input_parameter = input_parameter
        self.pythonPath = pythonpath
        if os.name == 'nt':
            self.packages_folder = "\\".join(pythonpath.split('\\')[0:-1]) + "\\Lib\\site-packages"
        else:
            self.packages_folder = pythonpath + "/dist-packages"
        self.db = SQL(dbfolder=self.db_folder, useSQLserver=use_sql_server)
        if delete_records_older_than_days > 0:
            self.db.remove_records_with_timestamp_older_than(delete_records_older_than_days)
        self.db.orchestrator()  # Run the orchestrator database
        self.id = -1  # Holds the ID for our flow
        self.error = None  # Indicator if the flow has any errors in its execution
        self.step_name = None
        self.flowname = None
        self.flowpath = None
        self.loopvariables = []
        self.previous_step = None
        self.step_nr = 0
        self.step_input = None
        self.current_step = None
        self.runlog = []
        self.variables = {}  # Dictionary to hold WorkflowEngine variables

    def get_input_parameter(self, as_dictionary: bool = False) -> any:
        """
        Returns the input parameter that was given when creating an instance of the WorkflowEngine
        :param as_dictionary: Optional. Indicator whether to treat the given input as a dictionary object (string to dict).
        :return: The input_parameter that was given when creating an instance of the WorkflowEngine
        """
        if as_dictionary:
            if not isinstance(self.input_parameter, dict):
                if isinstance(self.input_parameter, str):
                    self.input_parameter = self.input_parameter.replace("true", "True").replace("false",
                                                                                                "False").replace("yes",
                                                                                                                 "Yes").replace(
                        "no", "No")
                self.input_parameter = eval(self.input_parameter)
        self.print_log(f"Got input parameter {str(self.input_parameter)}", "Processing Input")
        return self.input_parameter

    def convert_binary_flow_to_default_file_format(self, flowpath: str) -> str:
        """
        Converts a flow to the default file format (base64 encoded json string) and saves it with the same name.
        :param flowpath: The path to the binary flow that needs to be converted
        """
        # read the binary flow
        flow = self.open(flowpath)
        # base64 encode the content
        string_bytes = json.dumps(flow).encode("ascii")
        base64_bytes = base64.b64encode(string_bytes)
        base64_string = base64_bytes.decode("ascii")
        # write it back to the file
        with open(flowpath, "w") as file:
            file.write(base64_string)
        return base64_string

    def open(self, filepath: str) -> any:
        """
        Open a flow document
        :param filepath: The full path (including extension) of the diagram file
        :returns: A DrawIO dictionary object
        """
        # Open an existing document.
        decoded = None
        if filepath is not None:
            self.flowpath = filepath
        if not filepath.__contains__(".vsdx"):
            if filepath.__contains__(".flw"):
                self.flowname = filepath.split("\\")[-1].replace(".flw", "")
                try:
                    with open(filepath, "r") as f:
                        content = f.read()
                    decoded = base64.b64decode(content).decode("ascii", errors='ignore')
                    retn = json.loads(decoded)
                    # get node where type = "information"
                    info = [x for x in retn if str(x).startswith("{'type': 'information'")]
                    if len(info) > 0:
                        self.information = info[0]["description"]
                        if "use_sql_server" in info[0]:
                            self.use_sql_server = info[0]["use_sql_server"]
                        if self.use_sql_server:
                            self.db = SQL(dbfolder=self.db_folder, useSQLserver=self.use_sql_server)
                            self.db.orchestrator()  # Run the orchestrator database
                    return retn
                except UnicodeDecodeError as e:
                    # Found non-text data in the file
                    print(e)
                    try:
                        with open(filepath, "rb") as binary_file:
                            binary_file.seek(24)
                            # Read the whole file at once
                            content = binary_file.read()
                        str_content = content.decode("ascii", errors='ignore')
                        decoded = None
                    except Exception as e:
                        print(e)
                        pass
                    try:
                        decoded = base64.b64decode(str_content).decode("ascii", errors='ignore')
                        if decoded.__contains__("}]@"):
                            decoded = decoded[0:decoded.index("}]@") + 2]
                        if decoded is not None:
                            if decoded.__contains__("}]"):
                                decoded = decoded[0:decoded.rfind("}]") + 2]
                    except Exception as e:
                        print(e)
                        str_content = str_content[:-1]
                        str_content = "".join([x for x in str_content if x != '' and x != '']).strip().strip(
                            '\x00').strip('\x01').strip('\x0b')
                    if decoded is None:
                        try:
                            decoded = base64.b64decode(str_content).decode("ascii", errors='ignore')
                        except (ValueError, Exception):
                            remain = math.ceil((len(str_content) / 4) - int(len(str_content) / 4))
                            str_content = str_content[0:len(str_content) - remain]
                            idx = 0
                            if str_content.__contains__("fV0") and not str_content.__contains__("In1d"):
                                str_content = str_content.split("fV0")[0][1:] + "fV0==="
                            if str_content.__contains__("In1d"):
                                if str_content.__contains__("In1d") + 4 > idx:
                                    idx = str_content.index("In1d") + 4
                            while idx > 0 and str_content.__contains__("In1d") and not str_content.endswith("In1d"):
                                idx = str_content.index("In1d") + 4
                                str_content = str_content[0:idx]
                            try:
                                decoded = base64.b64decode(str_content).decode("ascii", errors='ignore')
                            except (ValueError, Exception):
                                for i in range(0, 4):
                                    str_content = str_content[0:-1]
                                    try:
                                        decoded = base64.b64decode(str_content).decode("ascii", errors='ignore')
                                        break
                                    except (ValueError, Exception):
                                        pass
                            if decoded.__contains__("}]"):
                                decoded = decoded[0:decoded.rfind("}]") + 2]
                    dict_list = json.loads(decoded)
                    return dict_list
            else:
                self.flowname = filepath.split("\\")[-1].replace(".xml", "")
                xml_file = open(filepath, "r").read()
                retn = xmltodict.parse(xml_file)
                return retn
        else:
            # It is a MsVisio file!
            visio = Visio()
            self.flowname = filepath.split("\\")[-1].replace(".vsdx", "")
            visio.open_vsdx_file(filepath)
            return visio

    @staticmethod
    def set_db_path(value: str):
        """
        Write the orchestrator database path to the registry.
        :param value: The path of the orchestrator database that has to be written to the registry
        """
        if os.name == 'nt':
            try:
                reg_path = r"SOFTWARE\BPMN_RPA"
                winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path)
                registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0,
                                              winreg.KEY_WRITE)
                winreg.SetValueEx(registry_key, "dbPath", 0, winreg.REG_SZ, value)
                winreg.CloseKey(registry_key)
                return True
            except WindowsError:
                return False
        else:
            json_file = open('/etc/BPMN_RPA_settings', 'r')
            data = json.load(json_file)
            json_file.close()
            data["dbpath"] = value
            json_file = open('/etc/BPMN_RPA_settings', 'w')
            json.dump(data, json_file)
            json_file.close()

    @staticmethod
    def get_db_path() -> any:
        """
        Get the path to the orchestrator database
        :return: The path to the orchestrator database
        """
        if os.name == 'nt':
            try:
                reg_path = r"SOFTWARE\BPMN_RPA"
                registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ)
                value, regtype = winreg.QueryValueEx(registry_key, 'dbPath')
                winreg.CloseKey(registry_key)
                return value
            except WindowsError:
                return None
        else:
            json_file = open('/etc/BPMN_RPA_settings', 'r')
            data = json.load(json_file)
            json_file.close()
            return data["dbpath"]

    @staticmethod
    def get_python_path() -> any:
        """
        Get the path to the Python.exe file
        :return: The path to the Python.exe file
        """
        if os.name == 'nt':
            try:
                reg_path = r"SOFTWARE\BPMN_RPA"
                registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ)
                value, regtype = winreg.QueryValueEx(registry_key, 'PythonPath')
                winreg.CloseKey(registry_key)
                return value
            except WindowsError:
                return None
        else:
            json_file = open('/etc/BPMN_RPA_settings', 'r')
            data = json.load(json_file)
            json_file.close()
            return data["pythonpath"]

    @staticmethod
    def set_python_path(value: str):
        """
        Write the oPython path to the registry.
        :param value: The path of the Python.exe file that has to be written to the registry
        """
        if os.name == 'nt':
            try:
                reg_path = r"SOFTWARE\BPMN_RPA"
                winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path)
                registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0,
                                              winreg.KEY_WRITE)
                winreg.SetValueEx(registry_key, "PythonPath", 0, winreg.REG_SZ, value)
                winreg.CloseKey(registry_key)
                return True
            except WindowsError:
                return False
        else:
            json_file = open('/etc/BPMN_RPA_settings', 'r')
            data = json.load(json_file)
            json_file.close()
            data["pythonpath"] = value
            json_file = open('/etc/BPMN_RPA_settings', 'w')
            json.dump(data, json_file)
            json_file.close()

    def get_flow(self, ordered_dict: any) -> any:
        """
        Retrieving the elements of the flow in the Document.
        :param ordered_dict: The document object containing the flow elements.
        :returns: A List of flow elements
        """
        if str(ordered_dict).__contains__("Visio object"):
            # It is a Visio Object!
            visio = ordered_dict
            return visio.get_flow()
        # route for .flw flows
        if isinstance(ordered_dict, list):
            retn = []
            for rw in ordered_dict:
                tmp = self.dynamic_object()
                for k, v in rw.items():
                    ky = k
                    if ky.lower() == "class":
                        ky = "classname"
                    setattr(tmp, ky, v)
                self.store_system_variables(tmp)
                retn.append(tmp)
            # return .flw flow steps
            return retn
        connectors = []
        shapes = []
        connectorvalues = {}
        objects = ordered_dict['mxfile']['diagram']['mxGraphModel']['root']['object']
        for shape in ordered_dict['mxfile']['diagram']['mxGraphModel']['root']['mxCell']:
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

    def get_step_from_shape(self, shape: any) -> any:
        """
        Build a Step-object from the Shape-object
        :param shape: The Shape-object
        :returns: A Step-object
        """
        retn = self.dynamic_object()
        retn.id = shape.get("@id")
        for key, value in shape.items():
            attr = str(key).lower().replace("@", "")
            if attr == "class":
                attr = "classname"  # 'class' is a reserved keyword, so use 'classname'
            setattr(retn, attr, value)
        if shape.get("@source") is not None or shape.get("@target") is not None:
            retn.type = "connector"
        if shape.get("@label") is not None:
            if not hasattr(retn, "name"):
                retn.name = getattr(retn, "label")
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

    @staticmethod
    def get_variables_from_text(text: str) -> any:
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

    def get_parameters_from_shapevalues(self, step: any, input_signature: any) -> any:
        """
        If input values are provided in the Shape values, then create a mapping
        :param step: The step to use the Shape values of to create the mapping
        :param input_signature: The input parameters of the function that needs to be called
        :return: A mapping string
        """
        mapping = {}
        return_none = True
        tmp = None
        if input_signature is None:
            if hasattr(self.previous_step, "output_variable"):
                var = self.variables.get(self.previous_step.output_variable)
                if var is not None:
                    return var
                else:
                    return None
            return None
        for key, value in input_signature.parameters.items():
            attr = None
            if str(key).lower() != "self":
                try:
                    val = str(getattr(step, str(key).lower()))
                except (ValueError, Exception):
                    if str(value).__contains__("="):
                        val = value.default
                    else:
                        val = None
                if val is not None:
                    if len(str(val)) == 0:
                        if input is not None:
                            if str(value.default) == "None":
                                val = None
                            else:
                                val = ""
                        else:
                            if str(value).__contains__("="):
                                val = value.default
                            else:
                                val = "''"
                    else:
                        return_none = False
                if isinstance(val, str):
                    if val == "True" or val == "Yes":
                        val = True
                    elif val == "False" or val == "No":
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
                                                    try:
                                                        val = str(val).replace(tv, replace_value[0])
                                                    except Exception as e:
                                                        val = replace_value[0]
                                                else:
                                                    if len(replace_value) == 0:
                                                        self.print_log(status="Ending loop",
                                                                       result=f"No items to loop...")
                                                        val = replace_value
                                                        # self.exitcode_ok()
                                                    else:
                                                        if loopvars[0].counter < len(replace_value):
                                                            if isinstance(replace_value[loopvars[0].counter], str):
                                                                val = str(val).replace(tv,
                                                                                       replace_value[
                                                                                           loopvars[0].counter])
                                                            else:
                                                                try:
                                                                    val = list(replace_value[loopvars[0].counter])
                                                                except Exception as e:
                                                                    val = [replace_value[loopvars[0].counter]]
                                                                if len(lst) > 1:
                                                                    for lt in lst[1:]:
                                                                        val = val[int(lt.replace("]", ""))]
                                                        else:
                                                            if isinstance(replace_value[0], str):
                                                                val = str(val).replace(tv, replace_value[0])
                                                            else:
                                                                val = replace_value[0]
                                                                if len(lst) > 1:
                                                                    for ls in lst[1:]:
                                                                        val = val[int(ls.replace("]", ""))]

                                                        if str(getattr(step, str(key).lower())) != tv:
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
                                                                            tmp = tmp.replace(tv, str(
                                                                                replace_value[int(nr)]))
                                                                    val = tmp
                                            else:
                                                if loopvars[0].counter < len(replace_value):
                                                    replace_value = self.get_attribute_value(lst[0], replace_value[
                                                        loopvars[0].counter])
                                                    if str(tv).endswith("]%") and str(tv).__contains__("."):
                                                        # get last number from val
                                                        nr = str(tv).split("[")[-1].replace("]%", "")
                                                        if nr.isnumeric():
                                                            if len(replace_value) > int(nr):
                                                                replace_value = replace_value[int(nr)]
                                                else:
                                                    replace_value = self.get_attribute_value(lst[0], replace_value[0])
                                                    if str(tv).endswith("]%") and str(tv).__contains__("."):
                                                        # get last number from val
                                                        nr = str(tv).split("[")[-1].replace("]%", "")
                                                        if nr.isnumeric():
                                                            if len(replace_value) > int(nr):
                                                                replace_value = replace_value[int(nr)]

                                                if isinstance(replace_value, str):
                                                    val = str(val).replace(tv, str(replace_value))
                                                else:
                                                    if val is not None:
                                                        if isinstance(val, str):
                                                            if val.__contains__(tv):
                                                                if isinstance(replace_value, list):
                                                                    if len(replace_value) == 0:
                                                                        replace_value = ""
                                                                val = str(val).replace(tv, str(replace_value))
                                                        else:
                                                            val = replace_value
                                                    else:
                                                        val = replace_value
                                        else:
                                            if str(replace_value).__contains__("Message(mime_content="):
                                                if attr is None:
                                                    attr = ""
                                                if isinstance(replace_value, list):
                                                    if tv.__contains__("."):
                                                        attr = str(lst[0].split(".")[1]).replace(".", "")
                                                    if loopvars[0].counter <= len(replace_value) - 1:
                                                        val = replace_value[loopvars[0].counter]
                                                        if attr is not None:
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
                                                    val = str(val).replace(tv, str(replace_value))
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
                                                                        for lst in repl_list[2:]:
                                                                            tmp2 = tmp2[int(
                                                                                lst.replace("]", "").replace("%", ""))]
                                                                        if isinstance(tmp, str) and tmp != tv:
                                                                            tmp = tmp.replace(tv, tmp2)
                                                                        else:
                                                                            tmp = tmp2
                                            val = tmp
                                    elif tv.__contains__("."):
                                        replace_value = self.get_attribute_value(lst[0], replace_value)
                                        if isinstance(replace_value, str):
                                            val = str(val).replace(tv, str(replace_value))
                                        else:
                                            if val != tv:
                                                val = str(val).replace(tv, str(replace_value))
                                            else:
                                                val = replace_value
                                    else:
                                        if isinstance(replace_value, list):
                                            val = replace_value
                                        elif isinstance(replace_value, str):
                                            val = str(val).replace(tv, str(replace_value))
                                        else:
                                            if val != tv:
                                                val = str(val).replace(tv, str(replace_value))
                                            else:
                                                val = replace_value
                mapping[str(key)] = val
        if return_none:
            return None
        else:
            # replace all reserved keys
            for key in mapping:
                if key in ["id ", "type ", "name ", "description "]:
                    mapping[key.replace(" ", "")] = mapping.pop(key)
            return mapping

    @staticmethod
    def get_attribute_value(lst: str, replace_value: any) -> any:
        """
        Get an attribute value from a replace value (object)
        :param lst: The attribute list
        :param replace_value: The replace value object
        :return: The attribute value or object
        """
        val = None
        lst_ = lst.split(".")[1:]
        if len(lst_) == 0:
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

    @staticmethod
    def step_has_direct_variables(step: any) -> bool:
        """
        Check if a step uses any variables as input for any of the Shapevalue fields
        :param step: The step to check
        :return: True or False
       """
        attrs = vars(step)
        col = [key for key, val in attrs.items() if
               str(val).startswith("%") and str(val).endswith("%") and str(key) != "output_variable"]
        if len(col) > 0:
            return True
        else:
            return False

    def run_flow(self, steps: any, step_by_step: bool = False):
        """
        Execute a Flow.
        :param steps: The steps that must be executed in the flow
        :param step_by_step: Optional. Indicator if this function only performes one step and the looping of steps is done outside this function.
        """
        step = None
        output_previous_step = None
        if not isinstance(steps, list):
            steps = [steps]
            step = steps[0]
        db_path = self.get_db_path()
        if os.name == 'nt':
            if db_path == "\\":
                self.error = True
                raise Exception('Your installation directory is unknown.')
            if not str(self.flowpath).__contains__("\\"):
                self.flowpath = os.getcwd() + "\\" + self.flowpath
        else:
            if db_path == "/":
                self.error = True
                raise Exception('Your installation directory is unknown.')
            if not str(self.flowpath).__contains__("/"):
                self.flowpath = secure_filename(os.getcwd() + "/" + self.flowpath)
        sql = "SELECT id FROM Flows WHERE name =? AND location=?"
        flow_id = self.db.run_sql(sql=sql, params=[self.flowname, self.flowpath], tablename="Flows")
        if flow_id is None:
            sql = "INSERT INTO Flows (name, location) VALUES (?,?);"
            flow_id = self.db.run_sql(sql=sql, params=[self.flowname, self.flowpath], tablename="Flows")
        if step_by_step is False or self.step_nr == 0:
            self.previous_step = None
            shape_steps = [x for x in steps if x.type == "shape"]
            step = [x for x in shape_steps if x.IsStart][0]
            # Log the start in the orchestrator database
            sql = "INSERT INTO Runs (name, flow_id, result) VALUES (?,?,'The flow was aborted.');"
            self.id = self.db.run_sql(sql=sql, params=[self.flowname, flow_id], tablename="Runs")
            print("\n")
            self.print_log(status="Starting",
                           result=f"{datetime.today().strftime('%d-%m-%Y')} Starting flow '{self.flowname}'...")
            self.step_nr = 0
        while True:
            try:
                # to fetch module
                class_object = None
                module_object = None
                method_to_call = None
                this_step = None
                step_input = None
                is_in_loop = False
                if hasattr(step, "name"):
                    self.step_nr += 1
                    self.step_name = step.name
                    self.current_step = step
                    if len(step.name) == 0:
                        if hasattr(step, "type"):
                            if not hasattr(step, "function"):
                                self.print_log(status="Running",
                                               result=f"Passing an {step.type} with value {output_previous_step}...")
                    else:
                        if hasattr(step, "type"):
                            if step.type == "disabled":
                                self.print_log(status="Running",
                                               result=f"Ignoring disabled step '{step.name}'.")
                                step = self.get_next_step(step, steps, output_previous_step)
                                continue

                        if hasattr(step, "function"):
                            if step.function != "print_log":
                                self.print_log(status="Running", result=f"Executing step '{step.name}'...")
                        else:
                            self.print_log(status="Running", result=f"Executing step '{step.name}'...")
                if step is not None:
                    loopkvp = [kvp for kvp in self.loopvariables if kvp.id == step.id]
                    if loopkvp:
                        if loopkvp[0].counter > 0 and loopkvp[0].counter > loopkvp[0].start:
                            is_in_loop = True
                if hasattr(step, "module"):
                    # region get function call
                    method_to_call = None
                    if self.step_has_direct_variables(step):
                        # Get variable from stack
                        if hasattr(step, "output_variable"):
                            var = self.variables.get(step.output_variable)
                            if inspect.isclass(var) and var is not None:
                                method_to_call = getattr(var, step.function)
                    if method_to_call is None:
                        step_input = None
                        if hasattr(step, "module"):
                            if os.name == 'nt':
                                if not str(step.module).__contains__("\\") and str(step.module).lower().__contains__(
                                        ".py"):
                                    step.module = f"{self.packages_folder}\\BPMN_RPA\\Scripts\\{step.module}"
                                if not str(step.module).__contains__(":") and str(step.module).__contains__(
                                        "\\") and str(
                                    step.module).__contains__(".py"):
                                    step.module = f"{self.packages_folder}\\{step.module}"
                            if os.name != 'nt':
                                step.module = str(step.module).replace("\\", "/")
                                module_ = step.module
                                if not str(step.module).__contains__("/") and str(step.module).lower().__contains__(
                                        ".py") and str(step.module).__contains__(self.packages_folder):
                                    module_ = f"{self.packages_folder}/BPMN_RPA/Scripts/{step.module}"
                                if not str(step.module).__contains__("/") and not str(step.module).lower().__contains__(
                                        ".py") and not str(step.module).__contains__(self.packages_folder):
                                    modue_ = f"{self.packages_folder}/{step.module}"
                                step.module = module_
                            if str(step.module).lower().__contains__(".py"):
                                spec = util.spec_from_file_location(step.module, step.module)
                                module_object = util.module_from_spec(spec)
                                if module_object is None:
                                    step_time = datetime.now().strftime("%H:%M:%S")
                                    raise Exception(
                                        f"{step_time}: The module '{step.module}' could not be loaded. Check the path...")
                                getattr(spec.loader, "exec_module")(module_object)
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
                                    if len(step.function) > 0 and class_object is not None:
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
                            if len(step.function) > 0 and class_object is not None:
                                method_to_call = getattr(class_object, step.function)
                    else:
                        if module_object is None:
                            module_object = self
                        if hasattr(step, "function"):
                            method_to_call = getattr(module_object, step.function)

                if method_to_call is not None:
                    step_input = self.get_input_from_signature(step, method_to_call)
                if method_to_call is None and class_object is not None:
                    step_input = self.get_input_from_signature(step, class_object)
                self.step_input = step_input

                # execute function call and get returned values
                if step_input is not None and not is_in_loop:
                    if hasattr(step, "function"):
                        if len(step.function) > 0:
                            if isinstance(class_object, type):
                                class_object = class_object()
                                method_to_call = getattr(class_object, step.function)
                            if isinstance(step_input, dict):
                                output_previous_step = method_to_call(**step_input)
                            else:
                                try:
                                    output_previous_step = method_to_call(step_input)
                                except (ValueError, Exception):
                                    pass
                        else:
                            output_previous_step = class_object(**step_input)
                    else:
                        output_previous_step = class_object(**step_input)
                else:
                    if is_in_loop:
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
                            if output_previous_step is None and not called:
                                output_previous_step = class_object()
                        else:
                            if class_object is not None:
                                if inspect.isclass(class_object):
                                    output_previous_step = class_object()

                # set loop variable
                if output_previous_step is not None:
                    this_step = self.loopcounter(step, output_previous_step)
                if is_in_loop:
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
                        if step.function.lower() in ["loop_items_check", "is_first_item_equal_to_second_item",
                                                     "is_first_item_less_than_second_item",
                                                     "is_first_item_greater_than_second_item",
                                                     "is_first_item_less_or_equal_than_second_item",
                                                     "is_first_item_greater_or_equal_than_second_item",
                                                     "is_time_interval_less_or_equal", "is_time_number_of_seconds_ago",
                                                     "item1_contains_item2", "does_list_contain_item",
                                                     "does_list_contain_any_items", "is_object_empty"]:
                            if step.function.lower() == "loop_items_check" and str(
                                    output_previous_step).lower() == "true":
                                try:
                                    self.print_log(status="Running",
                                                   result=f"{method_to_call.__name__} executed with value {str(output_previous_step)} (loop item: {int(self.get_loop_variable_number(step_input['loop_variable']) + 1)}).")
                                except Exception as e:
                                    pass
                            else:
                                self.print_log(status="Running",
                                               result=f"{method_to_call.__name__} executed with value {str(output_previous_step)}.")
                        else:
                            if step.function != "print_log":
                                self.print_log(status="Running", result=f"{method_to_call.__name__} executed.")
                    else:
                        if hasattr(step, "name"):
                            if len(step.name) > 0:
                                if step.name.lower() == "exclusive gateway":
                                    self.print_log(status="Running",
                                                   result=f"{step.name} executed with value {str(output_previous_step)}.")
                                else:
                                    self.print_log(status="Running", result=f"{step.name} executed.")
            except Exception as ex:
                self.set_error(ex)
                raise Exception(f"Error: {ex}\n{self.error}")
            if step is None:
                self.end_flow()
                break
            if output_previous_step is not None:
                if str(output_previous_step).startswith("QuerySet"):
                    # If this is Exchangelib output then turn it into list
                    output_previous_step = list(output_previous_step)
                if this_step is not None:
                    self.save_output_variable(step, this_step, output_previous_step)
            self.previous_step = copy.deepcopy(step)
            if step_by_step:
                return output_previous_step
            step = self.get_next_step(step, steps, output_previous_step)
        if output_previous_step is not None:
            return output_previous_step

    def get_loop_variable_number(self, var_name):
        """
        Get the loop variable number.
        :param var_name: The name of the loop variable.
        """
        for lv in self.loopvariables:
            if lv.name == var_name:
                return lv.counter
        return 0

    def set_error(self, ex: any):
        """
        Set the internal error coming from the try-except
        :param ex: the exception
        """
        trace = []
        err_ = None
        tb = ex.__traceback__
        while tb is not None:
            trace.append({
                "filename": tb.tb_frame.f_code.co_filename,
                "name": tb.tb_frame.f_code.co_name,
                "lineno": tb.tb_lineno
            })
            tb = tb.tb_next
            err_ = str({
                'type': type(ex).__name__,
                'message': str(ex),
                'trace': trace
            })
        self.error = err_

    def print_log(self, result: str, status: str = ""):
        """
        Log progress to the Orchestrator database and print progress on screen
        :param status: Optional. The status of the step
        :param result: The result of the step
        """
        try:
            result = str(result).replace("<br>", " ")
            result = str(result[0]).capitalize() + result[1:]
            status = str(status)
            if not result.endswith("."):
                result += "."
            step_time = datetime.now().strftime("%H:%M:%S")
            if self.step_nr is not None:
                if self.subflow:
                    print(f"{step_time}: Subflow Step {self.step_nr} - {result}")
                    self.runlog.append(f"{step_time}: Subflow Step {self.step_nr} - {result}")
                else:
                    print(f"{step_time}: Step {self.step_nr} - {result}")
                    self.runlog.append(f"{step_time}: Step {self.step_nr} - {result}")
            else:
                print(f"{step_time}: {result}")
                self.runlog.append(f"{step_time}: {result}")
                self.step_nr = ""
            result = result.replace("'", "''").strip()
            if self.step_name is not None:
                step_name = self.step_name.replace("'", "''")
            else:
                result = "Starting"
                step_name = "Start"
            sql = "INSERT INTO Steps (run, name, step, status, result) VALUES (?,?,?,?,?);"
            self.db.run_sql(sql=sql,
                            params=[self.id, self.flowname, step_name, status, str(self.step_nr) + " " + result])
        except Exception as ex:
            self.set_error(ex)
            raise Exception(self.error)

    def exitcode_not_ok(self):
        """
        Exit the flow with exitcode not OK -1
        """
        self.end_flow()
        sys.exit(-1)

    def exitcode_ok(self):
        """
        Exit the flow with exitcode OK 0
        """
        self.end_flow()
        sys.exit(0)

    def end_flow(self):
        """
        Log the end of the flow in the orchestrator database
        """
        # Flow has ended. Log the end in the orchestrator database.
        ok = "The flow has ended."
        try:
            if self.error:
                ok = "The flow has ended with ERRORS."
            sql = "INSERT INTO Steps (run, name, step, status, result) VALUES (?,?,?,?,?);"
            step_time = datetime.now().strftime("%H:%M:%S")
            finished = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if self.subflow:
                end_result = step_time + ": Subflow Flow '" + self.flowname + "': " + ok
            else:
                end_result = step_time + ": Flow '" + self.flowname + "': " + ok
            print(end_result)
            self.db.run_sql(sql=sql, params=[self.id, self.flowname, 'End', 'Ended', ok], tablename="Steps")
            # Update the result of the flow
            sql = "UPDATE Runs SET result=?, finished=? where id =?;"
            self.db.run_sql(sql=sql, params=[ok, finished, self.id], tablename="Runs")
        except Exception as ex:
            self.set_error(ex)
            raise Exception(f"Error: {ex}\n{self.error}")

    def get_input_from_signature(self, step: any, method_to_call: any) -> any:
        sig = None
        try:
            sig = signature(method_to_call)
        except Exception as ex:
            self.set_error(ex)
            print(f"Error in getting input from input_signature: {self.error}")
        if str(sig) != "()":
            step_input = self.get_parameters_from_shapevalues(step=step, input_signature=sig)
            return step_input
        return None

    def reset_loopcounter(self, reset_for_loop_variable, directcall=True):
        """
        Reset the loopcounter for a loop variable
        :param directcall: Optional. Indication whether a direct call should be made.
        :param reset_for_loop_variable: The name of the loop variable.
        """
        loopvars = [x for x in self.loopvariables if x.name == reset_for_loop_variable]
        if loopvars is not None and len(loopvars) > 0:
            loopvar = loopvars[0]
        else:
            loopvar = None
            if directcall:
                self.print_log(
                    f"Loopcounter '{reset_for_loop_variable}' has not yet been initiated. No reset needed.", "Running")
        if loopvar is not None:
            if loopvar.total_listitems <= loopvar.counter:
                self.loopvariables.remove(loopvar)
                if directcall:
                    self.print_log(f"Loopcounter reset for loopvariable '{reset_for_loop_variable}'",
                                   "Running")

    def loopcounter(self, step: any, output_previous_step: any) -> any:
        """
        Process steps with a loopcounter
        :param step: The current step object
        :param output_previous_step: The output of the previous step as object
        :return: An item from the list that is looped
        """
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
                        if isinstance(output_previous_step, str) and not str(output_previous_step).__contains__(
                                "%") and not isinstance(output_previous_step, list):
                            loopvar.items = [output_previous_step]
                        else:
                            loopvar.items = output_previous_step
                    if loopvar.total_listitems == 0:
                        self.print_log("There are no more items to loop", "Ending loop")
                        # self.exitcode_ok()
                    loopvar.start = int(step.loopcounter)  # set start of counter
                if int(loopvar.counter) <= loopvar.start:
                    loopvar.counter = int(loopvar.start)
                    loopvar.name = step.output_variable
                # It's a loop! Overwrite the output_previous_step with the right element
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
                    self.print_log(end_result, "Looping")
                    return loopvar.items[loopvar.counter]
                else:
                    return output_previous_step
            except Exception as ex:
                self.set_error(ex)
                sql = f"INSERT INTO Steps (run, name, step, status, result) VALUES ('{self.id}', '{self.flowname}', '{step.name}', 'Running', '', 'Error: {self.error}');"
                self.db.run_sql(sql=sql, tablename="Steps")
                self.error = True
                print(f"Error: {self.error}")
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
                self.variables.update({'%__month__%': "{:02d}".format(datetime.today().month)})
            if str(getattr(step, value)).__contains__("%__year__%"):
                self.variables.update({'%__year__%': datetime.today().year})
            if str(getattr(step, value)).__contains__("%__weeknumber__%"):
                self.variables.update({'%__weeknumber__%': datetime.today().strftime("%V")})
            if str(getattr(step, value)).__contains__("%__tomorrow__%"):
                self.variables.update({'%__tomorrow__%': datetime.today() + timedelta(days=1)})
            if str(getattr(step, value)).__contains__("%__tomorrow_formatted__%"):
                self.variables.update(
                    {'%__tomorrow_formatted__%': (datetime.today() + timedelta(days=1)).strftime("%d-%m-%Y")})
            if str(getattr(step, value)).__contains__("%__yesterday__%"):
                self.variables.update({'%__yesterday__%': datetime.today() + timedelta(days=-1)})
            if str(getattr(step, value)).__contains__("%__yesterday_formatted__%"):
                self.variables.update(
                    {'%__yesterday_formatted__%': (datetime.today() + timedelta(days=-1)).strftime("%d-%m-%Y")})
            if str(getattr(step, value)).__contains__("%__time__%"):
                self.variables.update({'%__time__%': datetime.now().time()})
            if str(getattr(step, value)).__contains__("%__time_formatted__%"):
                self.variables.update({'%__time_formatted__%': datetime.now().time().strftime("%H:%M:%S")})
            if str(getattr(step, value)).__contains__("%__now__%"):
                self.variables.update({'%__now__%': datetime.now()})
            if str(getattr(step, value)).__contains__("%__now_formatted__%"):
                self.variables.update({'%__now_formatted__%': datetime.today().date().strftime(
                    "%d-%m-%Y") + "_" + datetime.now().time().strftime("%H%M%S")})
            if str(getattr(step, value)).__contains__("%__folder_desktop__%"):
                self.variables.update(
                    {'%__folder_desktop__%': os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')})
            if str(getattr(step, value)).__contains__("%__folder_downloads__%"):
                self.variables.update(
                    {'%__folder_downloads__%': os.path.join(os.path.join(os.environ['USERPROFILE']), 'Downloads')})
            if str(getattr(step, value)).__contains__("%__folder_system__%"):
                self.variables.update({'%__folder_system__%': os.environ['WINDIR'] + "\\System\\"})
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
        retn = False
        try:
            loop = [x for x in self.loopvariables if x.name == loop_variable][0]
            loop.counter += 1
        except (ValueError, Exception):
            print(
                f"Error: probably isn't the variable name '{loop_variable}' the right variable to check for more loop-items...")
            return retn
        if loop is not None:
            if loop.counter < loop.total_listitems:
                retn = True
            else:
                self.reset_loopcounter(loop_variable, False)
                retn = False
        else:
            self.reset_loopcounter(loop_variable, False)
            retn = False
        return retn

    def get_next_step(self, current_step, steps, output_previous_step: any) -> any:
        """
        Get the next step in the flow
        :param output_previous_step: The output of the previous step.
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
        except (ValueError, Exception):
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
                         ((str(x.value).lower() == "true" or str(
                             x.value).lower() == "yes") and x.source == current_step.id)][0]
                except (ValueError, Exception):
                    raise Exception("Your Exclusive Gateway doesn't contain a 'True' or 'False' sequence arrow output.")
            else:
                try:
                    conn = \
                        [x for x in outgoing_connector if
                         ((str(x.value).lower() == "false" or str(
                             x.value).lower() == "no") and x.source == current_step.id)][0]
                except (ValueError, Exception):
                    raise Exception("Your Exclusive Gateway doesn't contain a 'True' or 'False' sequence arrow output.")
            try:
                retn = [x for x in steps if x.id == conn.target][0]
            except (ValueError, Exception):
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
                except Exception as ex:
                    self.set_error(ex)
                    print(f"Error: {self.error}")
        return retn

    class dynamic_object(object):
        pass

    def set_breakpoint(self):
        """
        Set a breakpoint to debug the code.
        """
        print("---------- Debug ----------")
        finished = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sql = f"UPDATE Runs SET result= 'Encounters a breakpoint.', finished='{finished}' where id = {self.id};"
        self.db.run_sql(sql=sql, tablename="Runs")
        breakpoint()


class SQL:

    def __init__(self, dbfolder: str, useSQLserver: bool = False):
        """
        Class for SQLite actions on the Orchestrator database.
        :param dbfolder: The folder of the SQLite orchestrator database
        :param useSQLserver: Use SQL Server instead of SQLite. TheSQLserver on localhost is used with a trusted connection. The database is called 'orchestrator'. This database must be created in advance with the right permissions. Default is False.
        """
        self.useSQLserver = useSQLserver
        if not self.useSQLserver:
            if os.name == 'nt':
                if dbfolder == "\\":
                    return
                if not dbfolder.endswith("\\"):
                    dbfolder += "\\"
            else:
                if not dbfolder.endswith("/"):
                    dbfolder += "/"
            self.connection = connect(f'{dbfolder}orchestrator.db')
            self.connection.execute("PRAGMA foreign_keys = 1")
            self.connection.execute("PRAGMA JOURNAL_MODE = 'WAL'")
            # if os.name == 'posix':
            #    self.connection.execute("PRAGMA SQLITE_ENABLE_LOCKING_STYLE = 1")
            #    self.connection.execute("PRAGMA journal=OFF")
        else:
            # use the odbc driver for SQL Server
            self.connection = connectSQL(
                "Driver={ODBC Driver 17 for SQL Server};Server=localhost;Database=orchestrator;Trusted_Connection=yes;")
        self.error = None

    def run_sql(self, sql: str, params: any = None, tablename: str = ""):
        """
        Run SQL command and commit.
        :param sql: The SQL command to execute.
        :param params: An array with the parameters for the sql command.
        :param tablename: Optional. The tablename of the table used in the SQL command, for returning the last id of the primary key column.
        :return: The last inserted id of the primary key column
        """
        if params is None:
            params = []
        cursor = None
        if not self.useSQLserver:
            if not hasattr(self, "connection"):
                return
        if not self.useSQLserver:

            self.connection.execute(sql, params)
        else:
            cursor = self.connection.cursor()
            if params is None:
                cursor.execute(sql)
            else:
                cursor.execute(sql, params)
        if not sql.lower().startswith("select"):
            self.connection.commit()
            if len(tablename) > 0:
                try:
                    return self.get_inserted_id(tablename)
                except Exception as ex:
                    self.set_error(ex)
                    raise Exception(self.error)
            else:
                return None
        else:
            if not self.useSQLserver:
                row = self.connection.cursor().fetchone()
            else:
                row = cursor.fetchone()
            if row is not None:
                return row[0]
            else:
                return None

    def set_error(self, ex: any):
        """
        Set the internal error comming from the try-except
        :param ex: the exception
        """
        trace = []
        err_ = None
        tb = ex.__traceback__
        while tb is not None:
            trace.append({
                "filename": tb.tb_frame.f_code.co_filename,
                "name": tb.tb_frame.f_code.co_name,
                "lineno": tb.tb_lineno
            })
            tb = tb.tb_next
            err_ = str({
                'type': type(ex).__name__,
                'message': str(ex),
                'trace': trace
            })
        self.error = err_

    def get_inserted_id(self, tablename: str) -> any:
        """
        Get the last inserted id of the primary key column of the table
        :param tablename: The name of the table to get the last id of
        :return: The last inserted id of the primary key column
        """
        sql = f"SELECT MAX(id) FROM {tablename};"
        curs = self.connection.cursor()
        curs.execute(sql)
        row = curs.fetchone()
        if row[0] is None:
            return None
        return int(row[0])

    def commit(self):
        """
        Commit any sql statement
        """
        try:
            self.connection.commit()
        except Exception as ex:
            self.set_error(ex)
            raise Exception(self.error)

    def get_saved_flows(self):
        """
        Get a list of all saved flows in the orchestrator database.
        :return: A list of flow names that are saved in the orchestrator database.
        """
        sql = "SELECT name FROM Flows;"
        curs = self.connection.cursor()
        curs.execute(sql)
        rows = curs.fetchall()
        ret = []
        for rw in rows:
            ret.append(f"{rw[0]}.xml")
        return ret

    def get_runned_flows(self, flow_id=None):
        """
        Get a list of all runned flows in the orchestrator database.
        :param flow_id: Optional. The flow ID to get the runned data of.
        :return: A list of flow data of flows that have runned.
        """
        if flow_id is None:
            sql = "SELECT * FROM Runs;"
        else:
            sql = "SELECT * FROM Runs WHERE flow_;"
        curs = self.connection.cursor()
        curs.execute(sql)
        rows = curs.fetchall()
        ret = []
        for rw in rows:
            ret.append([rw[0], rw[1], rw[2], rw[3], rw[4], rw[5]])
        return ret

    def get_flows(self):
        """
        Get a list of all flows in the orchestrator database.
        :return: A list of flow names.
        """
        sql = "SELECT * FROM Flows;"
        curs = self.connection.cursor()
        curs.execute(sql)
        rows = curs.fetchall()
        ret = []
        for rw in rows:
            ret.append([rw[0], rw[1], rw[2], rw[3], rw[4]])
        return ret

    def remove_saved_flows(self, lst: list = None):
        """
        Removes saved flows from the orchestrator database by matching on the given list of flow-names
        :param lst: The list with flow names to remove from the database
        """
        if lst is None:
            lst = []
        names = "'" + "', '".join(lst) + "'"
        sql = f"DELETE FROM Flows WHERE name IN ({names});"
        curs = self.connection.cursor()
        curs.execute(sql)
        self.connection.commit()

    def orchestrator(self):
        """
        Create tables for the Orchestrator database
        """
        if not self.useSQLserver:

            try:
                sql = "CREATE TABLE IF NOT EXISTS Flows (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, location TEXT NOT NULL, description TEXT, timestamp DATE DEFAULT (datetime('now','localtime')));"
                self.run_sql(sql)
                sql = "CREATE TABLE IF NOT EXISTS Runs (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, flow_id INTEGER NOT NULL, name TEXT NOT NULL, result TEXT, started DATE DEFAULT (datetime('now','localtime')), finished DATE DEFAULT (datetime('now','localtime')), CONSTRAINT fk_saved FOREIGN KEY (flow_id) REFERENCES Flows (id) ON DELETE CASCADE);"
                self.run_sql(sql)
                sql = "CREATE TABLE IF NOT EXISTS Steps (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, run INTEGER NOT NULL, status TEXT, name TEXT NOT NULL,step TEXT,result TEXT,timestamp DATE DEFAULT (datetime('now','localtime')), CONSTRAINT fk_runs FOREIGN KEY (run) REFERENCES Runs (id) ON DELETE CASCADE);"
                self.run_sql(sql)
                sql = "CREATE TABLE IF NOT EXISTS Survey (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, question_id STRING NOT NULL, question STRING NOT NULL, answer_id string NOT NULL, answer STRING NOT NULL, recipient STRING NOT NULL, received INTEGER DEFAULT 0, timestamp DATE DEFAULT (datetime('now','localtime')));"
                self.run_sql(sql)
            except Exception as ex:
                self.set_error(ex)
                print(ex)
                pass

        else:

            try:
                sql = "IF NOT EXISTS (select * from sysobjects where name='Flows') CREATE TABLE Flows (id INTEGER NOT NULL PRIMARY KEY IDENTITY(1,1), name nvarchar(255) NOT NULL, location nvarchar(255) NOT NULL, description nvarchar(MAX), timestamp DATETIME DEFAULT GETDATE());"
                self.run_sql(sql=sql)
                sql = "IF NOT EXISTS (select * from sysobjects where name='Runs') CREATE TABLE Runs (id INTEGER NOT NULL PRIMARY KEY IDENTITY(1,1), flow_id INTEGER NOT NULL, name nvarchar(255) NOT NULL, result nvarchar(255), started DATETIME DEFAULT GETDATE(), finished DATETIME DEFAULT GETDATE(), CONSTRAINT fk_saved FOREIGN KEY (flow_id) REFERENCES Flows (id) ON DELETE CASCADE);"
                self.run_sql(sql=sql)
                sql = "IF NOT EXISTS (select * from sysobjects where name='Steps') CREATE TABLE Steps (id INTEGER NOT NULL PRIMARY KEY IDENTITY(1,1), run INTEGER NOT NULL, status nvarchar(255), name nvarchar(255) NOT NULL,step nvarchar(255),result nvarchar(255),timestamp DATETIME DEFAULT GETDATE(), CONSTRAINT fk_runs FOREIGN KEY (run) REFERENCES Runs (id) ON DELETE CASCADE);"
                self.run_sql(sql=sql)
                sql = "IF NOT EXISTS (select * from sysobjects where name='Survey') CREATE TABLE Survey (id INTEGER NOT NULL PRIMARY KEY IDENTITY(1,1), question_id NVARCHAR(255) NOT NULL, question NVARCHAR(MAX) NOT NULL, answer_id NVARCHAR(MAX) NOT NULL, answer NVARCHAR(MAX) NOT NULL, recipient NVARCHAR(255) NOT NULL, received INTEGER DEFAULT 0, timestamp DATETIME DEFAULT GETDATE());"
                self.run_sql(sql=sql)
            except Exception as ex:
                self.set_error(ex)
                print(ex)
                pass

    def remove_records_with_timestamp_older_than(self, table: str, days: int):
        """
        Remove records from a table with a timestamp older than the given days
        :param table: The table to remove records from
        :param days: The number of days to keep records
        """
        sql = f"DELETE FROM {table} WHERE timestamp < datetime('now', '-{days} day');"
        self.run_sql(sql)


class Visio:

    def __init__(self):
        """
        Class for reading a flow in MsVisio format (vsdx).
        """
        self.root = None
        self.master_connection = []
        self.master_shape = []

    class dynamic_object(object):
        pass

    def open_vsdx_file(self, file: str):
        """
        Open the VSDX file and store its cointents into memory.
        :param file: The filename to read.
        """
        with zipfile.ZipFile(file, "r") as docs:
            self.root = {}
            for d in docs.filelist:
                if str(d.filename).lower().endswith(".xml") or str(d.filename).lower().endswith(".rels"):
                    doc = docs.read(d)
                    dct = xmltodict.parse(doc)
                    self.root.update({d.filename: dct})

    def get_start(self):
        """
        Return the start Shape of the flow.
        """
        count = 1
        while True:
            if f"visio/pages/page{count}.xml" in self.root:
                for shape in self.root[f"visio/pages/page{count}.xml"].get("PageContents").get("Shapes").get("Shape"):
                    if "Section" in shape:
                        section = shape.get("Section")
                        if not isinstance(section, list):
                            section = [section]
                        for sec in section:
                            if sec["@N"] == "Property":
                                if not isinstance(sec["Row"], list):
                                    if {"@N": "Label", "@V": "Type"} in sec["Row"].get("Cell") and {"@N": "Value",
                                                                                                    "@V": "Start",
                                                                                                    "@U": "STR"} in sec[
                                        "Row"].get("Cell"):
                                        setattr(shape, "IsStart", True)
                                        return shape
                                else:
                                    for rw in sec["Row"]:
                                        if "Cell" in rw:
                                            if {"@N": "Label", "@V": "Type"} in rw.get("Cell") and {"@N": "Value",
                                                                                                    "@V": "Start",
                                                                                                    "@U": "STR"} in rw.get(
                                                "Cell"):
                                                setattr(shape, "IsStart", True)
                                                return shape
                count += 1
            else:
                break
        return None

    def get_connectors(self) -> list:
        """
        Get all connectors from the flow.
        :return: A list of connectors.
        """
        retn = []
        count = 1
        while True:
            if f"visio/pages/page{count}.xml" in self.root:
                connects = self.root[f"visio/pages/page{count}.xml"].get("PageContents").get("Connects").get("Connect")
                if connects:
                    for shp in self.root[f"visio/pages/page{count}.xml"].get("PageContents").get("Connects").get(
                            "Connect"):
                        conn = {"@ID": shp["@FromSheet"], "type": "connector"}
                        if shp["@FromCell"] == "BeginX":
                            obj = [x for x in
                                   self.root[f"visio/pages/page{count}.xml"].get("PageContents").get("Shapes").get(
                                       "Shape") if x["@ID"] == shp["@FromSheet"]][0]
                            text = None
                            if "Text" in obj:
                                text = obj["Text"]
                            if text is not None:
                                conn.update({"value": text})
                            conn.update({"source": shp["@ToSheet"]})
                            target = [y for y in [x for x in connects if x["@FromSheet"] == shp["@FromSheet"]] if
                                      y["@FromCell"] == "EndX"][0]["@ToSheet"]
                            conn.update({"target": target})
                            retn.append(conn)
                    count += 1
            else:
                break
        return retn

    def get_flow(self):
        """
        Get the flow from the file.
        :return: The flow object.
        """
        flow_ = []
        shape = self.get_start()
        flow_.append(shape)
        count = 1
        while True:
            if f"visio/pages/page{count}.xml" in self.root:
                shapes = self.root[f"visio/pages/page{count}.xml"].get("PageContents").get("Shapes").get("Shape")
                for shp in shapes:
                    if "@NameU" in shp:
                        if str(shp["@NameU"]).lower().__contains__("connector"):
                            if shp["@Master"] not in self.master_connection:
                                self.master_connection.append(shp["@Master"])
                    if not flow_.__contains__(shp) and not shp["@Master"] in self.master_connection:
                        flow_.append(shp)
                count += 1
            else:
                break
        connectors = self.get_connectors()
        flow_ += connectors
        retn = []
        for s in flow_:
            if s is not None:
                step = self.get_step_from_shape(s)
                retn.append(step)
        return retn

    def get_step_from_shape(self, shape: any) -> any:
        """
        Build a Step-object from the Shape-object
        :param shape: The Shape-object
        :returns: A Step-object
        """
        properties = {"id": shape.get("@ID")}
        properties.update({"type": "shape"})
        if "@Name" in shape:
            properties.update({"name": shape["@Name"]})
        properties.update({"IsStart": False})
        retn = self.dynamic_object()
        if "type" in shape:
            if str(shape["type"]).lower().__contains__("connector"):
                properties.pop("IsStart")
                properties.update({"type": "connector"})
                properties.update({"target": shape["target"]})
                properties.update({"source": shape["source"]})
                if "value" in shape:
                    properties.update({"value": shape["value"]})
                    properties.update({"name": shape["value"]})
                for k, v in properties.items():
                    setattr(retn, k, v)
                return retn

        # Get default attributes if any
        standard_attributes = []
        props = []
        target_id = None
        # region attributes from template
        if "@Master" in shape:
            master = shape["@Master"]
            obj = [x for x in self.root[f"visio/masters/masters.xml"].get("Masters").get("Master") if
                   x["@ID"] == master]
            if obj:
                r_id = obj[0]["Rel"]["@r:id"]
                obj = [x for x in
                       self.root[f"visio/masters/_rels/masters.xml.rels"].get("Relationships").get("Relationship") if
                       x["@Id"] == r_id]
                if obj:
                    target_id = obj[0]["@Target"]
                    obj = [x for x in
                           self.root[f"visio/masters/{target_id}"]["MasterContents"]["Shapes"]["Shape"]["Section"] if
                           x["@N"] == "Property"]
                    if obj:
                        if "Cell" in obj[0]["Row"]:
                            standard_attributes = obj[0]["Row"]["Cell"]
                        else:
                            for rw in obj[0]["Row"]:
                                for attr in rw["Cell"]:
                                    standard_attributes.append(attr)
        key = None
        value = None
        for rw in standard_attributes:
            if rw["@N"] == "Label":
                key = rw["@V"]
            if rw["@N"] == "Value":
                value = rw["@V"]
            if key is not None and value is not None:
                properties.update({"row_id": "template", str(key).lower(): value})
                # reset key and value
                key, value = None, None
        labels = []
        if target_id is not None:
            obj = [x for x in self.root[f"visio/masters/{target_id}"]["MasterContents"]["Shapes"]["Shape"]["Section"] if
                   x["@N"] == "Property"]
            if obj:
                labels = obj[0]["Row"]
        # endregion
        if "Section" in shape:
            if not isinstance(shape["Section"], list):
                sect = [shape["Section"]]
            else:
                sect = [x for x in shape["Section"] if x["@N"] == "Property"]
            # sect is a list or ordered dict. Get the 'Property' section
            if [x for x in sect if x["@N"] == "Property"]:
                props = [x for x in sect if x["@N"] == "Property"][0].get("Row")
            # props is now the 'Property' section of the Shape
            # Loop the properties
            # props is ordered_dict based on stencil, but list[ordered_dict] for manual
            if not isinstance(props, list):
                props = [props]
            for prop in props:
                # get the property row_id
                row_id = None
                if str(prop.get("@N")).lower().__contains__("row_"):
                    row_id = prop.get("@N")
                # region get the key and value
                key, value = None, None
                if "Cell" not in prop:
                    continue
                if isinstance(prop.get("Cell"), dict):
                    # it is a value that belongs to a template label
                    label = [x for x in labels if x["@N"] == row_id]
                    kvps = None
                    if label:
                        kvps = label[0]["Cell"]
                    rw_k = [x for x in kvps if x["@N"] == "Label"]
                    if rw_k:
                        key = rw_k[0]["@V"]
                    value = prop.get("Cell")["@V"]
                else:
                    rw_k = [x for x in prop.get("Cell") if x["@N"] == "Label"]
                    if rw_k:
                        key = rw_k[0]["@V"]
                    rw_l = [x for x in prop.get("Cell") if x["@N"] == "Value"]
                    if rw_l:
                        value = rw_l[0]["@V"]
                    # endregion
                if key is not None and value is not None:
                    properties.update({"row_id": row_id, str(key).lower(): value})

        if "Section" in shape:
            for rw in shape["Section"]:
                if str(rw).lower().__contains__("('@v', 'exclusive gateway')") and str(rw).lower().__contains__(
                        "('@n', 'type')"):
                    properties.update({"type": "exclusive gateway"})
                    properties.update({"name": ""})
                if str(rw).lower().__contains__("('@v', 'parallel gateway')") and str(rw).lower().__contains__(
                        "('@n', 'type')"):
                    properties.update({"type": "parallel gateway"})
                    properties.update({"name": ""})

        if "type" not in shape:
            count = 1
            while True:
                if f"visio/pages/page{count}.xml" in self.root:
                    if not [x for x in
                            self.root[f"visio/pages/page{count}.xml"].get("PageContents").get("Connects").get("Connect")
                            if x["@FromCell"] == "EndX" and x["@ToSheet"] == shape["@ID"]]:
                        properties.update({"IsStart": True})
                        properties.update({"name": "Start"})
                        properties.update({"type": "shape"})
                    if not [x for x in
                            self.root[f"visio/pages/page{count}.xml"].get("PageContents").get("Connects").get("Connect")
                            if x["@FromCell"] == "BeginX" and x["@ToSheet"] == shape["@ID"]]:
                        properties.update({"name": "End"})
                        properties.update({"type": "shape"})
                    count += 1
                else:
                    break
        properties.update({"id": shape.get("@ID")})
        if "Text" in shape:
            properties.update({"name": str(shape["Text"]).lower()})
        if str(properties["name"]).lower().__contains__("gateway"):
            properties.update({"name": ""})
        properties.update({"type": str(properties["type"]).lower()})
        for k, v in properties.items():
            setattr(retn, k, v)
        return retn