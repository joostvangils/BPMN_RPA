# BPMN_RPA
Robotic Process Automation in Windows by using Driagrams.net BPMN diagrams.

With this Framework you can draw Business Process Model Notation based Diagrams and run those diagrams with a WorkflowEngine.
It is based on the mxGraph model notation of https://app.diagrams.net/.

### Content:
* [Quick Start](#Quick-start)
* [Allowed Shapes](#Allowed-Shapes)
* [Example](#Example)


#### Quick start
- Open the diagram.net (or DrawIO desktop) app
- Import the BPMN RPA Shapes ( file -> import from -> device)
- Create your Diagram in https://app.diagrams.net/ or in the Desktop application by using the BPMN_RPA Shape-set
- Set the right mappings for each shape
- Save your diagram as XML
- Run your workflow by using the WorkflowEngine

#### Allowed Shapes
For the Workflow engine to recognize the flow, you are restricted to use the following Shapes:

* Tasks.
    #####Mandatory
    Each Task must contain the following Data attributes:
    * Module: This is the full path to the Python file that contains your Class and/or function.
    ** From file: specify the full path (including extension .py) if you want to load you module from a specific file location.
    ** From file in Script directory: specify only the module name (including extension .py) of the module you want to use.
    ** From installed package: specify only the module name (without extension .py).
    * Class: for reference to the Class to use in the Module.
    * Function: The name of the Function to Call.
    * Mapping: The mapping of the input parameters to the output of the previous task.
    
* GateWays:
    * For now you can only use the Exclusive Gateway. This Gateway has to have a Data attribute named 'Type' with the value 'Exclusive Gateway'.
* Sequence flow arrow. If the Sequence flow arrow is originating from an Exclusive Gateway, the Sequence flow arrow must have a value of 'True' or 'False'.


#### Example

```Python
engine = WorkflowEngine("c:\\\python\\\python.exe")
doc = engine.open("test.xml")
steps = engine.get_flow(doc)
engine.run_flow(steps)
```

You can download the DrawIO desktop version [here](https://github.com/jgraph/drawio-desktop/releases)
