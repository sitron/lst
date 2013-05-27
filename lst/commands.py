from remote import ZebraRemote, JiraRemote
from models import JiraEntry, GraphEntry, GraphEntries, AppContainer, ZebraDays, ZebraDay, ZebraManager
from output import SprintBurnUpOutput
from processors import SprintBurnUpJiraProcessor
from errors import *
from helpers import *
import os
import sys
import distutils.sysconfig
import datetime
import dateutil


class BaseCommand:
    def __init__(self):
        self.secret = AppContainer.secret
        self.config = AppContainer.config
        self.dev_mode = AppContainer.dev_mode

    def run(self, args):
        pass

    def get_start_and_end_date(self, dates):
        """
        Get a tuple with start and end dates. Default is none for end date, and last week-day for start_date

        :param dates:list of dates
        :return:tuple (start,end)
        """
        date_objects = [dateutil.parser.parse(d) for d in dates]

        # default values is None for end_date and last week-day for start_date
        start_date = None
        end_date = None
        if date_objects is None or len(date_objects) == 0:
            date_objects.append(DateHelper.get_last_week_day())

        if len(date_objects) == 1:
            start_date = ZebraHelper.zebra_date(date_objects[0])
        if len(date_objects) == 2:
            start_date = ZebraHelper.zebra_date(min(date_objects))
            end_date = ZebraHelper.zebra_date(max(date_objects))

        return (start_date, end_date)

    def get_zebra_remote(self):
        return ZebraRemote(
            self.secret.get_zebra('url'),
            self.secret.get_zebra('username'),
            self.secret.get_zebra('password')
        )


class CheckHoursCommand(BaseCommand):
    """
    Command to retrieve all Zebra hours for a specific date and/or user_id, and group them by project
    Usage:  check-hours [-d date] [-u user_id]
            check-hours [-d date] [-u user1_id user2_id]
            check-hours [-u user_id]
            check-hours [-d date]

    """
    def run(self, args):
        # parse and verify user arguments
        users = InputHelper.sanitize_users(args.user)
        dates = InputHelper.sanitize_dates(args.date)
        InputHelper.ensure_max_2_dates(dates)
        start_date, end_date = self.get_start_and_end_date(dates)

        # get zebra url to call
        report_url = ZebraHelper.get_zebra_url_for_activities(start_date=start_date, end_date=end_date, users=users)

        # retrieve zebra data
        zebra_entries = self._get_zebra_entries(report_url)
        if len(zebra_entries) == 0:
            return

        # print output to console
        self._output(self._group_entries_by_project(zebra_entries))

    def _get_zebra_entries(self, report_url):
        """query zebra to retrieve entries"""
        zebra = self.get_zebra_remote()
        zebra_json_result = zebra.get_data(report_url)
        zebra_entries = zebra.parse_entries(zebra_json_result)
        return zebra_entries

    def _group_entries_by_project(self, entries):
        """group entries by project"""
        return ZebraManager.group_by_project(entries)

    def _output(self, projects):
        # formated output
        print ''
        print 'Projects:'
        zebra_url = self.secret.get_zebra('url')
        for name,entries in projects.items():
            print '- %s' % (name)

            total = 0
            template = "  {time:<12} {username:<23} {description:<45} ({url:<15})"
            for entry in entries:
                d = dict
                d['time'] = str(entry.time) + ' hours'
                d['username'] = entry.username
                d['description'] = entry.description[:44]
                d['url'] = ZebraHelper.get_activity_url(zebra_url, entry.id)
                print template.format(**d)
                total += entry.time

            print '  Total: %s' % (total)
            print ''

