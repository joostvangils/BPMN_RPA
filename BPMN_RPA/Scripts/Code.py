import binascii
import inspect
import json
import os
import string
from importlib import util
from pathlib import Path
import xmltodict
from pyparsing import unicode
import unidecode
from BPMN_RPA.WorkflowEngine import WorkflowEngine
import sys
from lxml import etree as ET
import zlib
import base64
import urllib
from typing import List, Any


class dynamic_object(object):
    pass


def openflow(filepath: str, as_xml: bool = False) -> Any:
    """
    Open a DrawIO document
    :param filepath: The full path (including extension) of the diagram file
    :param as_xml: Optional. Returns the file content as XML.
    :returns: A DrawIO dictionary object
    """
    # Open an existing document.
    xml_file = open(filepath, "r")
    xml_root = ET.fromstring(xml_file.read())
    raw_text = xml_root[0].text
    base64_decode = base64.b64decode(raw_text)
    inflated_xml = zlib.decompress(base64_decode, -zlib.MAX_WBITS).decode("utf-8")
    url_decode = urllib.parse.unquote(inflated_xml)
    if as_xml:
        return url_decode
    retn = xmltodict.parse(url_decode)
    return retn


def get_flow(ordered_dict: Any) -> Any:
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
            step = get_step_from_shape(shape)
            if step.type == "connector":
                connectors.append(step)
            else:
                shapes.append(step)
    if not isinstance(objects, list):
        # there is only one shape
        step = get_step_from_shape(objects)
        shapes.append(step)
    else:
        for shape in objects:
            step = get_step_from_shape(shape)
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


def get_step_from_shape(shape: Any) -> Any:
    """
    Build a Step-object from the Shape-object
    :param shape: The Shape-object
    :returns: A Step-object
    """
    retn = dynamic_object()
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


def check_flow_for_usage(flow: str, search_module: str = "", search_class: str = "", search_function: str = "") -> List:
    """
    Check if the given code is used in the steps of a flow.
    :param flow: The path to the file of the flow.
    :param search_module: Optional. The full path of the module to search.
    :param search_class: Optional. The classname to search.
    :param search_function: Optional. The function name to search.
    :return: A list of explenations in which step the code is used.
    """
    doc = openflow(flow)
    flowname = flow.split("\\")[-1]
    steps = get_flow(doc)
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
    for c in hasclass:
        retn.append(f"Class \"{search_class}\" is used in step \"{c}\" of flow \"{flowname}\".")
    for m in hasmodule:
        retn.append(f"Module \"{search_module}\" is used in step \"{m}\" of flow \"{flowname}\".")
    for f in hasfunction:
        retn.append(f"Function \"{search_function}\" is used in step \"{f}\" of flow \"{flowname}\".")
    return retn

def get_library(filepath: str) -> Any:
    """
    Read a library file and return its content.
    :param filepath: The full path of the library to read.
    :return: The library content.
    """
    # Open an existing document.
    xml_file = open(filepath, "r")
    xml_root = ET.fromstring(xml_file.read())
    raw_text = xml_root.text
    # base64_decode = base64.b64decode(raw_text)
    # inflated_xml = zlib.decompress(base64_decode, -zlib.MAX_WBITS).decode("utf-8")
    # url_decode = urllib.parse.unquote(inflated_xml)
    retn = json.loads(xml_root.text)
    return retn


def save_library(filepath: str, dct: Any):
    """
    Save a library to a file.
    :param filepath: The full path to save the library to.
    :param dct: The content of the library (the list of dictionaries).
    """
    try:
        dct.sort(key=lambda x: x["title"], reverse=False)
    except:
        pass
    content = "<mxlibrary>" + json.dumps(dct) + "</mxlibrary>"
    # Open an existing document.
    xml_file = open(filepath, "w")
    xml_file.write(content)
    xml_file.close()


def shape_decode(shape: Any):
    """
    Decode the content of a shape to xml.
    :param shape: The shape to decode the content of.
    :return: Decoded xml of the shape.
    """
    original = shape.get("xml")
    base64_decode = base64.b64decode(shape.get("xml"))
    inflated_xml = zlib.decompress(base64_decode, -zlib.MAX_WBITS).decode("utf-8")
    retn = urllib.parse.unquote(inflated_xml)
    # test = shape_encode(retn)
    # if test != original:
    #     print(original)
    #     print(test)
    #     print("Err")
    return retn


