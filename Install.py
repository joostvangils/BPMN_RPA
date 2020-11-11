import os
import shutil
import urllib
import winreg
from sys import path
import requests


def set_reg(name, value):
    """
    Write BPMN RPA values to the registry
    :param name: The key name of the value to write
    :param value: The value to write
    """
    try:
        REG_PATH = r"SOFTWARE\BPMN_RPA"
        winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_PATH)
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0,
                                       winreg.KEY_WRITE)
        winreg.SetValueEx(registry_key, name, 0, winreg.REG_SZ, value)
        winreg.CloseKey(registry_key)
        return True
    except WindowsError:
        return False


print("The DPMN_RPA package will be installed in the Python site-packages directory.")
os.system("pip install --upgrade --force-reinstal BPMN_RPA")
installdir = input("\nEnter the directory to install additional files: ")
if not str(installdir).endswith("\\"):
    installdir += "\\"
if not os.path.exists(installdir):
    os.mkdir(installdir)
if not os.path.exists(f'{installdir}Registered Flows'):
    os.mkdir(f'{installdir}Registered Flows')
set_reg("dbPath", installdir)
pythonpath = input("\nEnter the full path to your Python.exe file: ")
if not str(pythonpath).lower().endswith("python.exe"):
    if not pythonpath.endswith("\\"):
        pythonpath += "\\Python.exe"
    else:
        pythonpath += "Python.exe"
set_reg("PythonPath", pythonpath)
print(f"\nThe Drawio desktop program will be downloaded to {installdir}...")
print("Please wait until the file is downloaded. This may take a while...")
urllib.request.urlretrieve("https://github.com/jgraph/drawio-desktop/releases/download/v13.7.9/draw.io-13.7.9-windows-no-installer.exe", f'{installdir}drawio.exe')
print("Download complete.")
print("Downloading Dashboard...")
urllib.request.urlretrieve("https://raw.githubusercontent.com/joostvangils/BPMN_RPA/main/BPMN_RPA/Orchestrator/Dashboard.py", f'{installdir}Dashboard.py')
print("Download complete.")
print("Downloading BPMN RPA predefined Shapes...")
urllib.request.urlretrieve("https://github.com/joostvangils/BPMN_RPA/blob/main/BPMN_RPA/BPMN%20RPA%20Mouse.xml", f'{installdir}BPMN RPA Mouse.xml')
urllib.request.urlretrieve("https://github.com/joostvangils/BPMN_RPA/blob/main/BPMN_RPA/BPMN%20RPA%20Shapes.xml", f'{installdir}BPMN RPA Shapes.xml')
urllib.request.urlretrieve("https://github.com/joostvangils/BPMN_RPA/blob/main/BPMN_RPA/BPMN%20RPA%20System.xml", f'{installdir}BPMN RPA System.xml')
urllib.request.urlretrieve("https://github.com/joostvangils/BPMN_RPA/blob/main/BPMN_RPA/BPMN%20RPA%20Window.xml", f'{installdir}BPMN RPA Window.xml')
urllib.request.urlretrieve("https://github.com/joostvangils/BPMN_RPA/blob/main/BPMN_RPA/BPMN%20RPA%20Keyboard.xml", f'{installdir}BPMN RPA Keyboard.xml')
print("Installing BPMN RPA trigger listener batch file in your personal Windows StartUp directory...")
username = os.environ['USERNAME']
startupfolder = f"C:\\Users\\{username}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"
bat = open(f"{startupfolder}\\BPMN_RPA_Trigger_Listener.bat", "w")
bat.write(f"SETCONSOLE /minimize\nSet oShell = CreateObject (\"WScript.Shell\")\noShell.run \"pythonw {installdir}Scripts\\BPMN_RPA_Trigger_Listener.py\"")
print("Download and install complete.")