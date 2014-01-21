import re
from datetime import datetime

from lst.commands import BaseCommand
from lst.helpers import ArgParseHelper, UrlHelper
from lst.models import ResultPerStorySeries
from lst.output import ResultPerStoryChart, HtmlOutput, OutputHelper
from lst.errors import SyntaxError


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
        sprint.story_collection = jira_entries

        # extract the integer from the story id
        jira_id_only_regex = re.compile("-(\d+)$")
        jira_values = {}
        for entry in jira_entries:
            story_id = jira_id_only_regex.findall(entry.id)[0]
            jira_values[story_id] = entry.story_points

        # retrieve zebra data
        zebra_manager = self.get_zebra_manager()
        zebra_entries = zebra_manager.get_timesheets_for_sprint(sprint)
        if len(zebra_entries) == 0:
            return

        zebra_values = zebra_entries.group_by_story_id(regex)

        # get all story ids found (zebra + jira)
        jira_keys = jira_values.keys()
        zebra_keys = zebra_values.keys()
        story_ids = jira_keys + list(set(zebra_keys) - set(jira_keys))

        expected_velocity = sprint.get_expected_velocity()

        # compare commited (planned) to actual result for each story
        series = ResultPerStorySeries()
        results = {}
        for story_id in story_ids:
            hours_burnt = zebra_values.get(story_id, 0)
            series['actual'].append(hours_burnt / 8)
            planned_story_points = jira_values.get(story_id, 0)
            series['planned'].append(planned_story_points / expected_velocity)
            results[story_id] = (series['actual'][-1], series['planned'][-1])

        self._output(sprint_name, story_ids, series, results)

    def _output(self, sprint_name, story_ids, series, results):
        # generate the graph
        chart = ResultPerStoryChart.get_chart(story_ids, series, results)

        html_generator = HtmlOutput()
        html = html_generator.get_html_structure().format(
            'Result per story',
            chart.render(is_unicode=True)
        )

        # write the graph to file
        path = 'result_per_story-{}-{}.html'.format(
            UrlHelper.slugify(unicode(sprint_name)),
            datetime.now().strftime("%Y%m%d")
        )
        graph_location = OutputHelper.write_to_file(path, html)
        print 'Your graph is available at %s' % graph_location
