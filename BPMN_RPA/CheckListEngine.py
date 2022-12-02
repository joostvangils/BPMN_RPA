import os
import pickle

from BPMN_RPA.WorkflowEngine import WorkflowEngine, SQL

# The BPMN-RPA CheckListEngine is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# The BPMN-RPA CheckListEngine is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# Copyright 2020-2021 Joost van Gils (J.W.N.M. van Gils)


class ChecklistEngine:
    def __init__(self, flow_name="", full_path_save_as="", input_parameter=""):
        """
        This Engine will start the flow and will svae the state of the flow after each step by pickeling the flow object.
        A Checklist can run multiple copies of the original flow. Therefore you must give each instance a separate name.
        :param flow_name: The full path of the flow to run, including the file name and extension. This may be the original flow (.flw) file when you are starting a first run of a new instance, or the full path to the instance of the flow with the saved state.
        :param input_parameter: The input parameter for the flow.
        :param full_path_save_as: The full path to save the flow instance to. This is used to save the state of the flow after each step. You can save the flow with another name than the original flow to create separate instances of the flow. It is advised to set this parameter when you are starting a new instance of the flow.
        """
        self.flow_name = flow_name
        self.save_as = full_path_save_as
        # Check if file exists. If not, throw exception
        if not os.path.exists(self.flow_name) and self.flow_name != "":
            raise FileNotFoundError(f"The flow file does not exist!")
        try:
            self.engine = WorkflowEngine(input_parameter=input_parameter)
            doc = self.engine.open(fr"{self.flow_name}")
            self.engine.doc = doc
            self.steps = self.engine.get_flow(doc)
            self.flow_name = self.save_as
        except Exception as e:
            try:
                self.load_flow_state(flow_name)
            except Exception as e:
                try:
                    self.load_flow_state(full_path_save_as)
                    self.flow_name = self.save_as
                except Exception as e:
                    pass

    def run_next_step(self, ask_permission=False, msgbox=True):
        """
        Loop the steps and save after each step.
        :param steps: The steps to run
        :param ask_permission: If True, the user will be asked to click the OK button to continue to the next step.
        :param msgbox: If this is True and ask_permission is True, a message box will be shown to the user to click OK to continue to the next step. Otherwise, the user will be asked to enter Yes (y) or No (n) in the console.
        :return: True or False
        """
        outputPreviousStep = None
        step = self.steps[self.engine.step_nr]
        if hasattr(step, "shape_description"):
            if getattr(step, "shape_description") == "End event.":
                os.remove(self.flow_name)
                self.engine.print_log(f"Flow finished, instance '{self.flow_name}' removed.")
                print(f"Flow finished, instance '{self.flow_name}' removed.")
                exit(0)
        try:
            if self.engine.db is None:
                db_path = self.engine.get_db_path()
                self.engine.db = SQL(db_path)
            tmp = outputPreviousStep  # Needed for gateway
            outputPreviousStep = self.engine.run_flow(step, True)
            if outputPreviousStep is None:
                outputPreviousStep = tmp  # When gateway
            step = self.engine.get_next_step(step, self.steps, outputPreviousStep)
            if step is None:
                os.remove(self.flow_name)
                self.engine.print_log(f"Flow finished, instance '{self.flow_name}' removed.")
                print(f"Flow finished, instance '{self.flow_name}' removed.")
                exit(0)
            self.save_flow_state()
            if ask_permission and not getattr(step, "IsStart") and not ("gateway" in str(getattr(step, "type"))):
                if not self.ask_permission_for_next_step(msgbox=msgbox):
                    exit(0)
        except Exception as e:
            pass
        return True

    def save_flow_state(self, full_path_to_save_to=""):
        """
        This function will save the state of the flow to a pickle file
        :param flow: The flow to save
        :param full_path_to_save_to: The full path to save the instance of the flow to.
        """
        if full_path_to_save_to != "":
            self.save_as = full_path_to_save_to
        if not self.save_as:
            flw = self.flow_name.replace(".flw", "")
        else:
            flw = self.save_as
        self.engine.db = None
        with open(f"{flw}", "wb") as f:
            pickle.dump(self.engine, f)

    def load_flow_state(self, flow_path=None):
        """
        This function will load the state of the flow from a pickle file
        :param flow_path: The full path of the flow to load
        """
        if flow_path:
            flw = flow_path
        else:
            if not self.save_as:
                flw = self.flow_name.replace(".flw", "")
            else:
                flw = self.save_as
        if flw == "":
            raise Exception("The path of the flow to load is empty!")
        with open(f"{flw}", "rb") as f:
            self.engine = pickle.load(f)
        db_path = self.engine.get_db_path()
        self.engine.db = SQL(db_path)
        self.flow_name = flw
        self.steps = self.engine.get_flow(self.engine.doc)

    def resume_flow(self, flow_path, ask_permission=False, msgbox=True):
        """
        This function will resume the flow from the last saved state.
        :param flow_path: The full path of the flow instance to resume
        :param ask_permission: If True, the user will be asked to click the OK button to continue to the next step.
        :param msgbox: If this is True and ask_permission is True, a message box will be shown to the user to click OK to continue to the next step. Otherwise, the user will be asked to enter Yes (y) or No (n) in the console.
        """
        self.load_flow_state(flow_path)
        while True:
            if not self.run_next_step(ask_permission=ask_permission, msgbox=msgbox):
                exit(0)

    def run_flow(self, ask_permission=False, msgbox=True):
        """
        This function will resume the flow from the last saved state.
        :param ask_permission: If True, the user will be asked to click the OK button to continue to the next step.
        :param msgbox: If this is True and ask_permission is True, a message box will be shown to the user to click OK to continue to the next step. Otherwise, the user will be asked to enter Yes (y) or No (n) in the console.
        """
        while True:
            if not self.run_next_step(ask_permission=ask_permission, msgbox=msgbox):
                exit(0)

    def ask_permission_for_next_step(self, msgbox=True):
        """
        This function will ask the user for permission to run the next step. If the user does not have permission, the flow will be saved and the program will exit.
        :param msgbox: If True, a messagebox will be shown to the user. If False, the user will be asked to enter Yes (y) or No (n) in the console.
        """
        instance_name = self.flow_name.split("\\")[-1].split(".")[0]
        if msgbox:
            # Show messagebox
            import BPMN_RPA.Scripts.MessageBox as mb
            result = mb.messagebox_show_with_yes_no_buttons(f"Continue with next step?", f"Do you want to execute the next step of flow '{instance_name}'?")
        else:
            # Show console
            result = input(f"Do you want to execute the next step of flow '{instance_name}'? (y/n) ")
            if result.lower() == "y":
                result = True
            else:
                result = False
        if result:
            return True
        else:
            self.save_flow_state()
            print(f"Flow state saved: {self.flow_name}")
            print("Program exited.")
            exit()
