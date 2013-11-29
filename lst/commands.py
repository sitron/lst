import yaml
import os
import sys
import distutils.sysconfig
import datetime
import dateutil
import re

from remote import ZebraRemote, JiraRemote
from models.jiraModels import *
from models.zebraModels import *
from models import *
from output import *
from errors import *
from helpers import *
from parser import ConfigParser
from managers.jiraManager import JiraManager
from managers.zebraManager import ZebraManager


class BaseCommand(object):
    def __init__(self):
        self.secret = AppContainer.secret
        self.config = AppContainer.config
        self.dev_mode = AppContainer.dev_mode

    def add_common_arguments(self, parser):
        parser.add_argument("--dev-mode", action="store_true", help="development mode")
        return parser

    def add_command_arguments(self, subparsers):
        # has to be implemented in all actions
        # the minimum being:
        #   parser = subparsers.add_parser('my-command-name')
        #   return parser
        raise DevelopmentError('Method add_command_arguments must be implemented in all commands')

    def run(self, args):
        pass

    def get_start_and_end_date(self, dates):
        """
        Get a tuple with start and end dates. Default is none for end date, and last week-day for start_date

        :param dates:list of dates
        :return:tuple (start,end)
        """
        date_objects = [dateutil.parser.parse(d, dayfirst=True) for d in dates]

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

    def ensure_sprint_in_config(self, sprint_name):
        """

        :rtype : models.Sprint
        """
        sprint = self.config.get_sprint(sprint_name)
        if sprint is None:
            raise InputParametersError("Sprint %s not found. Make sure it's defined in your settings file" % (sprint_name))

        print "Sprint %s found in config" % (sprint.name)

        return sprint

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

    def get_jira_manager(self):
        return JiraManager(AppContainer)

    def get_zebra_manager(self):
        return ZebraManager(AppContainer)


class ResultPerStoryCommand(BaseCommand):
    """
    Command to check how many hours were burnt per story (within a sprint)
    Usage:  result-per-story  [sprint-name]

    """
    def add_command_arguments(self, subparsers):
        parser = subparsers.add_parser('result-per-story')
        ArgParseHelper.add_sprint_name_argument(parser)
        return parser

    def run(self, args):
        sprint_name = self.get_sprint_name_from_args_or_current(args.sprint_name)
        sprint = self.ensure_sprint_in_config(sprint_name)

        # make sure a commit prefix is defined
        prefix = sprint.get_zebra_data('commit_prefix')
        try:
            regex = re.compile("^" + prefix + "(\d+)", re.IGNORECASE)
        except:
            raise SyntaxError("No commit prefix found in config. Make sure it's defined in your settings file")

        # retrieve jira data
        # to compare estimated story_points to actual MD consumption
        jira_manager = self.get_jira_manager()
        jira_entries = jira_manager.get_stories_for_sprint(sprint)

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
        zebra_manager = self.get_zebra_manager()
        zebra_entries = zebra_manager.get_timesheets_for_sprint(sprint)
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
    def add_command_arguments(self, subparsers):
        parser = subparsers.add_parser('check-hours')
        parser.add_argument(
            "-d", "--date", nargs='*', help="format: -d dd.mm.yyyy. specify either one or two dates (-d start end)"
        )
        ArgParseHelper.add_user_argument(parser)
        return parser

    def run(self, args):
        # parse and verify user arguments
        users = InputHelper.sanitize_users(args.user)
        dates = InputHelper.sanitize_dates(args.date)
        InputHelper.ensure_max_2_dates(dates)
        start_date, end_date = self.get_start_and_end_date(dates)

        # retrieve zebra data
        zebra_manager = self.get_zebra_manager()
        zebra_entries = zebra_manager.get_all_timesheets(
            start_date=start_date,
            end_date=end_date,
            users=users
        )

        if len(zebra_entries) == 0:
            return

        # print output to console
        self._output(
            self._sort_groups_alphabetically(
                zebra_entries.group_by_project()
            ),
            users
        )

    def _sort_groups_alphabetically(self, projects):
        """sort grouped entries alphabetically"""
        return sorted(projects.items(), key=lambda kv: kv[0])

    def _output(self, projects, users=None):
        # formated output
        print ''
        print 'Projects:'
        found_users = []
        zebra_url = self.secret.get_zebra('url')
        for name, entries in projects:
            print '- %s' % name

            total = 0
            template = "  {time:<12} {username:<23} {description:<45} ({url:<15})"
            for entry in entries:
                d = dict()
                d['time'] = str(entry.time) + ' hours'
                d['username'] = entry.username
                if entry.username not in found_users:
                    found_users.append(entry.username)
                d['description'] = entry.description[:44]
                d['url'] = ZebraHelper.get_activity_url(zebra_url, entry.id)
                print template.format(**d)
                total += entry.time

            print '  Total: %s' % (total)
            print ''

        if users is not None:
            if len(users) == len(found_users):
                print '(found entries for all users)'
            else:
                print 'Found entries for %d out of %d users (%s)' % \
                      (len(found_users), len(users), ','.join(found_users))


