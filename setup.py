'''
it is necessary to have a setup.py file. This file is used by setuptools to define the configuration of a project, 
such as its metadata, dependencies, and more. If you look at any libraries or open-source projects on PyPI, you will see
information about the project, such as metadata, dependencies, and version. We will set up this entire configuration.
'''



from setuptools import setup, find_packages
from typing import List


# The find_packages function scans all folders and considers any folder with an __init__.py file as a package.
# For example, if there is an __init__.py file in the network or network_security folder,
# those folders are considered packages. This function helps in identifying all packages within the project

def get_requirements() -> List[str] :
    """
    This function will return the list of requirements
    """
    requirements_list : List[str]  = []
    try:
        with open("requirements.txt") as requirement_file:
            line = requirement_file.readlines()
            
            for line in requirement_file:
                requirement = line.strip()
                if requirement and  requirement != "-e .":
                    requirements_list.append(requirement)
                
        
    except FileNotFoundError:
        raise FileNotFoundError("requirements.txt file not found")
    
    return requirements_list

setup(
    name="network_security",
    version="0.0.1",
    author="Nikhil Nagar",
    author_email="nagarn603@gmail.com",
    packages=find_packages(),
    install_requires=get_requirements(),
    description="A package for network security",
)