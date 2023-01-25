from werkzeug.utils import secure_filename

from BPMN_RPA.WorkflowEngine import WorkflowEngine
import os
import sys
pad = secure_filename(sys.argv[1])
print(pad)
input_parameter = None
if len(sys.argv) == 3:
    # make sure that the input parameter is a string
    input_parameter = str(sys.argv[2])
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
    doc = engine.open(filepath=flow)
    steps = engine.get_flow(doc)
    engine.run_flow(steps)