def shape_encode(shape_xml: str) -> str:
    """
    Encode the xml of a shape.
    :param shape_xml: The xml to encode.
    :return: Encoded xml.
    """
    retn = urllib.parse.quote(shape_xml).replace("/", "%2F")
    retn = zlib.compress(retn.encode('unicode_escape'))
    retn = retn[2:]
    retn = base64.b64encode(retn).decode('utf-8')
    # print(retn)
    return retn


def add_comments_to_library(filepath: str):
    """
    Add (or update) comments  to all shapes in a library.
    :param filepath: The full path to the library file.
    """
    dct = get_library(filepath)
    fileupdate = False
    for shape in dct:
        updated = False
        xml = shape_decode(shape)
        oldxml = xml
        root = ET.ElementTree(ET.fromstring(xml))
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
            doc = get_docstring_from_code(module, function, filepath, classname)
            if doc is None: doc = ""
            found.set('Description', doc)
            if classname is not None:
                if len(classname) == 0:
                    del found.attrib["Class"]
            if mapping is not None:
                if len(mapping) == 0:
                    del found.attrib["Mapping"]
            if variable is not None:
                if len(variable) == 0 and label.lower() != "template":
                    del found.attrib["Output_variable"]
            #found.set('tooltip', doc)
            xml = ET.tostring(root.getroot()).decode('utf-8')
            xml = shape_encode(xml)
            root.find('.//root/object')
            shape.update({"xml": str(xml)})
    save_library(filepath, dct)

def library_has_shape(filepath: str, module: str, function: str, classname: str = "") -> bool:
    dct = get_library(filepath)
    retn = False
    for shape in dct:
        updated = False
        xml = shape_decode(shape)
        oldxml = xml
        root = ET.ElementTree(ET.fromstring(xml))
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
            if module_.lower() == module.lower() and classname_.lower() == classname.lower() and function_.lower() == function.lower():
                retn = True
                break
    return retn

def get_docstring_from_code(module: str, function: str, filepath: str, classname: str = "") -> str:
    """
    Retreive the comments from code.
    :param module: The module name, including the path.
    :param function: The function name.
    :param filepath: The full path of the library file.
    :param classname: Optional. The Classname.
    :return: A string with the comments from code.
    """

    doc = None
    callobject = None
    method_to_call = None
    if module is None and len(classname) ==0:
        module = str("\\".join(sys.executable.split("\\")[:-1])) + r"\Lib\site-packages\BPMN_RPA\WorkflowEngine.py"
        classname = "WorkflowEngine"
    if module is not None:
        if len(module) ==0 and len(classname) ==0:
            module =  str("\\".join(sys.executable.split("\\")[:-1])) + r"\Lib\site-packages\BPMN_RPA\WorkflowEngine.py"
            classname = "WorkflowEngine"
    if classname is not None:
        if classname.startswith("%") and classname.endswith("%"):
            if module is not None:
                if not module.startswith("%") and not module.endswith("%"):
                    classname = module.split("\\")[-1].replace(".py", "")
            else:
                module, classname = get_module_from_variable_name(classname, filepath)
    if not module.endswith(".py"):
        path = "\\".join(sys.executable.split("\\")[:-1]) + "\\Lib\\"
        if os.path.exists(path + module + ".py"):
            module = path + module + ".py"
    else:
        path = "\\".join(sys.executable.split("\\")[:-1]) + "\\Lib\\site-packages\\BPMN_RPA\\Scripts\\" + module
        if os.path.exists(path):
            module = path
    spec = util.spec_from_file_location(module, module)
    if spec is not None:
        module_object = util.module_from_spec(spec)
        spec.loader.exec_module(module_object)
        callobject = module_object
        if classname is not None:
            if len(classname)>0:
                classobject = getattr(module_object, classname)
                callobject = classobject
    if function is not None:
        if len(function) > 0:
            method_to_call = getattr(callobject, function)
    else:
        method_to_call = getattr(classobject, "__init__")
    doc = inspect.getdoc(method_to_call)
    if doc is not None:
        doc = doc.replace(":param ", "\n").replace(":return: ", "\nReturn: ").replace(":returns: ", "\nReturn: ")
    return doc


