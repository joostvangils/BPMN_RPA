cd d:\Projects\BPMN_RPA
Rmdir /S /Q "d:\Projects\BPMN_RPA\BPMN_RPA.egg-info"
Rmdir /S /Q "d:\Projects\BPMN_RPA\build"
Rmdir /S /Q "d:\Projects\BPMN_RPA\dist"
python setup.py sdist bdist_wheel
python -m twine upload --repository pypi dist/*