import json
import os
import winreg
from datetime import datetime

from BPMN_RPA.WorkflowEngine import SQL


class triggers():

    def __init__(self):
        self.db = SQL(self.get_dbPath())
        self.cursor = self.db.connection.cursor()
        self.choice = None
        self.trigger = None
        self.location = None
        self.name = None
        while True:
            print("\nEnter 'x' on any question to cancel")
            print("1. Trigger a flow on a Window Title")
            print("2. Schedule the trigger of a flow")
            print("3. Trigger when files are added or deleted in folder")
            self.choice = input("Enter your choice: ")
            if self.choice == "x":
                exit(0)
            elif self.choice == "1":
                self.set_window_trigger()
            elif self.choice == "2":
                self.schedule_trigger()
            elif self.choice == "3":
                self.set_folder_trigger()
            if self.choice in ["1", "2", "3"]:
                self.save_trigger()

    def set_folder_trigger(self):
        while True:
            flow = input("Enter the path of the flow to run on the window trigger: ")
            if flow == "x":
                exit(0)
            flow = flow.lower().replace(".xml", "") + ".xml"
            if os.path.exists(flow):
                break
            else:
                print(f"The flow '{flow}' doesn't exist.")
        self.location = flow
        self.name = flow.split("\\")[-1]
        while True:
            fld = input("Enter the path of the folder to watch for added or deleted files: ")
            if fld == "x":
                exit(0)
            if os.path.exists(fld):
                break
            else:
                print(f"The folder '{fld}' doesn't exist.")
        self.trigger = {'type': 'folder'}
        self.trigger.update({'flow': flow})
        self.trigger.update({'folder': fld})
        expire = input("Do you want this trigger to expire on a specific date (y/n)?: ")
        if expire.lower() == "x":
            exit(0)
        if expire == "y":
            expire_date = input("At which date do you want this trigger to expire (format dd-mm-yyyy)?: ")
            if expire_date.lower() == "x":
                exit(0)
            self.trigger.update({'expire_date': expire_date})
        print(f"Folder trigger set for flow '{self.name}' on folder '{self.trigger.get('folder')}'")

    def schedule_trigger(self):
        while True:
            flow = input("Enter the path of the flow to run on the window trigger: ")
            if flow == "x":
                exit(0)
            flow = flow.lower().replace(".xml", "") + ".xml"
            if os.path.exists(flow):
                break
            else:
                print(f"The flow '{flow}' doesn't exist.")
        self.location = flow
        self.name = flow.split("\\")[-1]
        path = flow.split("\\")[:-1]
        self.trigger = {'type': 'schedule'}
        self.trigger.update({'flow': flow})
        if flow == "x":
            exit(0)
        fire = input(
            f"Fire the trigger for flow '{self.name}' Daily (d), on Specific Dates (s), Weekly (w) or Monthly (m)?: ")
        if fire.lower() == "x":
            exit(0)
        self.trigger.update({'fire': fire})
        if fire == "d":
            daily = self.set_trigger_time(self.name)
            self.trigger.update(daily)
        if fire == "s":
            specific = self.set_trigger_date(self.name)
            self.trigger.update(specific)
        if fire == "w":
            weekds = self.set_trigger_weekly(self.name)
            self.trigger.update(weekds)
        if fire == "m":
            mnt = self.set_trigger_monthly(self.name)
            self.trigger.update(mnt)
        if self.choice == "1":
            print(f"Trigger set for flow '{self.name}' on (part of) Window-title '{self.trigger('title')}'")
        if self.choice == "2":
            if self.trigger.get('fire') == "d":
                print(f"Daily trigger set for flow '{self.name}' on '{self.trigger.get('trigger_time')}'")
            if self.trigger.get('fire') == "s":
                print(
                    f"Specific date trigger set for flow '{self.name}' on '{self.trigger.get('trigger_date')} {self.trigger.get('trigger_time')}'")

    def save_trigger(self):
        # First register the flow
        sql = f"INSERT INTO Registered (name, location) SELECT '{self.name}', '{self.location}' WHERE NOT EXISTS (SELECT id FROM Registered WHERE name='{self.name}' AND location='{self.location}');"
        self.cursor.execute(sql)
        self.db.connection.commit()
        sql = f"SELECT id FROM Registered WHERE name='{self.name}' AND location='{self.location}'"
        self.cursor.execute(sql)
        row = self.cursor.fetchone()
        id = row[0]
        trig_info = self.trigger
        triggerinfo = json.dumps(trig_info)
        sql = f"INSERT INTO Triggers (registered_id, trigger_info) SELECT {id}, '{triggerinfo}' WHERE NOT EXISTS (SELECT id FROM Triggers WHERE registered_id={id} AND trigger_info='{triggerinfo}');"
        self.cursor.execute(sql)
        self.db.connection.commit()

    def set_trigger_weekly(self, name):
        retn = {}
        another_one = True
        datedict = {}
        while True:
            upddate = input(
                f"Enter the days of the week the flow '{name}' should be triggered (format: mon-tue-wed-thu-fri-sat-sun): ")
            if upddate.lower() == "x":
                exit(0)
            if self.check_weekday(upddate):
                break
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

    def check_weekday(self, days):
        lst = days.split("-")
        ok = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
        for day in days:
            if day not in ok:
                print("Your input is not correct. Allowed: mon-tue-wed-thu-fri-sat-sun.")
                return False
        return True

    def is_valid_date(self, dt):
        lst = dt.split("-")
        year = lst[2]
        month = lst[1]
        day = lst[0]
        try:
            datetime(int(year), int(month), int(day))
            return True
        except ValueError:
            print("Your input is not a valid date.")
            return False

    def is_valid_time(self, dt):
        lst = dt.split(":")
        try:
            s = int(lst[2])
            m = int(lst[1])
            h = int(lst[0])
            if (h < 0) or (h > 24) or (m < 0) or (m > 59) or (s < 0) or (s > 59):
                print("Your input is not a valid time.")
                return False
            return True
        except:
            print("Your input is not a valid time.")
            return False

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
        datedict.update({'trigger_monthly': updmonth, 'trigger_weekdays': upddate,
                         'trigger_times': self.set_trigger_time(name, False)})
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
        counter = 1
        while another_one:
            datedict = {}
            while True:
                upddate = input(f"Enter the date the flow '{name}' should be triggered (format dd-mm-yyyy): ")
                if upddate.lower() == "x":
                    exit(0)
                if self.is_valid_date(upddate):
                    break
            datedict.update({f'trigger_date_{counter}': upddate, 'trigger_times': self.set_trigger_time(name, False)})
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
            counter += 1
        return retn

    def set_trigger_time(self, name, askexpire=True):
        retn = {}
        another_one = True
        counter = 1
        while another_one:
            times = {}
            while True:
                updtime = input(f"Enter the time the flow '{name}' should be triggered (format hh:mm:ss): ")
                if updtime.lower() == "x":
                    exit(0)
                if self.is_valid_time(updtime):
                    break
            if askexpire:
                expire = input("Do you want this trigger to expire on a specific date (y/n)?: ")
                if expire.lower() == "x":
                    exit(0)
                if expire == "y":
                    expire_date = input("At which date do you want this trigger to expire (format dd-mm-yyyy)?: ")
                    if expire_date.lower() == "x":
                        exit(0)
                    times.update({f'trigger_time_{counter}': updtime, 'expire_date': expire_date})
                else:
                    times.update({f'trigger_time_{counter}': updtime})
            else:
                times.update({f'trigger_time_{counter}': updtime})
            retn.update(times)
            yn = input(
                f"Do you want to add another trigger time to the trigger you just entered for flow '{name}' (y/n)?: ")
            if yn.lower() == "n":
                another_one = False
            counter += 1
        return retn

    def set_window_trigger(self):
        title = input("Enter whole or part of the window title: ")
        if title == "x":
            exit(0)
        while True:
            flow = input("Enter the path of the flow to run on the window trigger: ")
            if flow == "x":
                exit(0)
            flow = flow.lower().replace(".xml", "") + ".xml"
            if os.path.exists(flow):
                break
            else:
                print(f"The flow '{flow}' doesn't exist.")
        while True:
            sensitive = input("Matching witch case sensitivity on title (y/n)?: ")
            if sensitive.lower() == "x":
                exit(0)
            if sensitive.lower() in ["y", "n"]:
                break
            print("Your input was not correct.")
        self.trigger = {'type': 'window', 'title': title, 'flow': self.location, 'sensitive': sensitive}
        self.location = flow
        self.name = flow.split("\\")[-1]
        path = flow.split("\\")[:-1]
        self.save_trigger()
        print(f"Trigger set for flow '{self.name}' on (part of) Window-title '{self.trigger.get('title')}'")

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
