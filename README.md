# Liip (unofficial) Scrum Toolbox (lst)
<cite>"a bit of LST everyday keeps your troubles away"</cite> (Jimi Hendrix, 1969)

## What is it?
LST is a command line utility to create sprint burnup charts out of Jira/Zebra data. 
Just edit a yml config file so that it knows what project you're currently working on, and enjoy a nice up-to-date chart.

## Advantages
* team knows how the sprint is going on
* PO knows how the sprint is going on
* easy installation (Python is your friend)
* easy setup (aka _no_ setup)
* easy configuration (edit a yml file)
* coming soon: even easier configuration (through interactive questions)

## Installation
* sudo pip install git+git://github.com/sitron/lst@v0.6
* pip install -r https://raw.github.com/sitron/lst/master/requirements.txt
* copy the [.lst-secret_dist.yml](lst/blob/master/.lst-secret_dist.yml) file to you home, rename it to .lst-secret.yml and change your jira/zebra credentials
* create a directory somewhere on your machine where you want your graphs to be outputted and add its path to .lst-secret.yml 
* copy the [.lst_dist.yml](lst/blob/master/.lst_dist.yml) file to you home, rename it to .lst.yml and edit as needed (see below)
* run lst test-install which should dump you some html and finish by 'end' (yes! it's working!)
* run lst sprint-graph -p [your_project_name] and check your first graph!

## Settings
See the annotated example [.lst_dist.yml](lst/blob/master/.lst_dist.yml)
You will need to define at least 1 project and 1 sprint to be able to run a command

## Commands
### Fetch data and display a chart
`lst sprint-graph -p my_project -s my_sprint` (if only 1 sprint is defined for the project, the s option can be omited)
### Test LST installation
`lst test-install`

