import os

class RPA_System:

    def __init__(self):
        pass

    def run_application(self, fullpath: str, commandline_arguments: str) -> str:
        try:
            if len(commandline_arguments) > 0:
                commandline_arguments = " " + commandline_arguments
            os.startfile(fullpath)
            return "OK"
        except Exception as e:
            return e


