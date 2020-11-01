import os
from sys import path
import requests

print("The DPMN_RPA package will be installed in the Python site-packages directory.")
os.system("pip install --upgrade --force-reinstal BPMN_RPA")
installdir = input("\nEnter the directory to install additional files:")
if not str(installdir).endswith("\\"):
    installdir += "\\"
if not path.exists(installdir):
    os.mkdir(installdir)
print("\nThe Drawio desktop package will be downloaded and started....")
drawio = requests.get("https://github.com/jgraph/drawio-desktop/releases")
open(drawio)