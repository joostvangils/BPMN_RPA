import setuptools


setuptools.setup(
    name="BPMN_RPA", # Replace with your own username
    version="0.0.3",
    author="Joost van Gils",
    author_email="joostvangils@1ic.nl",
    description="Robotic Process Automation in Windows by using Diagrams.net BPMN diagrams.",
    long_description="With this Framework you can draw Business Process Model Notation based Diagrams and run those diagrams with a WorkflowEngine.",
    long_description_content_type="text/markdown",
    url="https://github.com/joostvangils/BPMN_RPA",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: Microsoft",
    ],
    python_requires='>=3.6',
)