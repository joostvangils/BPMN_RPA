import os
import sys

import dill as pickle
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
#
# BPMN-RPA CheckListEngine uses the dill library, which is licensed under the BSD License (BSD-3-Clause).
# Copyright Mike McKerns. Further reading:
# M.M. McKerns, L. Strand, T. Sullivan, A. Fang, M.A.G. Aivazis,
# "Building a framework for predictive science", Proceedings of
# the 10th Python in Science Conference, 2011;
# http://arxiv.org/pdf/1202.1056
# Michael McKerns and Michael Aivazis,
# "pathos: a framework for heterogeneous computing", 2010- ;
# https://uqfoundation.github.io/project/pathos
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


class ChecklistEngine:
    def __init__(self, flow_name="", full_path_save_as="", input_parameter="", save_images_in_folder: str = ""):
        """
        This Engine will start the flow and will svae the state of the flow after each step by pickeling the flow object.
        A Checklist can run multiple copies of the original flow. Therefore you must give each instance a separate name.
        :param flow_name: The full path of the flow to run, including the file name and extension. This may be the original flow (.flw) file when you are starting a first run of a new instance, or the full path to the instance of the flow with the saved state.
        :param input_parameter: The input parameter for the flow.
        :param full_path_save_as: The full path to save the flow instance to. This is used to save the state of the flow after each step. You can save the flow with another name than the original flow to create separate instances of the flow. It is advised to set this parameter when you are starting a new instance of the flow.
        :param save_images_in_folder: The path to the folder where the images of the flow will be saved. If this parameter is empty, the images will be saved in the same folder as the instance.
        """
        self.flow_name = flow_name
        self.save_as = full_path_save_as
        self.outputPreviousStep = None
        self.PreviousStep = None
        self.step = None
        self.save_images_in_folder = save_images_in_folder
        if full_path_save_as == "":
            self.save_as = flow_name.replace(".flw", "_running_instance")
        # Check if file exists. If not, throw exception
        if not os.path.exists(self.flow_name) and self.flow_name != "":
            raise FileNotFoundError(f"The flow file does not exist!")
        try:
            self.engine = WorkflowEngine(input_parameter=input_parameter)
            doc = self.engine.open(fr"{self.flow_name}")
            self.engine.doc = doc
            self.steps = self.engine.get_flow(doc)
            if self.save_as != "":
                self.flow_name = self.save_as
        except Exception as e:
            try:
                self.load_flow_state(flow_name)
            except Exception as e:
                try:
                    self.load_flow_state(full_path_save_as)
                    if self.save_as != "":
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
        if self.engine.current_step is None:
            for stp in self.steps:
                if hasattr(stp, "IsStart"):
                    if stp.IsStart:
                        self.step = stp
                    break
        if self.step is None:
            self.PreviousStep = self.step
            self.step = self.engine.get_next_step(self.engine.current_step, self.steps, self.outputPreviousStep)
        try:
            if self.engine.db is None:
                db_path = self.engine.get_db_path()
                self.engine.db = SQL(db_path)
        except Exception as e:
            pass
        if ask_permission and getattr(self.step, "IsStart") == False and not (
                "gateway" in str(getattr(self.step, "type").lower())) and str(
            getattr(self.step, "shape_description").lower()) != "end event.":
            if not self.ask_permission_for_next_step(msgbox=msgbox):
                sys.exit(0)
        if hasattr(self.step, "shape_description"):
            if getattr(self.step, "shape_description") == "End event.":
                self.outputPreviousStep = self.engine.run_flow(self.step, True)
                try:
                    os.remove(self.flow_name)
                except:
                    pass
                try:
                    os.remove(self.flow_name + "_diagram.png")
                except:
                    pass
                self.engine.print_log(f"Flow finished, instance '{self.flow_name}' removed.")
                print(f"Flow finished, instance '{self.flow_name}' removed.")
                # try to remove png file
                try:
                    os.remove(f"{self.flow_name.split('.')[0]}.png")
                except Exception as e:
                    pass
                sys.exit(0)
        try:
            tmp = self.outputPreviousStep  # Needed for gateway
            self.outputPreviousStep = self.engine.run_flow(self.step, True)
            if self.outputPreviousStep is None:
                self.outputPreviousStep = tmp  # When gateway
            self.step = self.engine.get_next_step(self.step, self.steps, self.outputPreviousStep)
            if self.step is None:
                os.remove(self.save_as)
                self.engine.print_log(f"Flow finished, instance '{self.flow_name}' removed.")
                print(f"Flow finished, instance '{self.flow_name}' removed.")
                sys.exit(0)
            self.save_flow_state()

        except Exception as e:
            print(e)
            self.save_flow_state()
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
        pickle.settings['recurse'] = True
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
                sys.exit(0)

    def run_flow(self, ask_permission=False, msgbox=True):
        """
        This function will resume the flow from the last saved state.
        :param ask_permission: If True, the user will be asked to click the OK button to continue to the next step.
        :param msgbox: If this is True and ask_permission is True, a message box will be shown to the user to click OK to continue to the next step. Otherwise, the user will be asked to enter Yes (y) or No (n) in the console.
        """
        while True:
            if not self.run_next_step(ask_permission=ask_permission, msgbox=msgbox):
                sys.exit(0)

    def ask_permission_for_next_step(self, msgbox=True):
        """
        This function will ask the user for permission to run the next step. If the user does not have permission, the flow will be saved and the program will exit.
        :param msgbox: If True, a messagebox will be shown to the user. If False, the user will be asked to enter Yes (y) or No (n) in the console.
        """
        instance_name = os.path.basename(self.flow_name).split(".")[0]
        if self.save_images_in_folder != "":
            folder = self.save_images_in_folder
        else:
            folder = self.flow_name.replace(os.path.basename(self.flow_name), "")
        if msgbox:
            # Show messagebox
            import BPMN_RPA.Scripts.MessageBox as mb
            result = mb.messagebox_show_with_yes_no_buttons(f"Continue with next step?",
                                                            f"Do you want to execute the '{self.step.name}' step of flow '{instance_name}'?")
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
            self.create_flow_diagram(folder)
            print(f"Flow state saved: {self.flow_name}")
            print("Program exited.")
            sys.exit()

    def create_flow_diagram(self, folder=""):
        """
        This function will create a diagram of the flow.
        :param folder: The folder to save the diagram to.
        """
        steps = self.steps
        # get start step
        step = None
        for stp in self.steps:
            if hasattr(stp, "IsStart"):
                if stp.IsStart:
                    step = stp
                break
        import graphviz
        if os.name == 'nt':
            if not folder.endswith("\\"):
                folder += "\\"
            name = os.path.basename(self.flow_name).split('\\')[-1].split('.')[0]
        else:
            if not folder.endswith("/"):
                folder += "/"
            name = os.path.basename(self.save_as).split('/')[-1].split('.')[0]
        if name == "":
            name = os.path.basename(self.flow_name).split('/')[-1].split('.')[0]
        if self.save_as == "":
            self.save_as = self.flow_name
        e = graphviz.Graph('G', filename=folder + name, engine='dot', format='png')
        e.attr('node', shape='ellipse', id=step.id, bordercolor="black", borderwidth="1", fontname="Arial",
               fontsize="10")
        e.node(name=step.id, label='Start')
        step = steps[0]
        ctr = 1
        current_step = self.engine.get_next_step(self.engine.current_step, self.steps, "")
        while True:
            step = steps[ctr]
            if (str(getattr(step, "type")).lower() == "shape" or (
                    "gateway" in str(getattr(step, "type")).lower())) and hasattr(step, "shape_description"):
                if str(getattr(step, "shape_description").lower()) != "end event.":
                    if str(getattr(step, "shape_description").lower()) == "exclusive gateway.":
                        e.node(name=step.id, label="X", shape='diamond', id=step.id, style="filled", color="lightgrey",
                               bold="true", fontname="Arial", fontsize="10")
                    else:
                        if str(getattr(step, "shape_description").lower()) == "parallel gateway.":
                            e.node(name=step.id, label="+", shape='diamond', id=step.id, style="filled",
                                   color="lightgrey", bold="true", fontname="Arial", fontsize="10")
                        else:
                            if step == current_step:
                                e.node(name=step.id, label=step.name, shape='box', id=step.id, style="filled",
                                       color="black", bordercolor="black", borderwidth="1", fillcolor="#4A6648",
                                       fontname="Arial", fontsize="10", fontcolor="white")
                            else:
                                e.node(name=step.id, label=step.name, shape='box', id=step.id, style="", color="black",
                                       bordercolor="black", borderwidth="1", fillcolor="white", fontname="Arial",
                                       fontsize="10")
                else:
                    e.node(name=step.id, label='End', shape='ellipse', border='2', id=step.id, style="",
                           fillcolor="white", color="black", bordercolor="black", borderwidth="1", fontname="Arial",
                           fontsize="10")
            ctr += 1
            if ctr >= len(steps):
                break
        for step in steps:
            if hasattr(step, "type"):
                if str(step.type) == "connector":
                    if hasattr(step, "value"):
                        e.edge(step.source, step.target, dir="forward", arrowhead='normal', arrowsize='0.5',
                               label=step.value, fontname="Arial", fontsize="10")
                    else:
                        e.edge(step.source, step.target, dir="forward", arrowhead='normal', arrowsize='0.5',
                               fontname="Arial", fontsize="10")
        print(f"Flow diagram saved: {folder + name}_diagram.png")
        e.render(filename=f"{folder + name}_diagram", view=False, cleanup=True)