from lst.commands import BaseCommand
from lst.helpers import ArgParseHelper, DateHelper, UrlHelper
from lst.models.jiraModels import Story
from lst.output import SprintBurnUpChart, SprintBurnupHtmlOutput, OutputHelper, ResultPerValuePie
from lst.models import SprintBurnupSeries

from collections import OrderedDict
import dateutil
import datetime


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
        except Exception as e:
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
        days = DateHelper.get_all_days(sprint.get_zebra_data('start_date'), sprint.get_zebra_data('end_date'), True)
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
        if len(dates) and sprint.get_zebra_data('end_date') > dates[-1]:
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
        args = []
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

        # generate the html structure and embed all values
        html_generator = SprintBurnupHtmlOutput(result_charts.keys())
        html = html_generator.get_html_structure().format(*args)

        # write the graph to file
        path = 'sprint_burnup-%s-%s.html' % (
            UrlHelper.slugify(sprint.name),
            datetime.datetime.now().strftime("%Y%m%d")
        )
        graph_location = OutputHelper.write_to_file(path, html)
        print 'Your graph is available at %s' % graph_location

