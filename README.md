# BPMN_RPA
Robotic Process Automation in Windows by using Driagrams.net BPMN diagrams.

With this Framework you can draw Business Process Model Notation based Diagrams and run those diagrams with a WorkflowEngine.
It is based on the mxGraph model notation of https://app.diagrams.net/.

Usage:
- Create your Diagram in https://app.diagrams.net/ or in the Desktop application by using the BPMN_RPA Shape-set
- Set the right mappings for each shape
- Save your diagram as XML
- Run your workflow by using the WorkflowEngine

Example:

engine = WorkflowEngine(f"{os.getcwd()}\\Scripts\\", "c:\\python\\python.exe")<br>
doc = engine.open("test.xml")<br>
steps = engine.get_flow(doc)<br>
engine.run_flow(steps)<br>

You can download the DrawIO desktop version [here](https://github.com/jgraph/drawio-desktop/releases)