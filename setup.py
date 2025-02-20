import toml
import os

from setuptools import setup, find_packages


def pyproject_reader(app_root: str) -> dict:
    '''Loads content of pyproject.toml file given a path to the app rot 
    and returns the content or a the metadata of a given key

    Arguments:
        path {str} -- _path to pyproject.toml file

    Keyword Arguments:
        key {Optional[str]} -- _key to metadata (default: {None})

    Returns:
        dict -- the content of the pyproject.toml file or the metadata of a given key
    '''

    base = toml.load(os.path.join(app_root, 'pyproject.toml'))
    return base


def read_requirements() -> list:
    '''
    Reads the requirements.txt file and returns a list of packages
    '''
    with open(f'requirements.txt') as f:
        deps = f.read().splitlines()
    return [line.strip() for line in deps if line.strip() and not line.startswith('#')]


here = os.path.abspath(os.path.dirname(__file__))
pyproj = pyproject_reader(here)
proj_meta = pyproj['project']

setup(
    name=proj_meta['name'],
    author=proj_meta['authors'][0]['name'],
    version=proj_meta['version'],
    packages=find_packages(where='src') + ['cli'],
    package_dir={
        '': 'src',
        'cli': "cli",
    },
    install_requires=read_requirements(),
    extras_require={
        'dev': [
            "pytest>=7.1.0",
            "flake8>=4.0.1",
            "coverage>=6.3.2",
        ]
    },
    entry_points={
        'console_scripts': [
            'monitor=cli.main:main'
        ]
    }
)
