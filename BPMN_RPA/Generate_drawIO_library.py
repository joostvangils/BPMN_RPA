import sys
from BPMN_RPA.Scripts.Code import Code
cod = Code()
# get first commandline argument
mod = sys.argv[1]
fldr = sys.argv[2]
cod.module_to_library(modulepath=mod, libraryfolder=fldr)
