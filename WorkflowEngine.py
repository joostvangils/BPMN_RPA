import importlib
import os
from inspect import signature

import typing
import win32com.client
from typing import List, Any


class Visio():

    def __init__(self, modulepath: str, visible: bool = True):
        """
        Klasse voor automatiseren van Visio

        :param visible: Optioneel. Indicator of de applicatie Visio zichtbaar moet worden geopend.
        :param modulePath: Het pad naar de folder waarin de modules staan die worden uitgevoerd
        """
        self.pythonPath = "c:\\users\\jogil\\venv\\Scripts\\python.exe"
        self.modulePath = modulepath
        self.visio = win32com.client.Dispatch("Visio.Application")
        self.visio.Visible = visible

    def Open(self, name: str) -> Any:
        """
        Openen van een Visio document

        :param name: Het volledige pad inclusief extensie van het te openen document
        :returns: Een Visio document object
        """
        # Open an existing document.
        doc = self.visio.Documents.Open(name)
        return doc

    def GetFlow(self, doc) -> Any:
        """
        Ophalen van de elementen van de flow in het Document.

        :param doc: Het visio document object dat de flow elementen bevat.
        :returns: Een array van flow elementen
        """
        retn = []
        for shape in doc.Pages.Item(1).Shapes:
            retn.append(self.GetStepFromShape(shape))
        return retn

    def GetStepFromShape(self, shape):
        """
        Maakt een Step-object van het Shape-object

        :param shape: Het Shape-object waarvan een Step-object moet worden gemaakt
        :returns: Een Step-object
        """
        retn = self.dynamic_object()
        row = 0
        while True:
            if shape.CellsSRCExists(243, row, 0, 0):
                setattr(retn, str(shape.CellsSRC(243, row, 0).name).replace("Prop.", ""), str(shape.CellsSRC(243, row, 0).formula).replace('"', ''))
                row += 1
            else:
                break
        return retn

    def RunFlow(self, steps):
        """
        Voert een Flow uit.

        :params staps: De lijst met Steps die moeten worden uitgevoerd
        """
        previous_step = None
        output_previous_step = None
        for st in steps:
            input = []
            try:
                # to fetch module
                if hasattr(st, "PythonModule"):
                    spec = importlib.util.spec_from_file_location(st.PythonModule, self.modulePath + st.PythonModule)
                    module_object = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module_object)
                    if hasattr(module_object, st.PythonClass):
                        class_object = getattr(module_object, st.PythonClass)
                        method_to_call = getattr(class_object, st.PythonFunction)
                    else:
                        method_to_call = getattr(module_object, st.PythonFunction)
                    sig = signature(method_to_call)
                    if str(sig) != "()":
                        input = self.getInputParameters(step=st, method_to_call=method_to_call, signature=sig, output_previous_step=output_previous_step)
                        output_previous_step = method_to_call(**input)
                    else:
                        output_previous_step = method_to_call()
                    previous_step = st
                    print(f"{st.PythonClass}.{st.PythonFunction} executed.")
            except Exception as e:
                pass
            previous_step = st

    def buildDictFromMapping(self, mapping: str) -> typing.Dict[str, str]:
        """
        Maak een dictionary van de mapping string

        :param mapping: De mapping string waarvan een dictionary moet worden gemaakt
        :returns: Een dictionary
        """
        retn = {}
        for map in mapping.split(";"):
            retn[map.split("=")[0].strip()] = map.split("=")[1].strip()
        return retn

    def getInputParameters(self, step: Any, method_to_call: Any, signature: Any, output_previous_step: Any) -> typing.Dict[str, Any]:
        """
        Ophalen van de parameters om een functie dynamisch te kunnen aanroepen

        :param step: Het step-object van de huidige stap
        :param method_to_call: Het object van de functie die wordt aangeroepen
        :param signature: Het signature object van de functie die wordt aangeroepen
        :param output_previous_step: Het door de vorige stap doorgegeven object
        :returns: Een dictionary die direct in de functieaanroep als parameters kunnen worden meegegeven
        """
        retn = {}
        if hasattr(step, "PythonMapping_All"):
            mapping = self.buildDictFromMapping(getattr(step, "PythonMapping_All"))
        else:
            mapping = self.buildDictFromMapping(getattr(step, f"PythonMapping_{method_to_call.__name__}"))
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


# visio = Visio("c:\\tmp\\", True)
# doc = visio.Open(r"C:\Users\jogil\Desktop\BPMN\hello_world.vsdx")
# steps = visio.GetFlow(doc)
# visio.RunFlow(steps)
# print("OK")