def sort_library(filepath: str) -> Any:
    """
    Sort a DrawIo library of shapes.
    :param filepath: The path to the library file.
    :return: The sorted library as a list of dictionaries.
    """
    dct = get_library(filepath)
    dct.sort(key=lambda x: x["title"], reverse=False)
    return dct


def get_module_from_variable_name(variable: str, filepath: str)-> Any:
    """
    Get the module path from a variable name.
    :param variable: The name of the variable.
    :param filepath: The full path of the library file.
    :return: Tuple: The full path of the module and the classname.
    """
    dct = get_library(filepath)
    for shape in dct:
        xml = shape_decode(shape)
        root = ET.ElementTree(ET.fromstring(xml))
        found = root.find('.//root/object')
        if found is not None:
            fields = found.attrib
            classname = fields.get("Class")
            module = fields.get("Module")
            function = fields.get("Function")
            mapping = fields.get("Mapping")
            output_variable = fields.get("Output_variable")
            if output_variable == variable:
                return module, classname
    return None

def add_shape_from_function_to_library(filepath: str, module: str, function: str, classname: str = "", title: str = ""):
    """
    Create a shape from code and add it to a shape library.
    :param filepath: The path to the library file.
    :param module: The full path of the module.
    :param function: The name of the function.
    :param classname: The class name.
    :param title: The title of the new created shape in the library.
    """
    if library_has_shape(filepath, module, function, classname):
        print(f"Library {filepath} already has a shape for {module} {classname} {function}.".replace("  ", " ").replace(" .", "."))
        return
    dct = get_library(filepath)
    if len(title) == 0:
        title = function.capitalize().replace("_", " ")
    newentry = {'xml':'', 'w': 120, 'h': 80, 'aspect': 'fixed', 'title': title}
    newshape = f"<mxGraphModel><root><mxCell id=\"0\"/><mxCell id=\"1\" parent=\"0\"/><object label=\"{title}\" Module=\"{module}\" Class=\"{classname}\" Function=\"{function}\" Output_variable=\"\" id=\"2\" Description=\"\"><mxCell style=\"shape=ext;rounded=1;html=1;whiteSpace=wrap;\" vertex=\"1\" parent=\"1\"><mxGeometry width=\"120\" height=\"80\" as=\"geometry\"/></mxCell></object></root></mxGraphModel>"
    root = ET.ElementTree(ET.fromstring(newshape))
    found = root.find('.//root/object')
    if module is None:
        module = str(Path(os.getcwd()).parent) + r"\WorkflowEngine.py"
        classname = "WorkflowEngine"
    if len(module) ==0:
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
        if len(function) > 0:
            spec = util.spec_from_file_location(title, module)
            if spec is not None:
                module_object = util.module_from_spec(spec)
                spec.loader.exec_module(module_object)
                callobject = module_object
                if classname is not None:
                    if len(classname)>0:
                        classobject = getattr(module_object, classname)
                        callobject = classobject
                method_to_call = getattr(callobject, function)
                sig = inspect.signature(method_to_call)
                xml = {}
                for key, value in sig.parameters.items():
                    if str(value).__contains__("="):
                        val = str(value).split("=")[1].replace("\'", "").strip()
                    else:
                        if str(value).lower().__contains__("bool"):
                            val = False
                        else:
                            val = ""
                    found.set(str(key.split(":")[0]).capitalize(), str(val))
                doc = get_docstring_from_code(module, function, classname)
                if not doc.__contains__("Return: "):
                    del found.attrib["Output_variable"]
                found.set("Description", doc)
                if len(classname) == 0:
                    del found.attrib["Class"]
                xml = ET.tostring(root.getroot()).decode('utf-8')
                xml = shape_encode(xml)
                root.find('.//root/object')
                newentry.update({"xml": str(xml)})
                dct.append(newentry)
    dct.sort(key=lambda x: x["title"], reverse=False)
    save_library(filepath, dct)
    print(f"Shape {module} {classname} {title} added to Library {filepath}.".replace("..\\", "").replace("  ", " ").replace(" .", "."))



#add_shape_from_function_to_library(module=r"C:\PythonProjects\BPMN_RPA\BPMN_RPA\Scripts\Code.py", function="get_docstring_from_code", title="Get comments from Python code", filepath=r"..\Shapes.xml")
#add_comments_to_library(r"..\Shapes.xml")
