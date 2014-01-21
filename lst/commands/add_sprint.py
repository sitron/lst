from lst.commands import BaseCommand
from lst.helpers import InputHelper, JiraHelper
from lst.models import AppContainer


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

        client_id = InputHelper.get_user_input(
            'Give me the zebra project id (if you use Taxi, just do `taxi search client_name` else check in Zebra. '
            'It should be a four digit integer): ',
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
        story_data = self.get_jira_manager().get_story(story)

        jira_data = {}
        jira_data['project_id'] = int(story_data.project_id)
        jira_data['sprint_name'] = JiraHelper.sanitize_sprint_name(story_data.sprint_name)

        return jira_data
