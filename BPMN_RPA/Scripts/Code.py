import base64
import inspect
import json
import os
import sys
from urllib import parse
import zlib
import ast
from importlib import util
from pathlib import Path
from typing import List, Any

import xmltodict
from lxml import etree as eltree

from BPMN_RPA.WorkflowEngine import WorkflowEngine


class DynamicObject(object):
    pass


class Code:

    def __init__(self):
        """
        Class for reading code modules and creating and updating DrawIO libraries.
        """
        self.libs = []
        self.libpath = ""
        self.current_dict = None

    @staticmethod
    def openflow(filepath: str, as_xml: bool = False) -> Any:
        """
        Open a DrawIO document
        :param filepath: The full path (including extension) of the diagram file
        :param as_xml: Optional. Returns the file content as XML.
        :returns: A DrawIO dictionary object
        """
        # Open an existing document.
        xml_file = open(filepath, "r")
        header = xml_file.readlines()
        xml_file.seek(0, 0)
        root = eltree.fromstring(header[0])
        xml_root = eltree.fromstring(xml_file.read())
        raw_text = xml_root[0].text
        base64_decode = base64.b64decode(raw_text)
        inflated_xml = zlib.decompress(base64_decode, -zlib.MAX_WBITS).decode("utf-8")
        url_decode = parse.unquote(inflated_xml)
        if as_xml:
            return url_decode
        retn = xmltodict.parse(url_decode)
        return retn, root

    @staticmethod
    def saveflow(filepath: str, dct: Any, original: Any) -> Any:
        """
        Save a flow to a DrawIO document
        :param filepath: The full path (including extension) of the file.
        :param dct: The ordered dictionary that contains the flow content.
        :param original: the original file content
        """
        retn = xmltodict.unparse(dct)
        retn = parse.quote(retn).replace("/", "%2F")
        retn = zlib.compress(retn.encode('unicode_escape'))
        retn = retn[2:]
        content = base64.b64encode(retn).decode('utf-8')
        original[0].text = content
        # Open an existing document.
        newcontent = eltree.tostring(original)
        xml_file = open(filepath, "w")
        xml_file.write(newcontent.decode('utf8'))
        xml_file.close()

    def get_flow(self, ordered_dict: Any) -> Any:
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

    @staticmethod
    def get_step_from_shape(shape: Any) -> Any:
        """
        Build a Step-object from the Shape-object
        :param shape: The Shape-object
        :returns: A Step-object
        """
        retn = DynamicObject()
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

    def check_flow_for_usage(self, flow: str, search_module: str = "", search_class: str = "",
                             search_function: str = "") -> List:
        """
        Check if the given code is used in the steps of a flow.
        :param flow: The path to the file of the flow.
        :param search_module: Optional. The full path of the module to search.
        :param search_class: Optional. The classname to search.
        :param search_function: Optional. The function name to search.
        :return: A list of explenations in which step the code is used.
        """
        doc, _ = self.openflow(flow)
        flowname = flow.split("\\")[-1]
        steps = self.get_flow(doc)
        retn = []
        hasclass = []
        hasmodule = []
        hasfunction = []
        for step in steps:
            modulename = ""
            if hasattr(step, 'module'):
                modulename = step.module.split("\\")[-1].lower()
            if len(modulename) > 0 and modulename == search_module.lower():
                if not hasmodule.__contains__(step.name):
                    hasmodule.append(step.name)
            classname = ""
            if hasattr(step, 'classname'):
                classname = step.classname.lower()
            if len(classname) > 0 and classname == search_class.lower():
                if not hasclass.__contains__(step.name):
                    hasclass.append(step.name)
            functionname = ""
            if hasattr(step, 'function'):
                functionname = step.function.lower()
            if len(functionname) > 0 and functionname == search_function.lower():
                if not hasfunction.__contains__(step.name):
                    hasfunction.append(step.name)
        for cl in hasclass:
            retn.append(f"Class \"{search_class}\" is used in step \"{cl}\" of flow \"{flowname}\".")
        for m in hasmodule:
            retn.append(f"Module \"{search_module}\" is used in step \"{m}\" of flow \"{flowname}\".")
        for f in hasfunction:
            retn.append(f"Function \"{search_function}\" is used in step \"{f}\" of flow \"{flowname}\".")
        return retn

    def get_library(self, filepath: str) -> Any:
        """
        Read a library file and return its content.
        :param filepath: The full path of the library to read.
        :return: The library content.
        """
        # Open an existing document.
        xml_file = open(filepath, "r")
        xml_root = eltree.fromstring(xml_file.read())
        if xml_root.text is not None:
            retn = json.loads(xml_root.text)
            return retn
        else:
            dct = self.openflow(filepath, False)
            shapes = dct[0].get("mxGraphModel").get("root").get("object")
            return shapes

    def save_library(self):
        """
        Save the current library to a file.
        """
        try:
            self.current_dict.sort(key=lambda x: x["title"], reverse=False)
        except (ValueError, Exception):
            pass
        content = "<mxlibrary>" + json.dumps(self.current_dict) + "</mxlibrary>"
        # Open an existing document.
        xml_file = open(self.libpath, "w")
        xml_file.write(content)
        xml_file.close()

    @staticmethod
    def shape_decode(shape: Any):
        """
        Decode the content of a shape to xml.
        :param shape: The shape to decode the content of.
        :return: Decoded xml of the shape.
        """
        base64_decode = base64.b64decode(shape.get("xml"))
        inflated_xml = zlib.decompress(base64_decode, -zlib.MAX_WBITS).decode("utf-8")
        retn = parse.unquote(inflated_xml)
        return retn

    @staticmethod
    def shape_encode(shape_xml: str) -> str:
        """
        Encode the xml of a shape.
        :param shape_xml: The xml to encode.
        :return: Encoded xml.
        """
        retn = parse.quote(shape_xml).replace("/", "%2F")
        retn = zlib.compress(retn.encode('unicode_escape'))
        retn = retn[2:]
        retn = base64.b64encode(retn).decode('utf-8')
        # print(retn)
        return retn

    def add_descriptions_to_library(self, filepath: str):
        """
        Add (or update) descriptions from code to all shapes in a library.
        :param filepath: The full path to the library file.
        """
        self.libpath = filepath
        if len([x for x in self.libs if x["name"] == filepath]) == 0:
            dct = self.get_library(filepath)
            tmp_dct = self.TempDict(dct, filepath)
            self.libs.append(tmp_dct)
        else:
            tmp_dct = [x for x in self.libs if x["name"] == filepath][0]
        idx = self.libs.index(tmp_dct)
        dct = tmp_dct.dict
        for shape in dct:
            xml = self.shape_decode(shape)
            root = eltree.ElementTree(eltree.fromstring(xml))
            found = root.find('.//root/object')
            if found is not None:
                fields = found.attrib
                classname = fields.get("Class")
                module = fields.get("Module")
                function = fields.get("Function")
                mapping = fields.get("Mapping")
                variable = fields.get("Output_variable")
                label = fields.get("label")
                if module is not None:
                    if module.startswith("RPA_"):
                        module = module.replace("RPA_", "")
                        fields.update({"Module": module})
                doc = self.get_docstring_from_code(module, function, filepath, classname)
                if doc is None:
                    doc = ""
                found.set('Shape_description', doc)
                if classname is not None:
                    if len(classname) == 0:
                        del found.attrib["Class"]
                if mapping is not None:
                    if len(mapping) == 0:
                        del found.attrib["Mapping"]
                if variable is not None:
                    if len(variable) == 0 and label.lower() != "template":
                        del found.attrib["Output_variable"]
                # found.set('tooltip', doc)
                xml = eltree.tostring(root.getroot()).decode('utf-8')
                xml = self.shape_encode(xml)
                root.find('.//root/object')
                shape.update({"xml": str(xml)})
        tmp_dct.dict = dct
        self.libs[idx] = tmp_dct
        self.current_dict = dct

    def library_has_shape(self, filepath: str, module: str, function: str, classname: str = "") -> bool:
        """
        Chewck if a library has a shape that uses a specific code.
        :param filepath: The full patyh of the library.
        :param module: The full path of the module.
        :param function: The function name.
        :param classname: The class name.
        :return: True or False
        """
        dct = self.get_library(filepath)
        for shape in dct:
            if str(shape) == "{'xml': ''}":
                continue
            xml = self.shape_decode(shape)
            root = eltree.ElementTree(eltree.fromstring(xml))
            found = root.find('.//root/object')
            if found is not None:
                fields = found.attrib
                classname_ = fields.get("Class")
                if classname_ is None:
                    classname_ = ""
                module_ = fields.get("Module")
                if module_ is None:
                    module_ = ""
                function_ = fields.get("Function")
                if function_ is None:
                    function_ = ""
                if len(function) == 0:
                    if module_.lower() == module.lower() and classname_.lower() == classname.lower():
                        return True
                if module_.lower() == module.lower() and classname_.lower() == classname.lower() and function_.lower() == function.lower():
                    return True
        return False

    def get_docstring_from_code(self, module: str, function: str, filepath: str, classname: str = "") -> str:
        """
        Retreive the comments from code.
        :param module: The module name, including the path.
        :param function: The function name.
        :param filepath: The full path of the library file.
        :param classname: Optional. The Classname.
        :return: A string with the comments from code.
        """
        callobject = None
        method_to_call = None
        classobject = None
        module_ = module
        classname_ = classname
        checks = [module is None, classname is None]
        try:
            if all(checks):
                module = str(
                    "\\".join(sys.executable.split("\\")[:-1])) + r"\Lib\site-packages\BPMN_RPA\WorkflowEngine.py"
                classname = "WorkflowEngine"
            if len(module) == 0 and len(classname) == 0:
                module = str(
                    "\\".join(sys.executable.split("\\")[:-1])) + r"\Lib\site-packages\BPMN_RPA\WorkflowEngine.py"
                classname = "WorkflowEngine"
            if classname.startswith("%") and classname.endswith("%"):
                if module is not None:
                    if not module.startswith("%") and not module.endswith("%"):
                        classname = module.split("\\")[-1].replace(".py", "")
            else:
                if classname.startswith("%") and classname.endswith("%"):
                    module, classname = self.get_module_from_variable_name(classname, filepath)
                if module is None and classname is None:
                    module = module_
                    classname = classname_
            if not module.endswith(".py"):
                path = "\\".join(sys.executable.split("\\")[:-1]) + "\\Lib\\"
                if os.path.exists(path + module + ".py"):
                    module = path + module + ".py"
            spec = util.spec_from_file_location(module, module)
            if spec is not None:
                module_object = util.module_from_spec(spec)
                getattr(spec.loader, "exec_module")(module_object)
                callobject = module_object
                if classname is not None:
                    if len(classname) > 0:
                        classobject = getattr(module_object, classname)
                        callobject = classobject
            if function is not None:
                if len(function) > 0:
                    method_to_call = getattr(callobject, function)
            else:
                method_to_call = getattr(classobject, "__init__")
            doc = inspect.getdoc(method_to_call)
            if doc is not None:
                doc = doc.replace(":param ", "\n").replace(":return: ", "\nReturn: ").replace(":returns: ",
                                                                                              "\nReturn: ")
                return doc
            else:
                return ""
        except (ValueError, Exception):
            return ""

    def sort_library(self, filepath: str) -> Any:
        """
        Sort a DrawIo library of shapes.
        :param filepath: The path to the library file.
        :return: The sorted library as a list of dictionaries.
        """
        dct = self.get_library(filepath)
        try:
            dct.sort(key=lambda x: x["title"], reverse=False)
        except (ValueError, Exception):
            raise Exception("Cannot sort the library: one of the shapes in the library has no title.")
        self.current_dict = dct
        self.libpath = filepath
        self.save_library()
        return dct

    def get_module_from_variable_name(self, variable: str, filepath: str) -> Any:
        """
        Get the module path from a variable name.
        :param variable: The name of the variable.
        :param filepath: The full path of the library file.
        :return: Tuple: The full path of the module and the classname.
        """
        classname = None
        module = None
        output_variable = None
        dct = self.get_library(filepath)
        for shape in dct:
            if "xml" in shape:
                if len(shape.get("xml")) == 0:
                    return None, None
                xml = self.shape_decode(shape)
                root = eltree.ElementTree(eltree.fromstring(xml))
                found = root.find('.//root/object')
                if found is not None:
                    fields = found.attrib
                    classname = fields.get("Class")
                    module = fields.get("Module")
                    output_variable = fields.get("Output_variable")
            else:
                classname = shape.get("@Class")
                module = shape.get("@Module")
                output_variable = shape.get("@Output_variable")
            if output_variable == variable:
                return module, classname
        return None, None

    @staticmethod
    def search_modulename_in_flow(variable: str, flowsteps: Any) -> Any:
        """
        Search for the module path from a variable name.
        :param variable: The name of the variable.
        :param flowsteps: The steps of the flow (objects).
        :return: Tuple: The full path of the module and the classname.
        """
        for shape in flowsteps:
            classname = shape.get("@Class")
            module = shape.get("@Module")
            output_variable = shape.get("@Output_variable")
            if output_variable == variable:
                return module, classname
        return None, None

    class TempDict:

        def __init__(self, hold_dict, name):
            """
            Hold Dict infor with a name attached to it.
            :param hold_dict: The dictionary to hold.
            :param name: The name for the dictionary to hold.
            """
            self.dict = hold_dict
            self.name = name

    def add_shape_from_function_to_library(self, filepath: str, module: str, function: str, classname: str = "",
                                           title: str = "", variable: str = ""):
        """
        Create a shape from code and add it to a shape library.
        :param filepath: The path to the library file.
        :param module: The full path of the module.
        :param function: The name of the function.
        :param classname: Optional. The class name.
        :param title: Optional. The title of the new created shape in the library.
        :param variable: Optional. The name of the class variable to set as class in the function shape.
        """
        self.libpath = filepath
        if function == "__init__":
            function = ""
        if len([x for x in self.libs if x.name == filepath]) == 0:
            dct = self.get_library(filepath)
            tmp_dct = self.TempDict(dct, filepath)
            self.libs.append(tmp_dct)
        else:
            tmp_dct = [x for x in self.libs if x.name == filepath][0]
        idx = self.libs.index(tmp_dct)
        dct = tmp_dct.dict
        if len(title) == 0 and len(function) > 0:
            title = function.capitalize().replace("_", " ")
        if len(function) == 0:
            title = f"Create {classname} object"
        newentry = {'xml': '', 'w': 120, 'h': 80, 'aspect': 'fixed', 'title': title}
        newshape = f"<mxGraphModel><root><mxCell id=\"0\"/><mxCell id=\"1\" parent=\"0\"/><object label=\"{title}\" Module=\"{module}\" Class=\"{classname}\" Function=\"{function}\" Output_variable=\"\" id=\"2\" Shape_description=\"\"><mxCell style=\"shape=ext;rounded=1;html=1;whiteSpace=wrap;\" vertex=\"1\" parent=\"1\"><mxGeometry width=\"120\" height=\"80\" as=\"geometry\"/></mxCell></object></root></mxGraphModel>"
        root = eltree.ElementTree(eltree.fromstring(newshape))
        found = root.find('.//root/object')
        if module is None:
            module = str(Path(os.getcwd()).parent) + r"\WorkflowEngine.py"
            classname = "WorkflowEngine"
        if len(module) == 0:
            module = str(Path(os.getcwd()).parent) + r"\WorkflowEngine.py"
            classname = "WorkflowEngine"
        if not module.endswith(".py"):
            path = "\\".join(sys.executable.split("\\")[:-1]) + "\\Lib\\"
            if os.path.exists(path + module + ".py"):
                module = path + module + ".py"
            else:
                path = "".join(sys.executable.split("\\")[:-1]) + "\\Lib\\site-packages\\" + module
                if os.path.exists(path + module + ".py"):
                    module = path + module + ".py"
        if function is not None:
            classobject = None
            spec = util.spec_from_file_location(title, module)
            if spec is not None:
                module_object = util.module_from_spec(spec)
                getattr(spec.loader, "exec_module")(module_object)
                callobject = module_object
                if classname is not None:
                    if len(classname) > 0:
                        classobject = getattr(module_object, classname)
                        callobject = classobject
                if len(function) > 0:
                    method_to_call = getattr(callobject, function)
                else:
                    method_to_call = classobject
                sig = inspect.signature(method_to_call)
                for key, value in sig.parameters.items():
                    if key.lower() != "self":
                        if str(value).__contains__("="):
                            val = str(value).split("=")[1].replace("\'", "").strip()
                            if val.lower() == "none":
                                val = ""
                        else:
                            if str(value).lower().__contains__("bool"):
                                val = False
                            else:
                                val = ""
                        found.set(str(key.split(":")[0]).capitalize(), str(val))
                doc = self.get_docstring_from_code(module=module, function=function, filepath=filepath,
                                                   classname=classname)
                if len(doc) == 0 and len(function) == 0:
                    doc = title
                if not doc.lower().__contains__("return: ") and str(sig.return_annotation).lower() != "<class 'bool'>":
                    if len(function) > 0:
                        del found.attrib["Output_variable"]
                    else:
                        found.set("Output_variable", f"%{classname}%")
                    if str(sig.return_annotation).lower() == "<class 'bool'>":
                        title += "?"
                        newentry.update({"label": title})
                        found.set("label", title)
                if len(function) == 0:
                    del found.attrib["Function"]
                found.set("Shape_description", doc)
                if len(classname) == 0 and len(variable) == 0:
                    del found.attrib["Class"]
                if len(variable) > 0:
                    found.set("Class", f"%{variable}%")
                xml = eltree.tostring(root.getroot()).decode('utf-8')
                xml = self.shape_encode(xml)
                root.find('.//root/object')
                newentry.update({"xml": str(xml)})
                if newentry not in dct:
                    dct.append(newentry)
                else:
                    print("already in library")
        try:
            dct.sort(key=lambda x: x["title"], reverse=False)
        except (ValueError, Exception):
            pass
        # self.save_library(filepath, dct)
        # Update dict in list
        tmp_dct.dict = [x for x in dct if len(x["xml"]) > 0]
        self.libs[idx] = tmp_dct
        self.current_dict = dct
        print(f"Shape {module} {classname} {title} added to Library {filepath}.".replace("..\\", "").replace("  ",
                                                                                                             " ").replace(
            " .", "."))

    def add_descriptions_to_flow(self, filepath: str):
        """
        Add (or update) descriptions from code to all shapes in a library.
        :param filepath: The full path to the library file.
        """
        if filepath == r"d:\runtime\prd\BPMN\flows\Monitor_24x7_Exchange.xml":
            print("")
        dct, original = self.openflow(filepath)
        graph = dct.get("mxGraphModel")
        root = graph.get("root")
        steps = root.get("object")
        try:
            if steps is not None:
                for shape in steps:
                    shapetype = shape.get("@Type")
                    classname = shape.get("@Class")
                    module = shape.get("@Module")
                    function = shape.get("@Function")
                    variable = shape.get("@Output_variable")
                    label = shape.get("@label")
                    if classname is not None:
                        if classname.startswith("%") and classname.endswith("%"):
                            module, classname = self.search_modulename_in_flow(classname, steps)
                    if function is not None or classname is not None or module is not None:
                        doc = self.get_docstring_from_code(module, function, filepath, classname)
                    else:
                        doc = None
                    if doc is None:
                        doc = ""
                    shape.update({'@Shape_description': doc})
                    # try:
                    #     shape.pop("@Description")
                    # except:
                    #     pass
                    if classname is not None:
                        if len(classname) == 0:
                            shape.pop("@Class")
                    if variable is not None:
                        if len(variable) == 0 and label.lower() != "template":
                            shape.pop("@Output_variable")
                    # found.set('tooltip', doc)
            self.saveflow(filepath, dct, original)
        except (ValueError, Exception):
            raise Exception(f"Error. Probably the file {filepath} is not a BPMN-RPA flow or the flow is incorrect.")

    @staticmethod
    def get_functions_from_module(module: str) -> Any:
        """
        Retreive the comments from code.
        :param module: The module name, including the path.
        :return: A Tuple with class and function objects.
        """
        with open(module, "r") as file:
            node = ast.parse(file.read())
        functions = [n for n in node.body if isinstance(n, ast.FunctionDef)]
        classes = [n for n in node.body if isinstance(n, ast.ClassDef)]
        return classes, functions

    def module_to_library(self, modulepath: str, libraryfolder: str):
        """
        WCreate a DrawIo library from a module. For each function in the module a Task will be created in the library.
        :param modulepath: The path of the module to create the library for.
        :param libraryfolder: The folder in which the library will be created.
        """
        modulepath = modulepath.replace("/", "\\")
        libraryfolder = libraryfolder.replace("/", "\\")
        modulename = modulepath.split("\\")[-1].lower().replace(".py", "")
        libpath = fr"{libraryfolder}\{modulename}.xml"
        if not os.path.exists(libpath):
            f = open(libpath, "w")
            f.write("<mxlibrary>[{\"xml\": \"\"}]</mxlibrary>")
            f.close()
        classes, functions = self.get_functions_from_module(modulepath)
        classname = ""
        for cls in classes:
            for fn in cls.body:
                if hasattr(fn, "name"):
                    if fn.name == "__init__":
                        self.add_shape_from_function_to_library(filepath=libpath, module=modulepath, function=fn.name,
                                                                classname=cls.name)
                        classname = cls.name
                    if not fn.name.startswith("__"):
                        self.add_shape_from_function_to_library(filepath=libpath, module=modulepath, function=fn.name,
                                                                classname=cls.name, variable=classname)
        for f in functions:
            if hasattr(f, "name"):
                if not f.name.startswith("__"):
                    self.add_shape_from_function_to_library(filepath=libpath, module=modulepath, function=f.name,
                                                            classname="")
        self.save_library()
        self.sort_library(filepath=libpath)

    @staticmethod
    def run_flow(flow_path: str, flow_input: Any = None):
        """
        Run another WorkFlow.
        :param flow_path: The full path to the flow xml file.
        :param flow_input: Optional. Any input (object or string).
        """
        flow = flow_path.lower().replace(".xml", "") + ".xml"
        if os.path.exists(flow):
            with open(flow, 'r') as f:
                content = f.read()
            if content.startswith("<mxfile "):
                engine = WorkflowEngine(input_parameter=flow_input)
                doc = engine.open(flow_path)
                steps = engine.get_flow(doc)
                engine.run_flow(steps)
            else:
                raise Exception(f'Error: flow {flow} does not contain a valid xml definition')
        else:
            raise Exception(f'Error: flow {flow} not found.')


# c = Code()
# c.libpath = r"C:\Temp\Libraries\Shapes.xml"
# c.sort_library(c.libpath)
# c.run_flow(r"c:\temp\msgbox.xml", "hey!")
# c.add_shape_from_function_to_library(module=r"C:\PythonProjects\BPMN_RPA\BPMN_RPA\Scripts\Code.py",
#                                       function="get_docstring_from_code", title="Get comments from Python code",
#                                       filepath=r"..\Shapes.xml")
# add_descriptions_to_flow(r"D:\temp\taranis_query.xml")
# c.module_to_library("C:\PythonProjects\BPMN_RPA\BPMN_RPA\Scripts\compare.py", r"c:\temp\libs")
# c.sort_library(r"c:\temp\libs\shapes.xml")
# c.save_library()
