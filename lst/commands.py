from remote import ZebraRemote, JiraRemote
from models import *
from output import *
from processors import SprintBurnUpJiraProcessor
from errors import *
from helpers import *
import os
import sys
import distutils.sysconfig
import datetime
import dateutil
import re
from pprint import pprint
from parser import ConfigParser


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

    def get_jira_remote(self):
        return JiraRemote(
            self.secret.get_jira('url'),
            self.secret.get_jira('username'),
            self.secret.get_jira('password')
        )

    def get_story_data(self, story_id):
        url = JiraHelper.get_url_for_project_lookup_by_story_id(story_id)
        jira = self.get_jira_remote()
        xml_data = jira.get_data(url)
        story_data = jira.parse_story(xml_data)
        story_data['clean_sprint_name'] = JiraHelper.sanitize_sprint_name(story_data['sprint_name'])
        return story_data

    def ensure_sprint_in_config(self, sprint_name):
        """

        :rtype : models.Sprint
        """
        sprint = self.config.get_sprint(sprint_name)
        if sprint is None:
            raise InputParametersError("Sprint %s not found. Make sure it's defined in your settings file" % (sprint_name))

        print "Sprint %s found in config" % (sprint.name)

        return sprint

    def ensure_optional_argument_is_present(self, optional_arguments, message='Missing parameter'):
        if type(optional_arguments) != list or len(optional_arguments) == 0:
            raise InputParametersError(message)

    def get_sprint_name_from_args_or_current(self, optional_argument):
        """
        get a sprint name by parsing command args or by using _current sprint in config

        :param optional_argument:list user input arguments
        :return: string sprint name
        """
        if len(optional_argument) != 0:
            sprint_name = optional_argument[0]
        else:
            sprint_name = self.config.get_current_sprint_name()

        return sprint_name

    def _get_zebra_url_for_sprint_burnup(self, sprint):
        users = sprint.get_zebra_data('users')
        client_id = sprint.get_zebra_data('client_id')
        activities = sprint.get_zebra_data('activities')
        start_date = sprint.get_zebra_data('start_date')
        end_date = sprint.get_zebra_data('end_date')

        return ZebraHelper.get_zebra_url_for_activities(start_date, end_date, client_id, users, activities)

    def _get_jira_url_for_sprint_burnup(self, sprint):
        return "/sr/jira.issueviews:searchrequest-xml/temp/SearchRequest.xml?jqlQuery=project+%3D+'" + str(sprint.get_jira_data('project_id')) + "'+and+fixVersion+%3D+'" + sprint.get_jira_data('sprint_name') + "'&tempMax=1000"


