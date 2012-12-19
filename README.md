# Liip (unofficial) Scrum Toolbox (lst)
<cite>"a bit of LST everyday keeps your trouble away"</cite>

## What is it?
LST is a command line utility to create sprint burnup charts out of Jira/Zebra data. Just edit a yml config file so that it knows what project you're currently working on, and enjoy a nice up-to-date chart.

## Advantages
* team knows how the sprint is going on
* PO knows how the sprint is going on
* easy installation (Python is your friend)
* easy setup (aka _no_ setup)
* easy configuration (edit a yml file)
* coming soon: even easier configuration (through interactive questions)

## Installation
* pip install git+git://github.com/sitron/lst@v0.2
* copy the [.lst-secret_dist.yml](lst/blob/master/.lst-secret_dist.yml) file to you home, rename it to .lst-secret.yml and change your jira/zebra credentials
* copy the [.lst_dist.yml](lst/blob/master/.lst_dist.yml) file to you home, rename it to .lst.yml and edit as needed (see below)
* run lst sprint-graph -p [your_project_name]
* optionnaly create an alias to run it from anywhere

## Settings
See the annotated example [.lst_dist.yml](lst/blob/master/.lst_dist.yml)
You will need to define at least 1 project and 1 sprint to be able to run a command

## Commands
### Fetch data and display a chart (default)
`lst sprint-graph -p my_project -s my_sprint`

