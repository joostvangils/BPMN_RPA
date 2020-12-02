import importlib
import json
import multiprocessing
import sqlite3
import winreg
import subprocess
import multiprocessing
from datetime import datetime

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
            if "case_sensitive" in job.keys():
                sensitive = job.get("case_sensitive")
            hwnd = find_window(job.get('title'), case_sensitive=sensitive)
            if not is_triggered and hwnd is not None and not job.get('flow') is None:
                is_triggered = True
                engine = WorkflowEngine()
                doc = engine.open(job.get('flow'))
                steps = engine.get_flow(doc)
                engine.run_flow(steps)
            else:
                if not hwnd:
                    is_triggered = False
    if job.get('type') == "schedule":
        while True:
            if "fire" in job.keys():
                type = job.get("fire")
                if type == "d":
                    count = 1
                    times = []
                    while True:
                        if f"trigger_time_{count}" in job.keys():
                            times.append(job.get(f"trigger_time_{count}"))
                        else:
                            break
                        count += 1
                    now = datetime.now().strftime("%H:%M:%S")
                    if not is_triggered and now in times:
                        is_triggered = True
                        engine = WorkflowEngine()
                        doc = engine.open(job.get('flow'))
                        steps = engine.get_flow(doc)
                        engine.run_flow(steps)
                    else:
                        is_triggered = True
                if type == "s":
                    count = 1
                    times = []
                    while True:
                        if f"trigger_time_{count}" in job.keys():
                            times.append(job.get(f"trigger_time_{count}"))
                        else:
                            break
                        count += 1
                    now = datetime.now().strftime("%H:%M:%S")
                    if not is_triggered and now in times:
                        is_triggered = True
                        engine = WorkflowEngine()
                        doc = engine.open(job.get('flow'))
                        steps = engine.get_flow(doc)
                        engine.run_flow(steps)
                    else:
                        is_triggered = True


if __name__ == "__main__":
    main()
