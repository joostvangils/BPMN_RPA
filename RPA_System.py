import os
import subprocess


class RPA_System:
    def __init__(self):
        pass

    def run_application(self, full_path: str, commandline_arguments: str = None) -> str:
        """
        Run an application.
        :param full_path: The full path to the executable (.exe file)
        :param commandline_arguments:
        :returns: OK if succeeded, an error message when the call didn't succeed
        """
        if commandline_arguments is None:
            commandline_arguments = ""
        else:
            if not commandline_arguments.startswith(" "):
                commandline_arguments = " " + commandline_arguments
        try:
            os.system(full_path + commandline_arguments)
            return "OK"
        except Exception as e:
            return e

    def shutdown_computer(self):
        os.system("shutdown /s /t 1")

    def log_off_current_user(self):
        os.system("shutdown /l /f /t 00")


sp = RPA_System()
sp.run_application(r"C:\Windows\System32\notepad.exe")