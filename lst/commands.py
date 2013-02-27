from remote import ZebraRemote
from remote import JiraRemote
from models import JiraEntry
from models import JiraEntries
from models import GraphEntry
from models import GraphEntries
from models import AppContainer
from output import SprintBurnUpOutput
from processors import SprintBurnUpJiraProcessor
from parser import ConfigParser
import pkgutil
import os
import sys
import distutils.sysconfig
import yaml
from pprint import pprint
import datetime

class BaseCommand:
    def __init__(self):
        self.secret = AppContainer.secret
        self.config = AppContainer.config
        self.dev_mode = AppContainer.dev_mode

    def run(self):
        pass

class AddSprintCommand(BaseCommand):
    """
    Usage: add-sprint

    """
    def run(self, args):
        project = {}

        existing_projects = AppContainer.config.get_projects()
        choice = 0
        if len(existing_projects) != 0:
            print ''
            print 'Which project should this sprint belong to?'
            print '%s - None, create a new project' % (0)
            for index, p in enumerate(existing_projects):
                print '%s - %s' % (index + 1, p['name'])
            choice = int(raw_input('Your choice (0, 1, etc..): '))

        if choice == 0:
            # add project data
            name = raw_input('Give me a nickname for your project (no special chars): ')
            project['name'] = name
        else:
            project = AppContainer.config.get_raw_project(existing_projects[choice - 1]['name'])

        # add sprint data
        sprint = {}
        nb_mandays = float(raw_input('Give me the number of commited man days for this sprint: '))
        sprint['commited_man_days'] = nb_mandays

        try:
            sprints = project['sprints']
            sprint['index'] = len(sprints) + 1
        except:
            sprints = list()
            sprint['index'] = 1

        sprints.append({'sprint': sprint})
        project['sprints'] = sprints

        # add zebra data
        #start = raw_input('Give me the sprint start date (as 2013.02.25): ')
        start = '2013.02.25'
        [y,m,d] = map(int, start.split('.'))
        start_date = datetime.date(y,m,d)
        #end = raw_input('Give me the sprint end date (as 2013.02.25): ')
        end = '2013.02.26'
        [y,m,d] = map(int, end.split('.'))
        end_date = datetime.date(y,m,d)

        # todo: improve this part
        #client = raw_input('Give me the zebra project id (if you use Taxi, just do `taxi search client_name` else check in Zebra. It should be a four digit integer): ')
        client = 1296
        client_id = int(client)

        zebra_data = {}
        zebra_data['activities'] = '*'
        zebra_data['users'] = '*'
        zebra_data['start_date'] = start_date
        zebra_data['end_date'] = end_date
        zebra_data['client_id'] = client_id
        sprint['zebra'] = zebra_data

        jira_data = {}
        #story = raw_input('Give me the jira id of any story in your sprint (something like \'jlc-110\'): ').upper()
        story = 'jlc-567'
        command = RetrieveJiraInformationForConfigCommand()
        story_data = command.get_story_data(story)

        jira_data['project_id'] = int(story_data['project_id'])
        jira_data['sprint_name'] = story_data['clean_sprint_name']
        sprint['jira'] = jira_data

        # write to config file
        AppContainer.config.create_project(project)

class RetrieveJiraInformationForConfigCommand(BaseCommand):
    """
    Usage: jira-config-helper [story-id] (ie: get-project-id JLC-1)

    """
    def run(self, args):
        story_id = args.optional_argument[0].upper()
        story_data = self.get_story_data(story_id)

        print ''
        print 'Project info for story %s' % (story_id)
        print 'id: %s' % (story_data['project_id'])
        print 'name: %s' % (story_data['project_name'])
        print 'sprint name: %s' % (story_data['sprint_name'])
        print 'sprint name for config: %s' % (story_data['clean_sprint_name'])

    def get_story_data(self, story_id):
        jira = JiraRemote(self.secret.get_jira('url'), self.secret.get_jira('username'), self.secret.get_jira('password'))
        url = jira.get_url_for_project_lookup(story_id)
        xml_data = jira.get_data(url)
        story_data = jira.parse_story(xml_data)
        story_data['clean_sprint_name'] = story_data['sprint_name'].replace(' ', '+')
        return story_data

