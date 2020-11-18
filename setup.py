import setuptools
from os import path


def parse_requirements(filename):
    """Load requirements from a pip requirements file."""
    lineiter = (line.strip() for line in open(filename))
    return [line for line in lineiter if line and not line.startswith("#")]


if __name__ == "__main__":
    # read the contents of your README file
    this_directory = path.abspath(path.dirname(__file__))
    with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()
    setuptools.setup(
        name="BPMN_RPA",  # Replace with your own username
        version="0.0.58",
        author="Joost van Gils",
        author_email="joostvangils@1ic.nl",
        description="Robotic Process Automation in Windows by using Diagrams.net BPMN diagrams.",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/joostvangils/BPMN_RPA",
        packages=setuptools.find_packages(),
        install_requires=parse_requirements("requirements.txt"),
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: Apache Software License",
            "Operating System :: Microsoft",
        ],
        python_requires='>=3.6',
    )
