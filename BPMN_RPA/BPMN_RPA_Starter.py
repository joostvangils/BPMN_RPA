from BPMN_RPA.WorkflowEngine import WorkflowEngine
import os
import sys
pad = sys.argv[1]
input_parameter = None
if len(sys.argv) == 3:
    input_parameter = sys.argv[2]
flow = pad.lower().replace(".xml", "") + ".xml"
if os.path.exists(flow):
    with open(flow, 'r') as f:
        content = f.read()
    if content.startswith("<mxfile "):
        engine = WorkflowEngine(input_parameter=input_parameter)
        doc = engine.open(fr"{flow}")
        steps = engine.get_flow(doc)
        engine.run_flow(steps)
    else:
        raise Exception(f'Error: flow {flow} does not contain a valid xml definition')
else:
    raise Exception(f'Error: flow {flow} not found.')