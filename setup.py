import setuptools
from os import path


def parse_requirements(filename):
    """Load requirements from a pip requirements file."""
    with open(filename) as f:
        lineiter = (line.strip() for line in f)
        return [line for line in lineiter if line and not line.startswith("#")]


if __name__ == "__main__":
    # read the contents of your README file
    this_directory = path.abspath(path.dirname(__file__))
    with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()
    setuptools.setup(
        name="BPMN_RPA",  # Replace with your own username
        version="8.1.3",
        author="Joost van Gils",
        author_email="joostvangils@1ic.nl",
        description="Robotic Process Automation by running BPMN diagram flows.",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/joostvangils/BPMN_RPA",
        packages=setuptools.find_packages(),
        package_dir={'BPMN_RPA': 'BPMN_RPA'},
        include_package_data=True,
        install_requires=parse_requirements("requirements.txt"),
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: GNU Affero General Public License v3",
            "Operating System :: Microsoft", "Operating System :: POSIX :: Linux"
        ],
        python_requires='>=3.9',
    )
