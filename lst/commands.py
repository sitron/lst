from remote import ZebraRemote
from remote import JiraRemote
from models import JiraEntry
from models import JiraEntries
from models import GraphEntry
from models import GraphEntries
from models import AppContainer
from output import SprintBurnUpOutput
from processors import SprintBurnUpJiraProcessor
import pkgutil
import os
import sys
import distutils.sysconfig

class BaseCommand:
    def __init__(self):
        self.secret = AppContainer.secret
        self.config = AppContainer.config
        self.dev_mode = AppContainer.dev_mode

    def run(self):
        pass

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
        if args.name is None:
            raise SyntaxError("To get a user id you need to specify his/her last name (using the -n option)")

        names = [x.lower() for x in args.name]
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
            print 'No user found with lastname %s' % (args.name)

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

        print 'Start fetching Zebra'

        zebra = ZebraRemote(self.secret.get_zebra('url'), self.secret.get_zebra('username'), self.secret.get_zebra('password'))

        report_url = self._get_zebra_url_for_sprint_burnup(sprint)
        zebra_json_result = zebra.get_data(report_url)
        # parse response
        zebra_days = zebra.parse_entries(zebra_json_result)

        # check for forced zebra values
        for (key,value) in zebra_days.iteritems():
            value.time = sprint.get_forced_data(key, value.time)

        print 'End Zebra'

        print 'Start fetching Jira'

        JiraEntry.closed_status = set(sprint.get_closed_status_codes())
        jira = JiraRemote(self.secret.get_jira('url'), self.secret.get_jira('username'), self.secret.get_jira('password'))

        jira_url = self._get_jira_url_for_sprint_burnup(sprint)
        nice_identifier = sprint.get_jira_data('nice_identifier')
        closed_status = sprint.get_closed_status_name()
        ignored_stories = sprint.get_jira_data('ignored')

        # define jira post processor
        post_processor = SprintBurnUpJiraProcessor(closed_status, jira)

        jira_entries = jira.get_data(
            jira_url,
            nice_identifier,
            ignored_stories,
            post_processor
        )

        print 'End Jira'

        print 'Mixing retrieved values'
        graph_entries = GraphEntries()
        for day,z in zebra_days.items():
            graph_entry = GraphEntry()
            graph_entry.time = z.time
            graph_entries[day] = graph_entry
        for day,j in jira_entries.get_achievement_by_day().items():
            graph_entry = graph_entries.get(day, GraphEntry())
            graph_entry.story_points = j['sp']
            graph_entry.business_value = j['bv']
            graph_entries[day] = graph_entry

        data = graph_entries.get_ordered_data()

        commited_values = {}
        commited_values['storyPoints'] = jira_entries.get_commited_story_points()
        commited_values['businessValue'] = jira_entries.get_commited_business_value()
        commited_values['manDays'] = sprint.commited_man_days

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
        return "/sr/jira.issueviews:searchrequest-xml/temp/SearchRequest.xml?jqlQuery=project+%3D+'" + sprint.get_jira_data('project_name') + "'+and+fixVersion+%3D+'" + sprint.get_jira_data('sprint_name') + "'&tempMax=1000"

