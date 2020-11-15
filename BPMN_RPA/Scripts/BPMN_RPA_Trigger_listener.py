import multiprocessing
import sqlite3
import winreg


class trigger_listener():

    def __init__(self):
        self.jobs = []
        self.dbpath = self.get_reg("dbPath")
        self.connection = sqlite3.connect(rf'{self.dbpath}\orchestrator.db')
        sql = "SELECT * FROM Triggers;"
        self.cursor = self.connection.cursor()
        self.cursor.execute(sql)
        jobs = self.cursor.fetchall()
        for j in jobs:
            jb = trigger_job()
            jb.id = j[0]
            jb.name = j[1]
            jb.type = j[3]
            jb.time = j[4]
            jb.expires = j[5]
            jb.expires_on = j[6]
            jb.date = j[7]
            jb.days = j[8]
            jb.days_of_month = j[9]
            jb.months = j[10]
            self.jobs.append(jb)

    def get_reg(self, name):
        try:
            REG_PATH = r"SOFTWARE\BPMN_RPA"
            registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_READ)
            value, regtype = winreg.QueryValueEx(registry_key, name)
            winreg.CloseKey(registry_key)
            return value
        except WindowsError:
            return None


class trigger_job(object):
    pass
