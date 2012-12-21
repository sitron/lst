#!/usr/bin/env python
from distutils.core import setup

setup(
    name = 'lst',
    version = '0.0.2',
    packages = ['lst'],
    description = 'Liip Scrum Toolbox',
    author = 'sitron',
    author_email = 'laurent@sitronnier.com',
    url = 'https://github.com/sitron/lst',
    requires = [
        'PyYAML>=3.10',
        'argparse>=1.2.1',
        'python-dateutil>=2.1',
        'six>=1.2.0',
        'wsgiref>=0.1.2'
    ],
    scripts = ['bin/lst'],
    package_data = {'lst': ['html_templates']},
)

