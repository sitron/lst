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

## Installation
* `sudo pip install git+git://github.com/sitron/lst@v0.9.0`
* `sudo pip install -r https://raw.github.com/sitron/lst/master/requirements.txt`
* copy the [.lst-secret_dist.yml](.lst-secret_dist.yml) file to you home, rename it to .lst-secret.yml and change your jira/zebra credentials (watch out for the file name: it's [dot]lst-secret.yml
* create a directory somewhere on your machine where you want your graphs to be output and add its path to .lst-secret.yml 
* create a blank file in your home called .lst.yml (`cd && touch .lst.yml`)
* run `lst add-sprint` and answer the interactive questions. This will update your config using the default settings
* run `lst test-install` to test your install. It should dump some html and finish by 'end' (yes! it's working!)
* run `lst ls` to check what sprints are defined in your config
* run `lst sprint-burnup [sprint_name]` and enjoy your first graph!
* if you want to customize your config (to limit the Zebra users to take into account, or override a value or...) have a look at the Settings section below

## Upgrade
if by any chance you already installed LST before, just run:
* `sudo pip install git+git://github.com/sitron/lst@v0.9.0 --upgrade`
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
```
after (from 1.0.0):
```
sprints:
    jlc_col_3:
        commited_man_days: xxx
```

## Available commands
### Fetch data and display a chart
`lst sprint-burnup my_sprint_name`
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
See the annotated example [.lst_dist.yml](.lst_dist.yml)
You will need to define at least 1 sprint to be able to run a command

the config file is a sprint list, each sprint is defined by:

* a name: it can be anything. It's just a shortcut that you'll use to run all commands (that need a sprint name)
* a number of commited man days (integer). Self explanatory.
* some Zebra specific settings:
      * the zebra client id (check in Zebra, usually a 4 digits integer). You can also easily find it by running `taxi search [project_name]` if you have Taxi installed (you should!)
      * a list of Zebra activitity ids (check Zebra) or put '*' (including the quotes) to use all activities
      * a list of Zebra user ids (3 digits integer). You can run `lst get-user-id my_last_name` to get ids out of Zebra
      * a start date (like 2013-01-21)
      * a end date (like 2013-01-22)
      * optional: you can force some static data for Zebra: for example we have an external employee that does not log any hour in Zebra and works 100%. So i know that i need to add 8 hours of work for each day. I can use a date range '2013-01-21/2013-01-25' and '+8' as time to add 8 hours to all days within the date range.
* some Jira specific settings:
      * the Jira project id, usually a 5 digits integer. Run `lst jira-config-helper my_story_id` to get its project id
      * the sprint name: the FixVersion name as seen in Jira Query Builder. Run `lst jira-config-helper my_story_id` to get its sprint name
      * optional, nice\_identifier: if you have "Nice to have" stories in your sprint, you can specify how to recognize them (we use '(NICE)' in the story title)
      * optional, closed_statuses: the jira statuses to consider as 'closed'. During the sprint the stories are usually not closed, so your graph would be flat until the very last day. For example we use "For PO Review" as the "closed" status. Specified as a dictionary where the keys are the status codes, and the values the status names. See the "Advanced config" in [.lst_dist.yml](.lst_dist.yml) to see how it's structured.
      * optional, ignored: a list of stories to ignore. Specify their ids in a list ['XXX-134', 'XXX-119']. Very often we have stories in the sprint that should not be considered for the graph (closed before the sprint, out of scope.. whatever)

All this seems pretty complicated but it's just words... looking at the file itself [.lst_dist.yml](.lst_dist.yml) might just be self explanatory enough...
