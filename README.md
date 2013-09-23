# Liip (unofficial) Scrum Toolbox (lst)
<cite>"a bit of LST everyday keeps your troubles away"</cite> (Jimi Hendrix, 1969)

## What is it?
LST is a command line utility to help you with your scrum life at Liip.
At the moment, it creates sprint burnup charts out of Jira/Zebra data, but more will come!
It's main advantage is its ease of use: just edit a yml config file so that it knows what project you're currently working on, and enjoy a nice up-to-date chart.

## Advantages
* team knows how the sprint is going on
* PO knows how the sprint is going on (bis)
* no more "oh sh@@ i just noticed xxx pushed all his hours on a wrong project!"
* helps to improve estimation by displaying on what stories time was spent
* easy installation (Python (and pip) is your friend)
* easy setup (aka _no_ setup)
* easy configuration (edit a yml file)
* new! even easier configuration (through interactive questions)
* new! add MD forecast day by day with the new "planned" config param

## Installation
* `sudo pip install git+git://github.com/sitron/lst@v1.2.0`
* `sudo pip install -r https://raw.github.com/sitron/lst/master/requirements.txt`
* copy the [.lst-secret_dist.yml](.lst-secret_dist.yml) file to you home (yes, click on the [link](.lst-secret_dist.yml)!), rename it to .lst-secret.yml and change your jira/zebra credentials (watch out for the file name: it's [dot]lst-secret.yml
* create a directory somewhere on your machine where you want your graphs to be output and add its path to .lst-secret.yml 
* create a blank file in your home called .lst.yml (`cd && touch .lst.yml`)
* that'it!

## Create your first burnup graph
* first you need to add a sprint to your config. To do so just run the interactive command `lst add-sprint`
* answer the questions. This will update your config using the default settings.
* run `lst sprint-burnup my_sprint_name` and enjoy your first graph!
* if you want to customize your config (to limit the Zebra users to take into account, or override a value or...) have a look at the Settings section below

## Check estimates accuracy
* make sure you have at least 1 sprint defined in your config (see "create your first burnup graph" above)
* add a line `commit_prefix: xxx` in your config right under the zebra key.
```
zebra:
    commit_prefix: jlc-
    // where jlc- is how you prefix all your recorded time in Zebra
```
* run `lst result-per-story my_sprint_name` and enjoy a nice graph

## Check that your team mates didn't charge a wrong project
* run `lst check-hours to get all hours pushed by all users yesterday
* optionally specify one or multiple user_id(s) `lst check-hours -u user_id user_id` to limit the users taken into account (get zebra user ids by running the get-user-id command (see 'Available commands' below)
* optionally specify a date `lst check-hours -d 23.03.2013` to get hours for that date (defaults to yesterday)
* optionally specify an end date by adding a second date `lst check-hours -d 20.03.2013 22.03.2013` to get hours in this date range

## Install troubleshooting
* run `lst test-install` to test your install. It should dump some html and finish by 'end'
* get in touch with support :)

## Upgrade
if by any chance you already installed LST before, just run:
* `sudo pip install git+git://github.com/sitron/lst@v1.2.0 --upgrade`
* for old users (prior to 1.1) who want to keep (and upgrade) their config please check the [dedicated wiki page](https://github.com/sitron/lst/wiki/Upgrade)

## Available commands
### Fetch data and display a chart (by default displays values up to yesterday)
`lst sprint-burnup my_sprint_name`
### Fetch data and display a chart up to a specific date
`lst sprint-burnup my_sprint_name -d 2013.05.01
### Add a sprint to your config (interactive command)
`lst add-sprint`
### Fetch data and display how well your stories were estimated compared to actual results
`lst result-per-story my_sprint_name`
### Check that your team mates didn't charge wrong projects (date defaults to yesterday)
`lst check-hours -u user1_id user2_id -d 23.03.2013`
### Test LST installation
`lst test-install`
### Check all the sprints defined in your config
`lst ls`
### Search a Zebra user id by employee last name
`lst get-user-id my_last_name`
### Search multiple Zebra user ids by employees last name
`lst get-user-id my_last_name his_last_name her_last_name`
### Get Jira info for config (helper)
`lst jira-config-helper my_story_id`
Useful to fill the Jira part of the config. Give it a story id (JLC-xx) and it will retrieve it's project id and sprint name

## Settings
See the annotated example [.lst_dist.yml](.lst_dist.yml), which shows both a basic example, and a more advanced one. It's copied below for convenience:
```
# in .lst.yml

sprints:

######
# Simplest config
# only mandatory arguments
######
    my_project_sprint_1: # this is the name you'll specify when running any command
        commited_man_days: 30
        zebra:
            client_id: 111 # integer, zebra client id
            activities: '*' # can be either '*' (all activities) or a list of activity ids [1,2,3]
            users: '*' # can be either '*' (all users) or a list of zebra users id [1,2,3]
            start_date : 2012-11-19 # date format yyyy-mm-dd
            end_date : 2012-12-10 # date format yyyy-mm-dd
        jira:
            project_id: 12345 # Run `lst jira-config-helper jlc-100` to get its project id (change jlc-100 by the id of a story in your current sprint)
            sprint_name: "Fix+Version+As+Specified+In+Jira" # as seen in jira query builder (usually blanks are to be replaced with + in jira). Run `lst jira-config-helper jlc-100` to get its sprint name (replace jlc-100 by the id of a story in your current sprint)

######
# Advanced config
# all optional arguments below can be completely deleted if not used
######
    my_project_sprint_2: # this is the name you'll specify when running any command
        commited_man_days: 30
        zebra:
            commit_prefix: jlc- # prefix that you use for all hours pushed to zebra, to identify stories
            client_id: 111 # integer, zebra client id
            activities: '*' # can be either '*' (all activities) or a list of activity ids [1,2,3]
            users: [100,101,102] # can be either '*' (all users) or a list of zebra users id [1,2,3]
            start_date : 2012-11-19 # date format yyyy-mm-dd
            end_date : 2012-12-10 # date format yyyy-mm-dd
            force: # optional, use it to (force/)correct zebra values (this will not change the values *in* zebra, just force them to be displayed as you wish)
              - date: 2012-11-19 # can be either a single date...
                time: 8 # nb of hours. Can be either a number (= force value to 8 hours)...
              - date: [2013-04-09,2013-04-11] # ...or multiple dates (list)
                time: '+8' # ...or a delta string (to be added to the existing zebra value)...
              - date: '2013-04-09/2013-04-11' # ...or a date range (str separated by /)
                time: '-8' # ...in both directions 
            planned: # optional, can be removed alltogether if you don't want to include your planned MD per day
              - date: 2012-11-19 # can be either a single date...
                time: 16 # nb of hours
              - date: [2013-04-09,2013-04-11] # ...or multiple dates (list)
                time: 24
              - date: '2013-04-09/2013-04-11' # ...or a date range (str separated by /)
                time: 24
            planned: [16, 24, 0, 16] # The planned section can also be filled by providing a value for every business day of the sprint
        jira:
            project_id: 12345 # Run `lst jira-config-helper jlc-100` to get its project id (change jlc-100 by the id of a story in your current sprint
            sprint_name: "Fix+Version+As+Specified+In+Jira" # as seen in jira query builder (usually blanks are to be replaced with + in jira). Run `lst jira-config-helper jlc-100` to get its sprint name (replace jlc-100 by the id of a story in your current sprint
            nice_identifier: "(NICE)" # optional, how you specify that a story is a nice to have (must be part of the story title)
            closed_statuses:
                {6: closed, 10008: For PO Review} # optional, what status you consider as 'closed' (used to check if a story is "closed" and to know on what date it was closed reading the story activity stream)
            ignored: ['XXX-501', 'XXX-505'] # optional, list of stories that should be ignored

_current: my_project_sprint_2 # specify default sprint to use
```

## Power tips
* create a _current entry at root level specifying the name of your current sprint `_current: my_sprint_name (<- this
value should be in the `sprints` list) and call `lst sprint-burnup` (without specifying a sprint name)
