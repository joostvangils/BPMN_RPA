import sys

from BPMN_RPA.CheckListEngine import ChecklistEngine
# The BPMN-RPA Checklist start module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# The BPMN-RPA Checklist start module is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# Start a flow instance
try:
    name = sys.argv[1]
    path = sys.argv[2]
except:
    raise Exception("Please provide a name and a path to the flow as arguments")
chkLst = ChecklistEngine(flow_name=name, full_path_save_as=path)
chkLst.run_flow(ask_permission=True, msgbox=True)