class ResultPerStoryCommand(BaseCommand):
    """
    Command to check how many hours were burnt per story (within a sprint)
    Usage:  result-per-story  [sprint-name]

    """
    def run(self, args):
        sprint_name = self.get_sprint_name_from_args_or_current(args.optional_argument)
        sprint = self.ensure_sprint_in_config(sprint_name)

        # make sure a commit prefix is defined
        prefix = sprint.get_zebra_data('commit_prefix')
        try:
            regex = re.compile("^" + prefix + "(\d+)",re.IGNORECASE)
        except:
            raise SyntaxError("No commit prefix found in config. Make sure it's defined in your settings file")

        # retrieve jira data
        # to compare estimated story_points to actual MD consumption
        jira = self.get_jira_remote()
        jira_url = self._get_jira_url_for_sprint_burnup(sprint)
        jira_xml_result = jira.get_data(jira_url)
        jira_entries = jira.parse_stories(
            jira_xml_result,
            ignored = sprint.get_jira_data('ignored')
        )

        # extract the integer from the story id
        jira_id_only_regex = re.compile("-(\d+)$")
        jira_values = {}
        max_story_points = 0
        for entry in jira_entries:
            story_id = jira_id_only_regex.findall(entry.id)[0]
            jira_values[story_id] = entry.story_points
            max_story_points += entry.story_points

        # calculate the ideal velocity
        commit = float(sprint.commited_man_days)
        velocity = max_story_points / commit

        # retrieve zebra data
        zebra = ZebraRemote(self.secret.get_zebra('url'), self.secret.get_zebra('username'), self.secret.get_zebra('password'))
        report_url = self._get_zebra_url_for_sprint_burnup(sprint)
        zebra_json_result = zebra.get_data(report_url)
        zebra_entries = zebra.parse_entries(zebra_json_result)
        if len(zebra_entries) == 0:
            return

        # group zebra results by story
        zebra_values = {}
        total_hours = 0
        for entry in zebra_entries:
            story_id = None if regex.match(entry.description) is None else regex.findall(entry.description)[0]
            if story_id is None:
                story_id = 'other'
            try:
                zebra_values[str(story_id)] += entry.time
            except KeyError:
                zebra_values[str(story_id)] = entry.time
            total_hours += entry.time

        # merge zebra/jira data
        jira_keys = jira_values.keys()
        zebra_keys = zebra_values.keys()
        all_keys = jira_keys + list(set(zebra_keys) - set(jira_keys))

        # create an object to hold all values for js
        js_data = [];

        print ''
        print 'Results (planned velocity %s):' % (str(velocity))
        for story_id in all_keys:
            hours_burnt = zebra_values.get(story_id, 0)
            md_burnt = hours_burnt / 8
            planned_story_points = jira_values.get(story_id, 0)
            planned_md = planned_story_points / velocity
            planned_hours = planned_md * 8

            result_percent = 0 if planned_md == 0 else (md_burnt / planned_md) * 100

            print '%s \t%.2f/%.1f MD\t(%d/%d hours)\t%d%%' % (story_id, md_burnt, planned_md, hours_burnt, planned_hours, result_percent)

            # add to js data object
            js_data.append({
                'id': story_id,
                'md_burnt': md_burnt,
                'md_planned': planned_md,
                'hours_burnt': hours_burnt,
                'hours_planned': planned_hours,
                'result_percent': result_percent
            })

        print ''
        print 'Total\t%.2f/%.1f MD\t(%d/%d hours)\t%d%%' % (total_hours / 8, commit, total_hours, commit * 8, (total_hours / (commit * 8)) * 100)
        print ''

        # write the graph
        print 'Starting chart output'
        output = ResultPerStoryOutput(AppContainer.secret.get_output_dir())
        output.output(sprint.name, js_data)


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
        report_url = ZebraHelper.get_zebra_url_for_activities(
            start_date=start_date,
            end_date=end_date,
            users=users,
            project_type_to_consider='all'
        )

        # retrieve zebra data
        zebra_entries = self._get_zebra_entries(report_url)
        if len(zebra_entries) == 0:
            return

        # print output to console
        self._output(
            self._sort_groups_alphabetically(
                self._group_entries_by_project(zebra_entries)
            )
        )

    def _get_zebra_entries(self, report_url):
        """query zebra to retrieve entries"""
        zebra = self.get_zebra_remote()
        zebra_json_result = zebra.get_data(report_url)
        zebra_entries = zebra.parse_entries(zebra_json_result)
        return zebra_entries

    def _group_entries_by_project(self, entries):
        """group entries by project"""
        return ZebraManager.group_by_project(entries)

    def _sort_groups_alphabetically(self, projects):
        """sort grouped entries alphabetically"""
        return sorted(projects.items(), key=lambda kv: kv[0])

    def _output(self, projects):
        # formated output
        print ''
        print 'Projects:'
        zebra_url = self.secret.get_zebra('url')
        for name,entries in projects:
            print '- %s' % (name)

            total = 0
            template = "  {time:<12} {username:<23} {description:<45} ({url:<15})"
            for entry in entries:
                d = dict()
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
    # @todo: to be tested
    def run(self, args):
        name = InputHelper.get_user_input(
            'Give me a nickname for your sprint (no special chars): ',
            str
        )

        sprint = dict()
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

        zebra_data = dict()
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
        story_data = self.get_story_data(story)

        jira_data = {}
        jira_data['project_id'] = int(story_data['project_id'])
        jira_data['sprint_name'] = story_data['clean_sprint_name']

        return jira_data


class RetrieveJiraInformationForConfigCommand(BaseCommand):
    """
    Usage: jira-config-helper [story-id] (ie: jira-config-helper jlc-112)

    """
    def run(self, args):
        try:
            story_id = args.optional_argument[0].upper()
        except:
            raise InputParametersError('Specify a story id, something like \'jira-config-helper jlc-112\'')

        # retrieve data from jira
        story_data = self.get_story_data(story_id)

        print ''
        print 'Project info for story %s' % (story_id)
        print 'id: %s' % (story_data['project_id'])
        print 'name: %s' % (story_data['project_name'])
        print 'sprint name: %s' % (story_data['sprint_name'])
        print 'sprint name for config: %s' % (story_data['clean_sprint_name'])


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
            sprint-burnup (if _current is set)

            date defaults to yesterday

    """

    def run(self, args):
        sprint_name = self.get_sprint_name_from_args_or_current(args.optional_argument)
        sprint = self.ensure_sprint_in_config(sprint_name)

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
            jira_data = jira_entries.get_achievement_for_day(str(date))

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


class GetLastZebraDayCommand(BaseCommand):
    """
    Usage:  get-last-zebra-day [sprint_name]

    """

    def run(self, args):
        sprint_name = self.get_sprint_name_from_args_or_current(args.optional_argument)
        sprint = self.ensure_sprint_in_config(sprint_name)

        url = ZebraHelper.get_zebra_url_for_sprint_last_day(sprint)

        # fetch zebra data
        last_zebra_entry = self.get_last_zebra_entry(url)

        # get last entry and return its date
        print ''
        print 'last date in sprint \'%s\': %s' % (sprint.name, last_zebra_entry.readable_date())

    def get_last_zebra_entry(self, url):
        zebra = self.get_zebra_remote()
        zebra_json_result = zebra.get_data(url)
        zebra_entries = zebra.parse_entries(zebra_json_result)
        return zebra_entries[-1]

class EditCommand(BaseCommand):
    def run(self, args):

        # Open the config file
        os.system("vi "+ AppContainer.SETTINGS_PATH)

        # Validate it
        print "Start validation"
        parser = ConfigParser()
        parser.load_config(AppContainer.SETTINGS_PATH)
        sprints = self.config.get_sprints()
        error = False
        if len(sprints) == 0:
            print 'No sprints defined'
            error = True
        else:
            for name, data in sprints.items():
                try:
                    parser.parse_sprint(name, data)
                except Exception as e:
                    print "Error in sprint [" + name + "] definition: ", e
                    error = True
        if error is False:
            print 'Well done, no error detected!'