class AddSprintCommand(BaseCommand):
    """
    Usage: add-sprint

    """
    def run(self, args):
        name = InputHelper.get_user_input(
            'Give me a nickname for your sprint (no special chars): ',
            str
        )

        sprint = dict
        sprint['commited_man_days'] = InputHelper.get_user_input(
            'Give me the number of commited man days for this sprint: ',
            float
        )

        # add zebra/jira data
        sprint['zebra'] = self._get_zebra_data()
        sprint['jira'] = self._get_jira_data()

        # write to config file
        AppContainer.config.create_sprint(name, sprint)

    def _get_zebra_data(self):
        start_date = InputHelper.get_user_input('Give me the sprint start date (as 2013.02.25): ', 'date')
        end_date = InputHelper.get_user_input('Give me the sprint end date (as 2013.02.25): ', 'date')

        # todo: improve this part
        client_id = InputHelper.get_user_input(
            'Give me the zebra project id (if you use Taxi, just do `taxi search client_name` else check in Zebra. It should be a four digit integer): ',
            int
        )

        zebra_data = dict
        zebra_data['activities'] = '*'
        zebra_data['users'] = '*'
        zebra_data['start_date'] = start_date
        zebra_data['end_date'] = end_date
        zebra_data['client_id'] = client_id

        return zebra_data

    def _get_jira_data(self):
        story = InputHelper.get_user_input(
            'Give me the jira id of any story in your sprint (something like \'jlc-110\'): ',
            str
        ).upper()
        command = RetrieveJiraInformationForConfigCommand()
        story_data = command.get_story_data(story)

        jira_data = {}
        jira_data['project_id'] = int(story_data['project_id'])
        jira_data['sprint_name'] = story_data['clean_sprint_name']

        return jira_data


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
    Usage:  ls lists all sprints defined in config

    """

    def run(self, args):
        print ''
        sprints = self.config.get_sprints()
        if len(sprints) == 0:
            print 'No sprints defined'
        else:
            print 'All currently defined sprints:'
            for k,v in sprints.items():
                print k

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
    Usage:  sprint-burnup [sprint_name]
            sprint-burnup [sprint_name] [-d 2013.01.25]

            date defaults to yesterday

    """

    def run(self, args):
        # make sure the sprint specified exist in config
        user_sprint_name = args.optional_argument[0]
        sprint = self.config.get_sprint(user_sprint_name)
        try:
            print "Sprint %s found in config" % (sprint.name)
        except:
            raise SyntaxError("Sprint %s not found. Make sure it's defined in your settings file" % (user_sprint_name))

        # end date for the graph
        try:
            graph_end_date = dateutil.parser.parse(args.date[0]).date()
        except:
            graph_end_date = datetime.date.today() - datetime.timedelta(days = 1)

        # start fetching zebra data
        print 'Start fetching Zebra'

        zebra = ZebraRemote(self.secret.get_zebra('url'), self.secret.get_zebra('username'), self.secret.get_zebra('password'))

        report_url = self._get_zebra_url_for_sprint_burnup(sprint)
        zebra_json_result = zebra.get_data(report_url)
        # parse response
        zebra_entries = zebra.parse_entries(zebra_json_result)

        # group entries by date
        zebra_days = ZebraDays()

        for zebra_entry in zebra_entries:
            readable_date = zebra_entry.readable_date()

            if readable_date in zebra_days:
                zebra_days[readable_date].entries.append(zebra_entry)
                zebra_days[readable_date].time += zebra_entry.time
            else:
                day = ZebraDay()
                day.time = zebra_entry.time
                day.day = readable_date
                day.entries.append(zebra_entry)
                zebra_days[readable_date] = day

        print 'End Zebra'

        # start fetching jira data
        print 'Start fetching Jira'

        JiraEntry.closed_status_ids = sprint.get_closed_status_codes()
        jira = JiraRemote(self.secret.get_jira('url'), self.secret.get_jira('username'), self.secret.get_jira('password'))

        jira_url = self._get_jira_url_for_sprint_burnup(sprint)
        nice_identifier = sprint.get_jira_data('nice_identifier')
        closed_status_names = sprint.get_closed_status_names()
        ignored_stories = sprint.get_jira_data('ignored')

        # define jira post processor
        post_processor = SprintBurnUpJiraProcessor(closed_status_names, jira)

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

        # get all sprint days
        days = sprint.get_all_days(False)
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

            planned_time = sprint.get_planned_data(str(date))
            planned_str = '' if planned_time is None else '(Planned: ' + str(planned_time) + ')'

            # print total time per day (with and/or without forced values)
            if total_time != 0:
                if time_without_forced == total_time:
                    print 'Total: %s %s' % (total_time, planned_str)
                else:
                    print 'Total (without forced data): %s' % (time_without_forced)
                    print 'Total including forced data: %s %s' % (total_time, planned_str)
                print ''

            # get jira achievement for this day (bv/sp done)
            jira_data = jira_entries.get_achievement_for_day(str(date));

            # if we have some time, story closed for this day or planned time, add it to graph data
            if jira_data is not None or total_time != 0 or planned_time is not None:
                graph_entry = GraphEntry()
                graph_entry.date = date

                if planned_time is not None:
                    graph_entry.planned_time = planned_time

                graph_entry.time = total_time
                try:
                    graph_entry.story_points = jira_data['sp']
                    graph_entry.business_value = jira_data['bv']
                except TypeError, e:
                    pass
                graph_entries[str(date)] = graph_entry

        data = graph_entries.get_ordered_data(graph_end_date)

        # values needed to build the graph
        commited_values = {}
        commited_values['storyPoints'] = jira_entries.get_commited_story_points()
        commited_values['businessValue'] = jira_entries.get_commited_business_value()
        commited_values['manDays'] = sprint.commited_man_days


        # values needed to build the graph
        sprint_data = {}
        sprint_data['startDate'] = sprint.get_zebra_data('start_date').strftime('%Y-%m-%d')
        sprint_data['endDate'] = sprint.get_zebra_data('end_date').strftime('%Y-%m-%d')
        sprint_data['graphEndDate'] = graph_end_date.strftime('%Y-%m-%d')

        # write the graph
        print 'Starting output'
        output = SprintBurnUpOutput(AppContainer.secret.get_output_dir())
        output.output(sprint.name, data, commited_values, sprint_data)

    def _get_zebra_url_for_sprint_burnup(self, sprint):
        users = sprint.get_zebra_data('users')
        client_id = sprint.get_zebra_data('client_id')
        activities = sprint.get_zebra_data('activities')
        start_date = sprint.get_zebra_data('start_date')
        end_date = sprint.get_zebra_data('end_date')

        return ZebraHelper.get_zebra_url_for_activities(start_date, end_date, client_id, users, activities)

    def _get_jira_url_for_sprint_burnup(self, sprint):
        return "/sr/jira.issueviews:searchrequest-xml/temp/SearchRequest.xml?jqlQuery=project+%3D+'" + str(sprint.get_jira_data('project_id')) + "'+and+fixVersion+%3D+'" + sprint.get_jira_data('sprint_name') + "'&tempMax=1000"
