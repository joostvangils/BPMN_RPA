cd d:\Projects\BPMN_RPA
Rmdir /S /Q "d:\Projects\BPMN_RPA\BPMN_RPA.egg-info"
Rmdir /S /Q "d:\Projects\BPMN_RPA\build"
Rmdir /S /Q "d:\Projects\BPMN_RPA\dist"
python -m poetry build
python -m twine upload --repository pypi dist/* --username __token__ --password pypi-AgEIcHlwaS5vcmcCJDhhYWJhMmFhLTkwYzAtNDA4Mi1iYzMxLWRkMjE3ZDQzYjM5YgACEFsxLFsiYnBtbi1ycGEiXV0AAixbMixbImI4ZmI2ZTk3LTE0MjctNGYxNS04NmRkLTNkNzM2YjZmOWIxOSJdXQAABiC_hDnv7cwZGM8gUJzKKfsfSzlKZTXqjZ7ENDH7jW5rIg