class ListCommand(BaseCommand):
    """
    Usage:  ls lists all projects defined in config
            ls [-p project_id] lists all sprints defined in config for this project

    """

    def run(self, args):
        if args.project is not None:
            # list all sprints for this project
            print ''
            print 'All sprints defined for project %s:' % (args.project)
            for s in self.config.get_project(args.project).sprints.values():
                print 'index: %s' % (s.index)
                print 'commited man days: %s' % (s.commited_man_days)
                print ''
        else:
            # list all projects
            print ''
            print 'All currently defined projects:'
            for p in self.config.get_projects():
                print p['name']

class RetrieveUserIdCommand(BaseCommand):
    """
    Usage: get-user-id [-n last_name] Retrieves the Zebra user id from his/her last name
    """

    def run(self, args):
        # interactive command to retrieve a user id from his/her lastname
        if len(args.optional_argument) == 0:
            raise SyntaxError("To get a user id you need to specify his/her last name (ie: 'lst get-user-id last_name')")

        names = [x.lower() for x in args.optional_argument]
        report_url = 'user/.json'
        zebra = ZebraRemote(self.secret.get_zebra('url'), self.secret.get_zebra('username'), self.secret.get_zebra('password'))
        zebra_json_result = zebra.get_data(report_url)
        zebra_users = zebra.parse_users(zebra_json_result)
        if len(zebra_users) == 0:
            raise SyntaxError("No user found (at all!) check that you are connected to internet")

        users = []
        for user in zebra_users:
            if user['employee_lastname'].lower() in names:
                users.append(user)
                print 'found %s (%s) with id %s' % (user['employee_lastname'], user['employee_firstname'], user['id'])
        if len(users) == 0:
            print 'No user found with lastname %s' % (args.optional_argument)

class TestInstallCommand(BaseCommand):
    """
    Usage:  test-install
            will test the access to static files (html templates)

    """

    def run(self, args):
        print 'Will dump some useful variable to debug'
        print 'My sys.prefix is %s' % (sys.prefix)
        print 'My modules are installed in %s' % (distutils.sysconfig.get_python_lib())

        print 'Will now try to access the copied static files (development mode is %s)' % ('ON' if self.dev_mode else 'OFF')
        if self.dev_mode:
            template_dir = 'lst/html_templates'
        else:
            template_dir = os.path.join(distutils.sysconfig.get_python_lib(), 'lst', 'html_templates')
        file_path = os.path.join(template_dir, 'test.html')
        file_stream = open(file_path)
        file_content = file_stream.read()
        file_stream.close()
        print file_content
        print 'end'

