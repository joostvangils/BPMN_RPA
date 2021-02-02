from BPMN_RPA.WorkflowEngine import WorkflowEngine
import os
import sys
pad = sys.argv[1]
input_parameter = None
if len(sys.argv) == 3:
    input_parameter = sys.argv[2]
if pad.lower().__contains__(".vsdx"):
    flow = pad.lower().replace(".vsdx", "") + ".vsdx"
else:
    flow = pad.lower().replace(".xml", "") + ".xml"
if os.path.exists(flow):
    engine = WorkflowEngine(input_parameter=input_parameter)
    doc = engine.open(fr"{flow}")
    steps = engine.get_flow(doc)
    engine.run_flow(steps)
else:
    raise Exception(f'Error: flow {flow} not found.')