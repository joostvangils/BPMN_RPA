from BPMN_RPA.WorkflowEngine import WorkflowEngine
import os
import sys
if len(sys.argv) != 2:
    print(f'Error: Unexpected number of arguments given.')
    exit(-1)

pad = sys.argv[1]
print(pad)
flow = pad.lower().replace(".xml", "") + ".xml"
if os.path.exists(flow):
    with open(flow,'r') as f:
        inhoud=f.read()
    if inhoud.startswith("<mxfile "):
        engine = WorkflowEngine()
        doc = engine.open(pad)
        steps = engine.get_flow(doc)
        engine.run_flow(steps)
    else:
        raise Exception(f'Error: flow {flow} does not contain a valid xml definition')
else:
    raise Exception(f'Error: flow {flow} not found.')