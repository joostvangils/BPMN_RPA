# BPMN_RPA
Robotic Process Automation by using Driagrams.net BPMN diagrams.

With this Framework you can draw Business Process Model Notation based Diagrams and run those diagrams with a WorkflowEngine.
It is based on the mxGraph model notation of https://app.diagrams.net/.

Usage:
- Create your Diagram in https://app.diagrams.net/ or in the Desktop application by using the BPMN_RPA Shape-set
- Set the right mappings for each shape
- Save your diagram as XML
- Run your workflow by using the WorkflowEngine

Example:

engine = WorkflowEngine(f"{os.getcwd()}\\Scripts\\", "c:\\python\\python.exe")
doc = engine.open("test.xml")
steps = engine.get_flow(doc)
engine.run_flow(steps)

You can download the DrawIO desktop version [here](https://github.com/jgraph/drawio-desktop/releases)