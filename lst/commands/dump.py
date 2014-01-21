from lst.commands import BaseCommand
from lst.helpers import ArgParseHelper
import yaml


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
