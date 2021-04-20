from BPMN_RPA.WorkflowEngine import WorkflowEngine
import os
import sys
pad = sys.argv[1]
print(pad)
input_parameter = None
if len(sys.argv) == 3:
    input_parameter = sys.argv[2]
if pad.lower().__contains__(".vsdx"):
    flow = pad.replace(".vsdx", "") + ".vsdx"
if not pad.lower().__contains__(".flw"):
    flow = pad.replace(".xml", "") + ".xml"
else:
    flow = pad
if os.name == 'nt':
    cont = os.path.exists(flow)
else:
    cont = True
if cont:
    engine = WorkflowEngine(input_parameter=input_parameter)
    doc = engine.open(fr"{flow}")
    steps = engine.get_flow(doc)
    engine.run_flow(steps)