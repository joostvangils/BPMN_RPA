import base64
import importlib
import os
import urllib
import zlib
from inspect import signature
import xml.etree.ElementTree as ET
import typing
from operator import attrgetter

import win32com.client
from typing import List, Any

import xmltodict


class WorkflowEngine():

    def __init__(self, modulepath: str):
        """
        Class for automating DrawIO diagrams
        :param modulePath: Het pad naar de folder waarin de modules staan die worden uitgevoerd
        """
        self.pythonPath = "c:\\users\\jogil\\venv\\Scripts\\python.exe"
        self.modulePath = modulepath

    def open(self, name: str) -> Any:
        """
        Open a DrawIO document

        :param name: The name (including extension) of the diagram
        :returns: A DrawIO dictionary object
        """
        # Open an existing document.
        xml_file = open(name, "r")
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
        if shape.get("@source") is not None:
            retn.source = shape.get("@source")
        if shape.get("@target") is not None:
            retn.target = shape.get("@target")
            retn.type = "connector"
        if shape.get("@value") is not None:
            retn.name = shape.get("@value")
        if shape.get("@Module") is not None:
            retn.module = shape.get("@Module")
        if shape.get("@Class") is not None:
            retn.classname = shape.get("@Class")
        if shape.get("@Function") is not None:
            retn.function = shape.get("@Function")
        if shape.get("@Mapping") is not None:
            retn.mapping = shape.get("@Mapping")
        if shape.get("@label") is not None:
            retn.name = shape.get("@label")
        if shape.get("@script") is not None:
            retn.script = shape.get("@script")
        if shape.get("@class") is not None:
            retn.script = shape.get("@class")
        if shape.get("@function") is not None:
            retn.script = shape.get("@function")
        if shape.get("@source") is None and shape.get("@target") is None:
            retn.type = "shape"
            retn.IsStart = False
        return retn


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
                    spec = importlib.util.spec_from_file_location(step.module, self.modulePath + step.module)
                    module_object = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module_object)
                    if hasattr(module_object, step.classname):
                        class_object = getattr(module_object, step.classname)
                        method_to_call = getattr(class_object, step.function)
                    else:
                        method_to_call = getattr(module_object, step.function)
                    sig = signature(method_to_call)
                    if str(sig) != "()":
                        input = self.get_input_parameters(step=step, method_to_call=method_to_call, signature=sig, output_previous_step=output_previous_step)
                        output_previous_step = method_to_call(**input)
                    else:
                        output_previous_step = method_to_call()
                    previous_step = step
                    print(f"{step.classname}.{step.function} executed.")
            except Exception as e:
                pass
            step = self.get_next_step(step, steps)
            if step is None:
                break
            previous_step = step

    def get_next_step(self, current_step, steps):
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
        return [x for x in shapes if x.id == my_connector.target][0]

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

    def get_input_parameters(self, step: Any, method_to_call: Any, signature: Any, output_previous_step: Any) -> typing.Dict[str, Any]:
        """
        Fetching parameters to create a dynamic function

        :param step: The current step object
        :param method_to_call: The object of the function that must be called
        :param signature: The signature object of the function that must be called
        :param output_previous_step: The output-object of the previous step
        :returns: A dictionary that can be used as direct input for parameters in a function call
        """
        retn = {}
        if hasattr(step, "Mapping"):
            mapping = self.build_dict_from_mapping(step.mapping)
        else:
            mapping = self.build_dict_from_mapping(getattr(step, f"PythonMapping_{method_to_call.__name__}"))
        if hasattr(step, "PythonValue"):
            if len(getattr(step, "PythonValue")) > 0:
                valuestring = getattr(step, "PythonValue")
                retn[list(mapping.keys())[0]] = valuestring
                return retn
        for key, value in mapping.items():
            retn[key] = output_previous_step[value]
        return retn

    class dynamic_object(object):
        pass


# Test
we = WorkflowEngine(f"{os.getcwd()}\\Scripts\\")
doc = we.open(f"test.xml")
steps = we.get_flow(doc)
we.run_flow(steps)

