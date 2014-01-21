#!/usr/bin/env python
from setuptools import setup, find_packages
from lst import __version__


setup(
    name='lst',
    version=__version__,
    packages=find_packages(),
    description='Liip Scrum Toolbox',
    author='sitron',
    author_email='laurent@sitronnier.com',
    url='https://github.com/sitron/lst',
    scripts=['bin/lst'],
    test_suite="lst.tests.suite",
    install_requires=[
        'PyYAML>=3.10',
        'argparse>=1.2.1',
        'python-dateutil>=2.1',
        'six>=1.2.0',
        'pygal>=1.1.0',
        'beautifulsoup4>=4.3.2',
    ],
)

