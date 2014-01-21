import argparse
import os

from lst.parser import ConfigParser, SecretParser
from lst.models import AppContainer
from lst.errors import NotFoundError
from lst.commands import *
from lst.commands.result_per_story import ResultPerStoryCommand
from lst.commands.check_hours import CheckHoursCommand
from lst.commands.add_sprint import AddSprintCommand
from lst.commands.list import ListCommand
from lst.commands.retrieve_user_id import RetrieveUserIdCommand
from lst.commands.retrieve_jira_information_for_config import RetrieveJiraInformationForConfigCommand
from lst.commands.edit import EditCommand
from lst.commands.dump import DumpSprintConfigCommand
from lst.commands.test_install import TestInstallCommand
from lst.commands.sprint_burnup import SprintBurnUpCommand
from lst.commands.get_last_zebra_day import GetLastZebraDayCommand


__version__ = '1.4'


class Lst(object):
    """LST, helps keeping your sprint commitment safe"""

    def __init__(self):
        usage = """%(prog)s command [options]

available commands:
  sprint-burnup\t\tPrints a burn up chart for a given sprint until an optional date (defaults to yesterday)
  test-install\t\tTest the installation
  get-user-id\t\tRetrieve a Zebra user id from his/her last name
  ls \t\t\tList all sprints defined in config
  edit \t\t\tOpen the config in edit mode
  jira-config-helper\tRetrieve some useful information about a Jira project and sprint from a story id (ie. XX-12)
  add-sprint\t\tAdds a sprint to your config file
  check-hours\t\tRetrieve all Zebra hours for a date/user(s). User is optional and can be multiple. Date is optional defaults to yesterday. If 2 dates are specified then min = start date, max = end date
  get-last-zebra-day\tRetrieve the last Zebra day that contains a commit for this project
  result-per-story\t\tPrint the actual time used per story
  dump-sprint-config\t\tOutput your config for a specific sprint"""

        SETTINGS_PATH = os.path.expanduser('~/.lst.yml')
        SECRET_PATH = os.path.expanduser('~/.lst-secret.yml')

        available_actions = {
            'sprint-burnup': SprintBurnUpCommand,
            'test-install': TestInstallCommand,
            'get-user-id': RetrieveUserIdCommand,
            'ls': ListCommand,
            'edit': EditCommand,
            'jira-config-helper': RetrieveJiraInformationForConfigCommand,
            'add-sprint': AddSprintCommand,
            'check-hours': CheckHoursCommand,
            'get-last-zebra-day': GetLastZebraDayCommand,
            'result-per-story': ResultPerStoryCommand,
            'dump-sprint-config': DumpSprintConfigCommand,
        }

        # define arguments and options
        parser = argparse.ArgumentParser(
            prog='lst',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            usage=usage
        )

        # add version argument
        parser.add_argument('-v', '--version', action='version', version=__version__)

        # add arguments for all commands
        subparsers = parser.add_subparsers(dest='command')
        for name, command in available_actions.items():
            action = command()
            # add specific args
            subparser = action.add_command_arguments(subparsers)
            # add common args
            action.add_common_arguments(subparser)

        # read command line arguments
        args = parser.parse_args()

        AppContainer.SETTINGS_PATH = SETTINGS_PATH
        AppContainer.SECRET_PATH = SECRET_PATH

        # read usernames and passwords for jira/zebra
        secret = SecretParser()
        secret.parse(SECRET_PATH)

        # create globally accessible app container
        AppContainer.secret = secret
        AppContainer.user_args = args
        AppContainer.dev_mode = args.dev_mode

        # read config
        print 'Reading config'
        config = ConfigParser()
        config.load_config(SETTINGS_PATH)
        AppContainer.config = config

        if args.command not in available_actions:
            raise NotFoundError("Command '%s' does not exist. See lst -h" % (args.command))

        action = available_actions[args.command]()
        action.run(args)

if __name__ == '__main__':
    lst = Lst()
