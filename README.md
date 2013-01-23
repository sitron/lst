# Liip (unofficial) Scrum Toolbox (lst)
<cite>"a bit of LST everyday keeps your troubles away"</cite> (Jimi Hendrix, 1969)

## What is it?
LST is a command line utility to help you with your scrum life at Liip.
At the moment, it creates sprint burnup charts out of Jira/Zebra data, but more will come!
It's main advantage is its ease of use: just edit a yml config file so that it knows what project you're currently working on, and enjoy a nice up-to-date chart.

## Advantages
* team knows how the sprint is going on
* PO knows how the sprint is going on (bis)
* easy installation (Python (and pip) is your friend)
* easy setup (aka _no_ setup)
* easy configuration (edit a yml file)
* coming soon: even easier configuration (through interactive questions)

## Installation
* `sudo pip install git+git://github.com/sitron/lst@v0.8`
* `sudo pip install -r https://raw.github.com/sitron/lst/master/requirements.txt`
* copy the [.lst-secret_dist.yml](lst/blob/master/.lst-secret_dist.yml) file to you home, rename it to .lst-secret.yml and change your jira/zebra credentials (watch out for the file name: it's [dot]lst-secret.yml
* create a directory somewhere on your machine where you want your graphs to be output and add its path to .lst-secret.yml 
* copy the [.lst_dist.yml](lst/blob/master/.lst_dist.yml) file to you home, rename it to .lst.yml (watch out for the file name: it's [dot]lst.yml) and edit as needed (see 'Settings' below). You'll need to have at least 1 project and 1 sprint defined in your config to continue
* once your .lst.yml file is ready, run `lst test-install` to test your install. It should dump some html and finish by 'end' (yes! it's working!)
* run `lst ls` to check what projects are defined in your config
* run `lst ls -p [your_project_name]` to see all sprints defined for this project
* run `lst sprint-burnup -p [your_project_name] -s [sprint_index]` and enjoy your first graph!

## Upgrade
if by any chance you already install LST before, just run:
* `sudo pip install git+git://github.com/sitron/lst@v0.7 --upgrade` 

## Settings
See the annotated example [.lst_dist.yml](lst/blob/master/.lst_dist.yml)
You will need to define at least 1 project and 1 sprint to be able to run a command

the config file is a project list, each project is defined by:

* a name: it can be anything. It's just a shortcut that you'll use to run all commands (that need a project name)
* a list of sprints, each sprint being defined by:
 * an index (integer) must be unique within the project, so that you can then call "draw me a graph for [project_name], using sprint [sprint_index] 
 * a number of commited man days (integer). Self explanatory.
 * some Zebra specific settings:
       * the zebra client id (check in Zebra, usually a 4 digits integer). You can also easily find it by running `taxi search [project_name]` if you have Taxi installed (you should!)
       * a list of Zebra activitity ids (check Zebra) or put '*' (including the quotes) to use all activities
       * a list of Zebra user ids (3 digits integer). You can run `lst get-user-id my_last_name` to get ids out of Zebra
       * a start date (like 2013-01-21)
       * a end date (like 2013-01-22)
       * optional: you can force some static data for Zebra: for example we have an external employee that does not log any hour in Zebra, but i know that i need to add 8 hours of work for each day. I can then use a date range '2013-01-21/2013-01/30 and '+8' as time to add 8 hours to all Zebra data retrieved.
 * some Jira specific settings:
       * the Jira project id, usually a 5 digits integer. Run `lst jira-config-helper my_story_id` to get its project id
       * the sprint name: the FixVersion name as seen in Jira Query Builder. Run `lst jira-config-helper my_story_id` to get its sprint name
       * optional, nice\_identifier: if you have "Nice to have" stories in your sprint, you can specify how to recognize them (we use '(NICE)' in the story title)
       * optional, closed_status: the status to consider as 'closed'. During the sprint the stories are usually not closed, but set as "For PO Review". Use this string to keep your burnup chart up-to-date
       * optional, closed\_status\_codes: a list of status ids to consider as closed. By default it uses 6 (closed) and 10008 (For PO Review)
       * optional, ignored: a list of stories to ignore. Specify their ids in a list ['XXX-134', 'XXX-119']. Very often we have stories in the sprint that should not be considered for the graph (closed before the sprint, out of scope.. whatever)

All this seems pretty complicated but it's just words... looking at the file itself might just be self explanatory enough...

## Available commands
### Fetch data and display a chart
`lst sprint-burnup -p my_project -s my_sprint`
### Fetch data and display a chart (if only 1 sprint is defined for the project)
`lst sprint-burnup -p my_project`
### Test LST installation
`lst test-install`
### Check all the projects defined in your config (if you don't remember their name for ex.)
`lst ls`
### Check all the sprints defined in your config for a specific project
`lst ls -p my_project`
### Search a Zebra user id by employee last name
`lst get-user-id my_last_name`
### Search multiple Zebra user ids by employees last name
`lst get-user-id my_last_name his_last_name her_last_name`
### Get Jira info for config (helper)
`lst jira-config-helper my_story_id`
Useful to fill the Jira part of the config. Give it a story id (JLC-xx) and it will retrieve it's project id and sprint name