class AddSprintCommand(BaseCommand):
    """
    Usage: add-sprint

    """
    def add_command_arguments(self, subparsers):
        parser = subparsers.add_parser('add-sprint')
        return parser

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
    def add_command_arguments(self, subparsers):
        parser = subparsers.add_parser('jira-config-helper')
        ArgParseHelper.add_user_story_id_argument(parser)
        return parser

    def run(self, args):
        story_id = args.story_id.upper()

        jira_manager = self.get_jira_manager()
        story = jira_manager.get_story(story_id)
        clean_sprint_name = JiraHelper.sanitize_sprint_name(story.sprint_name)

        self._output(story, clean_sprint_name)

    def _output(self, story, clean_sprint_name):
        print ''
        print 'Project info for story {}'.format(story.id)
        print 'id: {}'.format(story.project_id)
        print 'name: {}'.format(story.project_name)
        print 'sprint name: {}'.format(story.sprint_name)
        print 'sprint name for config: {}'.format(clean_sprint_name)


class ListCommand(BaseCommand):
    """
    Usage:  ls lists all sprints defined in config

    """
    def add_command_arguments(self, subparsers):
        parser = subparsers.add_parser('ls')
        return parser

    def run(self, args):
        print ''
        sprints = self.config.get_sprints()
        if len(sprints) == 0:
            print 'No sprints defined'
        else:
            print 'All currently defined sprints:'
            for k, v in sprints.items():
                print k


class RetrieveUserIdCommand(BaseCommand):
    """
    Usage: get-user-id [last_name] Retrieves the Zebra user id from his/her last name
    """

    def add_command_arguments(self, subparsers):
        parser = subparsers.add_parser('get-user-id')
        parser.add_argument("lastname", nargs='+', help="user(s) lastname")
        return parser

    def run(self, args):
        names = [x.lower() for x in args.lastname]

        zebra_manager = self.get_zebra_manager()
        all_users = zebra_manager.get_all_users()
        if len(all_users) == 0:
            raise SyntaxError(
                "No user found at all! (check that you are connected to internet)"
            )

        users = []
        for user in all_users:
            if user['employee_lastname'].lower() in names:
                users.append(user)

        self._output(users, names)

    def _output(self, users, names):
        if len(users) == 0:
            print 'No user found with lastname {}'.format(', '.join(names))
            return

        for user in users:
            print 'found {} ({}) with id {}'.format(
                user['employee_lastname'],
                user['employee_firstname'],
                user['id']
            )


class TestInstallCommand(BaseCommand):
    """
    Usage:  test-install
            will test the access to static files (html templates)

    """
    def add_command_arguments(self, subparsers):
        parser = subparsers.add_parser('test-install')
        return parser

    def run(self, args):
        print 'Will dump some useful variable to debug'
        print 'My sys.prefix is %s' % sys.prefix
        print 'My modules are installed in %s' % (distutils.sysconfig.get_python_lib())


