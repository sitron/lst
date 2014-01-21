from lst.commands import BaseCommand


class ListCommand(BaseCommand):
    """
    Usage:  ls lists all sprints defined in config

    """
    def add_command_arguments(self, subparsers):
        parser = subparsers.add_parser('ls')
        return parser

    def run(self, args):
        self._output(self.config.get_sprints())

    def _output(self, sprints):
        print ''
        if len(sprints) == 0:
            print 'No sprints defined'
        else:
            print 'All currently defined sprints:'
            for k, v in sprints.items():
                print k
