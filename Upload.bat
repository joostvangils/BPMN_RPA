cd C:\PythonProjects\BPMN_RPA
Rmdir /S /Q "C:\PythonProjects\BPMN_RPA\BPMN_RPA.egg-info"
Rmdir /S /Q "C:\PythonProjects\BPMN_RPA\dist"
python setup.py sdist bdist_wheel
python -m twine upload --repository pypi dist/*