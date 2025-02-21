from setuptools import setup, find_packages


def read_requirements() -> list:
    with open('requirements.txt') as f:
        deps = f.read().splitlines()
    return [line.strip() for line in deps if line.strip() and not line.startswith('#')]


setup(
    name='range_monitor_2',
    author='Georgia Cyber Range',
    version='0.1',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
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
            'monitor_setup=scripts.create_env:main',
            'monitor=cli.main:main'
        ]
    },
    setup_requires=['setuptools>=17.1'],
    include_package_data=True
)
