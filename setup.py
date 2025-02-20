from scripts.utils import pyproject_reader
import os 

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
project_meta = pyproject_reader(here, 'project')

