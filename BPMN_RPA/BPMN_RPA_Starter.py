from BPMN_RPA.WorkflowEngine import WorkflowEngine
import os
import sys
pad = sys.argv[1]
print(pad)
input_parameter = None
if len(sys.argv) == 3:
    input_parameter = sys.argv[2]
if pad.__contains__(".vsdx"):
    flow = pad.replace(".vsdx", "") + ".vsdx"
else:
    flow = pad.replace(".xml", "") + ".xml"
if os.name == 'nt':
    cont = os.path.exists(flow)
else:
    cont = True
if cont:
    engine = WorkflowEngine(input_parameter=input_parameter)
    doc = engine.open(fr"{flow}")
    steps = engine.get_flow(doc)
    engine.run_flow(steps)