class SprintBurnUpCommand(BaseCommand):
    """
    Usage:  sprint-burnup [sprint_name]
            sprint-burnup [sprint_name] [-d 2013.01.25]
            sprint-burnup (if _current is set)

            date defaults to yesterday

    """

    def add_command_arguments(self, subparsers):
        parser = subparsers.add_parser('sprint-burnup')
        ArgParseHelper.add_sprint_name_argument(parser)
        ArgParseHelper.add_date_argument(parser)
        return parser

    def run(self, args):
        sprint_name = self.get_sprint_name_from_args_or_current(args.sprint_name)
        sprint = self.ensure_sprint_in_config(sprint_name)

        # end date for the graph can be specified via the --date arg. Defaults to yesterday
        try:
            graph_end_date = dateutil.parser.parse(args.date[0], dayfirst=True).date()
        except:
            graph_end_date = datetime.date.today() - datetime.timedelta(days=1)

        # start fetching zebra data
        print 'Start fetching Zebra'
        zebra_manager = self.get_zebra_manager()
        timesheets = zebra_manager.get_timesheets_for_sprint(sprint)
        sprint.timesheet_collection = timesheets
        zebra_days = timesheets.group_by_day()
        print 'End Zebra'

        # start fetching jira data
        print 'Start fetching Jira'
        Story.closed_status_ids = sprint.get_closed_status_codes()
        jira_manager = self.get_jira_manager()
        stories = jira_manager.get_stories_for_sprint_with_end_date(sprint)
        sprint.story_collection = stories
        print 'End Jira'

        # define x serie
        dates = []

        # define all y series
        serie_collection = SprintBurnupSeries()
        sprint.serie_collection = serie_collection

        # set commited value by serie
        serie_collection.get('md').ideal_value = float(sprint.commited_man_days) * 8
        serie_collection.get('sp').ideal_value = stories.get_commited('sp')
        serie_collection.get('bv').ideal_value = stories.get_commited('bv')

        # loop through all sprint days and gather values
        days = DateHelper.get_all_days(sprint.get_zebra_data('start_date'), sprint.get_zebra_data('end_date'))
        for date in days:
            time_without_forced = 0

            zebra_day = zebra_days.get(str(date))

            if zebra_day is not None:
                time_without_forced = zebra_day.time

            # check for forced zebra values
            total_time = sprint.get_forced_data(str(date), time_without_forced)

            planned_time = sprint.get_planned_data(str(date))

            # output data for this day to the console (useful but not necessary for this command
            if total_time != 0:
                print date

                entries_per_user = zebra_day.get_entries_per_user()
                for user, time in entries_per_user.items():
                    print "%s : %s" % (user, time)

                planned_str = '' if planned_time is None else '(Planned: ' + str(planned_time) + ')'

                # print total time per day (with and/or without forced values)
                if time_without_forced == total_time:
                    print 'Total: %s %s' % (total_time, planned_str)
                else:
                    print 'Total (without forced data): %s' % time_without_forced
                    print 'Total including forced data: %s %s' % (total_time, planned_str)
                print ''
            # end of output

            # get jira achievement for this day (bv/sp done)
            jira_data = stories.get_achievement_for_day(str(date))

            # if we have some time, story closed for this day or planned time, add it to graph data
            if jira_data is not None or total_time != 0 or planned_time is not None:
                dates.append(date)

                for serie in serie_collection.values():
                    # only add data for dates > graph_end_date for "planned" (not md, sp, bv...)
                    if serie.name == 'planned':
                        serie.cumulate(planned_time)
                    elif serie.name == 'md':
                        if date <= graph_end_date:  # for md, sp, bv dont add data if date is after graph_end_date
                            serie.cumulate(total_time)
                    else:
                        if date <= graph_end_date:  # for md, sp, bv dont add data if date is after graph_end_date
                            serie.cumulate(None if jira_data is None else jira_data[serie.name])

        # get only meaningfull series (ie. don't use BV if the team doesnt use it)
        graph_series = serie_collection.get_series_for_chart()

        self._output(sprint, dates, graph_series, graph_end_date)

    def _output(self, sprint, dates, graph_series, graph_end_date):
        # convert all y series to percents
        percent_series = OrderedDict()
        for name, serie in graph_series.items():
            percent_series[name] = serie.get_values_as_percent()

        # add future days (up to graph_end_date) so that the graph looks more realistic
        if sprint.get_zebra_data('end_date') > dates[-1]:
            today = datetime.date.today()
            future_dates = DateHelper.get_future_days(sprint.get_zebra_data('end_date'), dates[-1] != today, False)

            for date in future_dates:
                dates.append(date)

        # generate main graph (sprint burnup)
        chart = SprintBurnUpChart.get_chart(dates, percent_series)

        # generate top graphs (result per serie)
        top_graph_series = ['md', 'sp', 'bv']
        result_charts = {}

        for name, serie in graph_series.items():
            if name in top_graph_series:
                result_charts[name] = ResultPerValuePie.get_chart((serie.get_max_value(), serie.get_commited_value()))

        # collect all needed values for graph output
        args = list()
        args.append('{} ({})'.format(sprint.get_jira_data('sprint_name').replace('+', ' '), sprint.name))
        args.append(
            'Velocity: actual: {:.2f} expected: {:.2f}'.format(
                sprint.get_actual_velocity(), sprint.get_expected_velocity()
            )
        )
        for name in result_charts:
            serie = graph_series.get(name)
            args.append('{serie_name} {percent:.0f}%<br/>({result:.0f}/{max_value:.0f})'.format(
                serie_name=serie.name.upper(),
                percent=serie.get_result_as_percent(),
                result=serie.get_max_value(),
                max_value=serie.get_commited_value(),
            ))
            args.append(result_charts[name].render(is_unicode=True))
        args.append(chart.render(is_unicode=True))

        # embed the graphs in html
        content = SprintBurnUpChart.get_sprint_burnup_html_structure(result_charts.keys()).format(*args)

        # write the graph to file
        path = 'sprint_burnup-%s-%s.html' % (
            Helper.slugify(sprint.name),
            datetime.datetime.now().strftime("%Y%m%d")
        )
        graph_location = OutputHelper.output(path, content)
        print 'Your graph is available at %s' % graph_location


