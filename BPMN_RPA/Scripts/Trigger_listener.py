import importlib
import json
import multiprocessing
import sqlite3
import winreg
import subprocess
import multiprocessing


from BPMN_RPA.Scripts.Windows import find_window
from BPMN_RPA.WorkflowEngine import WorkflowEngine


def main():
    jobs = []
    dbpath = get_reg("dbPath")
    connection = sqlite3.connect(rf'{dbpath}\orchestrator.db')
    sql = "SELECT * FROM Triggers;"
    cursor = connection.cursor()
    cursor.execute(sql)
    jobs = cursor.fetchall()
    connection.close()
    pool = multiprocessing.Pool()
    for c in range(0, len(jobs)):
        jb = json.loads(jobs[c][2])
        jobs.append(jb)
    results = pool.map(start_listener, jobs)


def get_reg(name):
    try:
        REG_PATH = r"SOFTWARE\BPMN_RPA"
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_READ)
        value, regtype = winreg.QueryValueEx(registry_key, name)
        winreg.CloseKey(registry_key)
        return value
    except WindowsError:
        return None


def start_listener(job):
    is_triggered = False
    if job.get('type') == "window":
        while True:
            sensitive = False
            if hasattr(job, "case_sensitive"):
                sensitive = job.get("case_sensitive")
            hwnd = find_window(job.get('title'), case_sensitive=sensitive)
            if not is_triggered and hwnd is not None:
                is_triggered = True
                engine = WorkflowEngine()
                doc = engine.open(job.get('path'))
                steps = engine.get_flow(doc)
                engine.run_flow(steps)
            else:
                if not hwnd:
                    is_triggered = False


if __name__ == "__main__":
    main()
