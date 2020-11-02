import os
import shutil
import urllib
from sys import path
import requests

print("The DPMN_RPA package will be installed in the Python site-packages directory.")
os.system("pip install --upgrade --force-reinstal BPMN_RPA")
installdir = input("\nEnter the directory to install additional files:")
if not str(installdir).endswith("\\"):
    installdir += "\\"
if not os.path.exists(installdir):
    os.mkdir(installdir)
print(f"\nThe Drawio desktop program will be downloaded to {installdir}...")
print("Please wait until the file is downloaded...")
urllib.request.urlretrieve("https://github.com/jgraph/drawio-desktop/releases/download/v13.7.9/draw.io-13.7.9-windows-no-installer.exe", f'{installdir}drawio.exe')
print("Download complete.")
print("Downloading BPMN RPA predefined Shapes")
urllib.request.urlretrieve("https://github.com/joostvangils/BPMN_RPA/blob/main/BPMN_RPA/BPMN%20RPA%20Mouse.xml", f'{installdir}BPMN RPA Mouse.xml')
urllib.request.urlretrieve("https://github.com/joostvangils/BPMN_RPA/blob/main/BPMN_RPA/BPMN%20RPA%20Shapes.xml", f'{installdir}BPMN RPA Shapes.xml')
urllib.request.urlretrieve("https://github.com/joostvangils/BPMN_RPA/blob/main/BPMN_RPA/BPMN%20RPA%20System.xml", f'{installdir}BPMN RPA System.xml')
urllib.request.urlretrieve("https://github.com/joostvangils/BPMN_RPA/blob/main/BPMN_RPA/BPMN%20RPA%20Window.xml", f'{installdir}BPMN RPA Window.xml')
urllib.request.urlretrieve("https://github.com/joostvangils/BPMN_RPA/blob/main/BPMN_RPA/BPMN%20RPA%20Keyboard.xml", f'{installdir}BPMN RPA Keyboard.xml')
print("Download and install complete.")