from distutils.core import setup

setup(
    name = 'scrum-nanny',
    version = '1.0.0',
    packages = ['scrum_nanny'],
    package_dir = {'scrum_nanny': 'src/scrum_nanny'},
    author = 'sitron',
    author_email = 'laurent@sitronnier.com',
    url = 'scrum-nanny.sitronnier.com',
    description = 'Sprint burndown chart from Jira and Zebra',
)

