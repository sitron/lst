#!/usr/bin/env python
from distutils.core import setup
import distutils.sysconfig
import os

# target directory where static assets (html templates, js files) will be copied
# see data_files below
template_dir = os.path.join(distutils.sysconfig.get_python_lib(), 'lst', 'html_templates')

setup(
    name = 'lst',
    version = '0.0.4',
    packages = ['lst'],
    description = 'Liip Scrum Toolbox',
    author = 'sitron',
    author_email = 'laurent@sitronnier.com',
    url = 'https://github.com/sitron/lst',
    scripts = ['bin/lst'],
    data_files = [
        (template_dir, ['lst/html_templates/sprint_burnup.html', 'lst/html_templates/test.html']),
        (os.path.join(template_dir, 'css'), ['lst/html_templates/css/graph.css']),
        (os.path.join(template_dir, 'js'), ['lst/html_templates/js/graph.js']),
        (os.path.join(template_dir, 'js', 'vendors'), ['lst/html_templates/js/vendors/d3.v2.js', 'lst/html_templates/js/vendors/jquery.js']),
    ]
)

