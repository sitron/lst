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
)

