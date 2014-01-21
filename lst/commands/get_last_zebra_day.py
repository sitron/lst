from lst.commands import BaseCommand
from lst.helpers import ArgParseHelper

import datetime


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
