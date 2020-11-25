import winreg

from BPMN_RPA.WorkflowEngine import SQL

class triggers():

    def __init__(self):
        self.set_window_trigger()
        self.db = SQL(self.get_dbPath())
        self.cursor = self.db.connection.cursor()


    def set_window_trigger(self):
        title = input("Enter (whole or part of) the window title: ")
        flow = input("Enter the path of the flow to run on the window trigger: ")
        flow = flow.lower().replace(".xml", "") + ".xml"
        name = flow.split("\\")[-1]
        path = flow.split("\\")[:-1]
        # First register the flow
        sql = f"INSERT INTO Registered (name, location) SELECT '{name}', '{path}' WHERE NOT EXISTS (SELECT id FROM Registered WHERE name='{name}' AND location='{path}');"
        self.cursor.execute(sql)
        self.db.connection.commit()
        sql = f"SELECT id FROM Registered WHERE name='{name}' AND location='{path}'"
        self.cursor.execute(sql)
        row = self.cursor.fetchone()
        id = row[0]
        sql = f"INSERT INTO Triggers (registered_id, trigger_info) SELECT {id}, '{triggerinfo}' WHERE NOT EXISTS (SELECT id FROM Triggers WHERE registered_id={id} AND trigger_info='{triggerinfo}');"
        self.cursor.execute(sql)
        self.db.connection.commit()
        print(f"Trigger set for flow '{name}' on (part of) Window-title '{title}'")


    def get_dbPath(self):
        """
        Get the path to the orchestrator database
        :return: The path to the orchestrator database
        """
        try:
            REG_PATH = r"SOFTWARE\BPMN_RPA"
            registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_READ)
            value, regtype = winreg.QueryValueEx(registry_key, 'dbPath')
            winreg.CloseKey(registry_key)
            return value
        except WindowsError:
            return None


trig = triggers()