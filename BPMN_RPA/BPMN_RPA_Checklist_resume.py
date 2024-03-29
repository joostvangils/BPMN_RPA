import sys

from werkzeug.utils import secure_filename

# The BPMN-RPA Checklist resume module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# The BPMN-RPA Checklist resume module is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from BPMN_RPA.CheckListEngine import ChecklistEngine

try:
    # Sanitize input and allow only secure filenames
    flow = secure_filename(sys.argv[1])
except:
    raise Exception("Please provide a path to the flow as argument")
chkLst = ChecklistEngine()
chkLst.resume_flow(flow_path=flow, ask_permission=True, msgbox=True)
