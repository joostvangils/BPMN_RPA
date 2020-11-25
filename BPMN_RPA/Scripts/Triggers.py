import json
import winreg

from BPMN_RPA.WorkflowEngine import SQL


class triggers():

    def __init__(self):
        self.db = SQL(self.get_dbPath())
        self.cursor = self.db.connection.cursor()
        while True:
            print("Enter 'x' on any question to cancel")
            print("1. Trigger a flow on a Window Title")
            print("2. Schedule the trigger of a flow")
            choice = input("Enter your choice: ")
            if choice == "x":
                exit(0)
            elif choice == "1":
                self.set_window_trigger()
            elif choice == "2":
                self.schedule_trigger()

    def schedule_trigger(self):
        flow = input("Enter the path of the flow to run on the window trigger: ")
        flow = flow.lower().replace(".xml", "") + ".xml"
        name = flow.split("\\")[-1]
        path = flow.split("\\")[:-1]
        trigger = {}
        if flow == "x":
            exit(0)
        fire = input(
            f"Fire the trigger for flow '{name}' Daily (d), on Specific Dates (s), Weekly (w) or Monthly (m)?: ")
        if fire.lower() == "x":
            exit(0)
        trigger.update({'fire': fire})
        if fire == "d":
            daily = self.set_trigger_time(name)
            trigger.update(daily)
        if fire == "s":
            specific = self.set_trigger_date(name)
            trigger.update(specific)
        if fire == "w":
            weekds = self.set_trigger_weekly(name)
            trigger.update(weekds)
        if fire == "m":
            mnt = self.set_trigger_monthly(name)
            trigger.update(mnt)
        # First register the flow
        sql = f"INSERT INTO Registered (name, location) SELECT '{name}', '{flow}' WHERE NOT EXISTS (SELECT id FROM Registered WHERE name='{name}' AND location='{flow}');"
        self.cursor.execute(sql)
        self.db.connection.commit()
        sql = f"SELECT id FROM Registered WHERE name='{name}' AND location='{flow}'"
        self.cursor.execute(sql)
        row = self.cursor.fetchone()
        id = row[0]
        trig_info = trigger
        triggerinfo = json.dumps(trig_info)
        sql = f"INSERT INTO Triggers (registered_id, trigger_info) SELECT {id}, '{triggerinfo}' WHERE NOT EXISTS (SELECT id FROM Triggers WHERE registered_id={id} AND trigger_info='{triggerinfo}');"
        self.cursor.execute(sql)
        self.db.connection.commit()
        print(f"Trigger set for flow '{name}' on (part of) Window-title '{title}'")

    def set_trigger_weekly(self, name):
        retn = {}
        another_one = True
        datedict = {}
        upddate = input(
            f"Enter the days of the week the flow '{name}' should be triggered (format: mon-tue-thu-fri-sat-sun): ")
        if upddate.lower() == "x":
            exit(0)
        datedict.update({'trigger_weekly': upddate, 'trigger_times': self.set_trigger_time(name, False)})
        expire = input("Do you want this trigger to expire on a specific date (y/n)?: ")
        if expire.lower() == "x":
            exit(0)
        if expire == "y":
            expire_date = input("At which date do you want this trigger to expire (format dd-mm-yyyy)?: ")
            if expire_date.lower() == "x":
                exit(0)
            datedict.update({'expire_date': expire_date})
        retn.update(datedict)
        return retn

    def set_trigger_monthly(self, name):
        retn = {}
        another_one = True
        datedict = {}
        updmonth = input(
            f"Enter the months of the year the flow '{name}' should be triggered (format: jan-feb-mar-apr-may-jun-jul-aug-sep-oct-nov-dec): ")
        if updmonth.lower() == "x":
            exit(0)
        upddate = input(
            f"Enter the days of the week the flow '{name}' should be triggered (format: mon-tue-thu-fri-sat-sun): ")
        if upddate.lower() == "x":
            exit(0)
        datedict.update({'trigger_monthly': updmonth, 'trigger_weekdays': upddate, 'trigger_times': self.set_trigger_time(name, False)})
        expire = input("Do you want this trigger to expire on a specific date (y/n)?: ")
        if expire.lower() == "x":
            exit(0)
        if expire == "y":
            expire_date = input("At which date do you want this trigger to expire (format dd-mm-yyyy)?: ")
            if expire_date.lower() == "x":
                exit(0)
            datedict.update({'expire_date': expire_date})
        retn.update(datedict)
        return retn

    def set_trigger_date(self, name):
        retn = {}
        another_one = True
        while another_one:
            datedict = {}
            upddate = input(f"Enter the date the flow '{name}' should be triggered (format dd-mm-yyyy): ")
            if upddate.lower() == "x":
                exit(0)
            datedict.update({'trigger_date': upddate, 'trigger_times': self.set_trigger_time(name, False)})
            expire = input("Do you want this trigger to expire on a specific date (y/n)?: ")
            if expire.lower() == "x":
                exit(0)
            if expire == "y":
                expire_date = input("At which date do you want this trigger to expire (format dd-mm-yyyy)?: ")
                if expire_date.lower() == "x":
                    exit(0)
                datedict.update({'expire_date': expire_date})
            retn.update(datedict)
            yn = input(f"Do you want to add another trigger date for flow '{name}' (y/n)?: ")
            if yn.lower() == "n":
                another_one = False
        return retn

    def set_trigger_time(self, name, askexpire=True):
        retn = {}
        another_one = True
        while another_one:
            times = {}
            updtime = input(f"Enter the time the flow '{name}' should be triggered (format hh:mm:ss): ")
            if updtime.lower() == "x":
                exit(0)
            if askexpire:
                expire = input("Do you want this trigger to expire on a specific date (y/n)?: ")
                if expire.lower() == "x":
                    exit(0)
                if expire == "y":
                    expire_date = input("At which date do you want this trigger to expire (format dd-mm-yyyy)?: ")
                    if expire_date.lower() == "x":
                        exit(0)
                    times.update({'trigger_time': updtime, 'expire_date': expire_date})
            else:
                times.update({'trigger_time': updtime})
            retn.update(times)
            yn = input(f"Do you want to add another trigger time for flow '{name}' (y/n)?: ")
            if yn.lower() == "n":
                another_one = False
        return retn

    def set_window_trigger(self):
        title = input("Enter (whole or part of) the window title: ")
        if title == "x":
            exit(0)
        flow = input("Enter the path of the flow to run on the window trigger: ")
        if flow == "x":
            exit(0)
        sensitive = input("Matching witch case sensitivity on title (y/n)?: ")
        if sensitive == "x":
            exit(0)
        flow = flow.lower().replace(".xml", "") + ".xml"
        name = flow.split("\\")[-1]
        path = flow.split("\\")[:-1]
        # First register the flow
        sql = f"INSERT INTO Registered (name, location) SELECT '{name}', '{flow}' WHERE NOT EXISTS (SELECT id FROM Registered WHERE name='{name}' AND location='{flow}');"
        self.cursor.execute(sql)
        self.db.connection.commit()
        sql = f"SELECT id FROM Registered WHERE name='{name}' AND location='{flow}'"
        self.cursor.execute(sql)
        row = self.cursor.fetchone()
        id = row[0]
        trig_info = {'type': 'window', 'title': title, 'flow': name, 'path': flow}
        triggerinfo = json.dumps(trig_info)
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
