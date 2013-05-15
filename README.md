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
* easy installation (Python (and pip) is your friend)
* easy setup (aka _no_ setup)
* easy configuration (edit a yml file)
* new! even easier configuration (through interactive questions)
* new! add MD forecast day by day with the new "planned" config param

## Installation
* `sudo pip install git+git://github.com/sitron/lst@v1.1.1`
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
* `sudo pip install git+git://github.com/sitron/lst@v1.1.1 --upgrade`
* special instructions for pre-0.9x users: config has changed. There is no "project" level anymore. You can easily update your config by removing the project level, and renaming your sprint index with a name property.

before (prior to 0.9.0):
```
projects:
    - project:
        name: jlc_col
        sprints:
            - sprint:
                index: 3
```
after (from 1.0.0):
```
sprints:
    jlc_col_3:
        commited_man_days: xxx
```
* special instructions for 0.9.0 users: config has changed again! In the main config, the sprint list is now a dictionary, keyed by sprint name. Just change your config as following:

before (in 0.9.0):
```
sprints:
- name: jlc_col_3
  commited_man_days: xxx
```
after (from 1.0.0):
```
sprints:
    jlc_col_3:
        commited_man_days: xxx
```
* special instructions for 1.0.0 users using the obscure "force" parameter. Its syntax is now easier:

before (in 1.0.0):
```
force:
  - static:
        date: 2013-04-17
        time: xxx
```
after (from 1.0.1):
```
force:
  - date: 2013-04-17
    time: xxx
```

## Available commands
### Fetch data and display a chart (by default displays values up to yesterday)
`lst sprint-burnup my_sprint_name`
### Fetch data and display a chart up to a specific date
`lst sprint-burnup my_sprint_name -d 2013.05.01
### Add a sprint to your config (interactive command)
`lst add-sprint`
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
        jira:
            project_id: 12345 # Run `lst jira-config-helper jlc-100` to get its project id (change jlc-100 by the id of a story in your current sprint
            sprint_name: "Fix+Version+As+Specified+In+Jira" # as seen in jira query builder (usually blanks are to be replaced with + in jira). Run `lst jira-config-helper jlc-100` to get its sprint name (replace jlc-100 by the id of a story in your current sprint
            nice_identifier: "(NICE)" # optional, how you specify that a story is a nice to have (must be part of the story title)
            closed_statuses:
                {6: closed, 10008: For PO Review} # optional, what status you consider as 'closed' (used to check if a story is "closed" and to know on what date it was closed reading the story activity stream)
            ignored: ['XXX-501', 'XXX-505'] # optional, list of stories that should be ignored
```
If you prefer a text version:  
the config file is a sprint dictionary, keyed by sprint name. Each sprint is defined by:

* a name: it can be anything. It's just a shortcut that you'll use to run all commands (which need a sprint name)
* a number of commited man days (integer). Self explanatory.
* some Zebra specific settings:
      * the zebra client id (check in Zebra, usually a 4 digits integer). You can also easily find it by running `taxi search [project_name]` if you have Taxi installed (you should!)
      * a list of Zebra activitity ids (check Zebra) or put '*' (including the quotes) to use all activities
      * a list of Zebra user ids (3 digits integer). You can run `lst get-user-id my_last_name` to get ids out of Zebra
      * a start date (like 2013-01-21)
      * a end date (like 2013-01-22)
      * optional: you can force some static data for Zebra: for example we have an external employee that does not log any hour in Zebra and works 100%. So i know that i need to add 8 hours of work for each day. I can use a date range '2013-01-21/2013-01-25' and '+8' as time to add 8 hours to all days within the date range.
* some Jira specific settings:
      * optional: you can add your forecast, day by day. This is very useful if you have non linear MD consumption (everybody is off on Wednesday for ex.) so that you know if your MD consumption corresponds to reality. You can use a date range '2013-01-21/2013-01-25' or a list of dates [2013-01-21,2013-01-23] or a single date 2013-01-21 and a time value (int) in planned hours
      * the Jira project id, usually a 5 digits integer. Run `lst jira-config-helper my_story_id` to get its project id
      * the sprint name: the FixVersion name as seen in Jira Query Builder. Run `lst jira-config-helper my_story_id` to get its sprint name
      * optional, nice\_identifier: if you have "Nice to have" stories in your sprint, you can specify how to recognize them (we use '(NICE)' in the story title)
      * optional, closed_statuses: the jira statuses to consider as 'closed'. During the sprint the stories are usually not closed, so your graph would be flat until the very last day. For example we use "For PO Review" as the "closed" status. Specified as a dictionary where the keys are the status codes, and the values the status names. See the "Advanced config" in [.lst_dist.yml](.lst_dist.yml) to see how it's structured.
      * optional, ignored: a list of stories to ignore. Specify their ids in a list ['XXX-134', 'XXX-119']. Very often we have stories in the sprint that should not be considered for the graph (closed before the sprint, out of scope.. whatever)