class SprintBurnUpCommand(BaseCommand):
    """
    Usage:  sprint-burnup [-p project_id] (uses last sprint defined in this project)
            sprint-burnup [-p project_id] [-i sprint_index]

    """

    def run(self, args):
        # make sure the project and sprint specified exist in config
        project = self.config.get_project(args.project)
        try:
            print "Project %s found in config" % (project.name)
        except:
            raise SyntaxError("Project %s not found. Make sure it's defined in your settings file" % (args.project))

        if project.has_sprints() == False:
            raise SyntaxError("There is no sprint defined in your config for the project %s" % (project.name))

        sprint = project.get_sprint(args.sprint_index, True)
        try:
            if sprint.index == args.sprint_index:
                print "Sprint %s found in config" % (sprint.index)
            else:
                print "No sprint with index %s found in config, taking %s as default" % (args.sprint_index, sprint.index)

        except:
            if args.sprint_index is None:
                raise SyntaxError("You have more than 1 sprint for the project %s. Please use the -s option to specify the one you'd like to use" % (project.name))
            else:
                raise SyntaxError("There is no sprint with the index %s defined in your config for the project %s" % (args.sprint_index, project.name))

        # start fetching zebra data
        print 'Start fetching Zebra'

        zebra = ZebraRemote(self.secret.get_zebra('url'), self.secret.get_zebra('username'), self.secret.get_zebra('password'))

        report_url = self._get_zebra_url_for_sprint_burnup(sprint)
        zebra_json_result = zebra.get_data(report_url)
        # parse response
        zebra_days = zebra.parse_entries(zebra_json_result)

        print 'End Zebra'

        # start fetching jira data
        print 'Start fetching Jira'

        JiraEntry.closed_status = set(sprint.get_closed_status_codes())
        jira = JiraRemote(self.secret.get_jira('url'), self.secret.get_jira('username'), self.secret.get_jira('password'))

        jira_url = self._get_jira_url_for_sprint_burnup(sprint)
        nice_identifier = sprint.get_jira_data('nice_identifier')
        closed_status = sprint.get_closed_status_name()
        ignored_stories = sprint.get_jira_data('ignored')

        # define jira post processor
        post_processor = SprintBurnUpJiraProcessor(closed_status, jira)

        jira_xml_result = jira.get_data(jira_url)

        jira_entries = jira.parse_stories(
            jira_xml_result,
            nice_identifier,
            ignored_stories,
            post_processor
        )

        print 'End Jira'

        print 'Mixing retrieved values'

        graph_entries = GraphEntries()

        print ''
        print 'Zebra output per day:'

        # get all sprint days until today
        days = sprint.get_all_days(True)
        for date in days:
            total_time = 0
            time_without_forced = 0
            try:
                zebra_day = zebra_days[str(date)]
                print date

                # output nb of hours for each person for this day
                entries_per_user = zebra_day.get_entries_per_user()
                for user,time in entries_per_user.items():
                    print "%s : %s" % (user, time)
                time_without_forced = zebra_day.time
                # check for forced zebra values
                total_time = sprint.get_forced_data(str(date), zebra_day.time)

            except KeyError, e:
                total_time = sprint.get_forced_data(str(date), 0)
                if total_time != 0:
                    print date

            # print total time per day (with and/or without forced values)
            if total_time != 0:
                if time_without_forced == total_time:
                    print 'Total: %s' % (total_time)
                else:
                    print 'Total (without forced data): %s' % (time_without_forced)
                    print 'Total including forced data: %s' % (total_time)
                print ''

            # get jira achievement for this day (bv/sp done)
            jira_data = jira_entries.get_achievement_for_day(str(date));

            # if we have some time or story closed for this day add it to graph data
            if jira_data is not None or total_time != 0:
                graph_entry = GraphEntry()
                graph_entry.time = total_time
                try:
                    graph_entry.story_points = jira_data['sp']
                    graph_entry.business_value = jira_data['bv']
                except TypeError, e:
                    pass
                graph_entries[str(date)] = graph_entry

        data = graph_entries.get_ordered_data()

        # values needed to build the graph
        commited_values = {}
        commited_values['storyPoints'] = jira_entries.get_commited_story_points()
        commited_values['businessValue'] = jira_entries.get_commited_business_value()
        commited_values['manDays'] = sprint.commited_man_days

        # values needed to build the graph
        sprint_data = {}
        sprint_data['startDate'] = sprint.get_zebra_data('start_date').strftime('%Y-%m-%d')
        sprint_data['endDate'] = sprint.get_zebra_data('end_date').strftime('%Y-%m-%d')

        # write the graph
        print 'Starting output'
        output = SprintBurnUpOutput(AppContainer.secret.get_output_dir())
        output.output(project.name, sprint.index, data, commited_values, sprint_data)

    def _get_zebra_url_for_sprint_burnup(self, sprint):
        report_url = 'timesheet/report/.json?option_selector='

        users = sprint.get_zebra_data('users')
        client_id = sprint.get_zebra_data('client_id')
        activities = sprint.get_zebra_data('activities')
        start_date = sprint.get_zebra_data('start_date')
        end_date = sprint.get_zebra_data('end_date')

        if type(users) == list:
            for user in users:
                report_url += '&users[]=' + `user`
        else:
            report_url += '&users[]=' + str(users)

        if type(activities) == list:
            for activity in activities:
                report_url += '&activities[]=' + `activity`
        else:
            report_url += '&activities[]=' + str(activities)

        report_url += '&projects[]=' + `client_id`
        report_url += '&start=' + str(start_date)
        report_url += '&end=' + str(end_date)

        return report_url

    def _get_jira_url_for_sprint_burnup(self, sprint):
        return "/sr/jira.issueviews:searchrequest-xml/temp/SearchRequest.xml?jqlQuery=project+%3D+'" + str(sprint.get_jira_data('project_id')) + "'+and+fixVersion+%3D+'" + sprint.get_jira_data('sprint_name') + "'&tempMax=1000"

