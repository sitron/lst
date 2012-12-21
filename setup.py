#!/usr/bin/env python
from distutils.core import setup

setup(
    name = 'lst',
    version = '0.0.4',
    packages = ['lst'],
    description = 'Liip Scrum Toolbox',
    author = 'sitron',
    author_email = 'laurent@sitronnier.com',
    url = 'https://github.com/sitron/lst',
    scripts = ['bin/lst'],
    package_data = {'lst': ['html_templates/*.html', 'html_templates/css/*.css', 'html_templates/js/*.js', 'html_templates/js/vendors/*.js']},
)

