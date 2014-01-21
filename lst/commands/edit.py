from lst.commands import BaseCommand
from lst.helpers import FileHelper
from lst.models import AppContainer
from lst.parser import ConfigParser


class EditCommand(BaseCommand):
    """
    Command to edit the config
    Usage: edit

    """
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