class GetLastZebraDayCommand(BaseCommand):
    """
    Usage:  get-last-zebra-day [sprint_name]

    Get the last day for which data was pushed to zebra (on specified sprint)
    """
    def add_command_arguments(self, subparsers):
        parser = subparsers.add_parser('get-last-zebra-day')
        ArgParseHelper.add_sprint_name_argument(parser)
        return parser

    def run(self, args):
        sprint_name = self.get_sprint_name_from_args_or_current(args.sprint_name)
        sprint = self.ensure_sprint_in_config(sprint_name)

        # force sprint end_date to today
        end_date = datetime.date.today()
        sprint.zebra_data['end_date'] = end_date

        zebra_manager = self.get_zebra_manager()
        zebra_entries = zebra_manager.get_timesheets_for_sprint(sprint)
        last_entry = zebra_entries[-1]

        self._output(sprint_name, last_entry)

    def _output(self, sprint_name, last_entry):
        print ''
        print 'last date for sprint {}: {}'.format(sprint_name, last_entry.readable_date())


class EditCommand(BaseCommand):

    def add_command_arguments(self, subparsers):
        parser = subparsers.add_parser('edit')
        return parser

    def run(self, args):

        # Open the config file
        FileHelper.open_for_edit(AppContainer.SETTINGS_PATH)

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
                    print "Error in sprint [{}] definition: ".format(name), e
                    error = True
        if error is False:
            print 'Well done, no error detected!'


class DumpSprintConfigCommand(BaseCommand):
    """
    Command to easily dump a sprint config (ie. to share with someone/wiki)
    Usage:  dump-sprint-config [sprint-name]
            dump-sprint-config (if _current is set in your config)

    """
    def add_command_arguments(self, subparsers):
        parser = subparsers.add_parser('dump-sprint-config')
        ArgParseHelper.add_sprint_name_argument(parser)
        return parser

    def run(self, args):
        sprint_name = self.get_sprint_name_from_args_or_current(args.sprint_name)
        self.ensure_sprint_in_config(sprint_name)
        sprint_data = self.config.get_sprint(sprint_name, raw=True)
        wrapper = {'sprints': {sprint_name: sprint_data}}

        self._output(wrapper)

    def _output(self, wrapper):
        print ''
        print yaml.dump(wrapper, default_flow_style=False)
