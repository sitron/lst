import argparse
import os

from parser import ConfigParser, SecretParser
from models import AppContainer
import commands
from errors import NotFoundError

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
  result-per-story\t\tPrint the actual time used per story"""

        SETTINGS_PATH = os.path.expanduser('~/.lst.yml')
        SECRET_PATH = os.path.expanduser('~/.lst-secret.yml')

        available_actions = {
            'sprint-burnup': commands.SprintBurnUpCommand,
            'test-install' : commands.TestInstallCommand,
            'get-user-id' : commands.RetrieveUserIdCommand,
            'ls' : commands.ListCommand,
            'edit': commands.EditCommand,
            'jira-config-helper': commands.RetrieveJiraInformationForConfigCommand,
            'add-sprint': commands.AddSprintCommand,
            'check-hours': commands.CheckHoursCommand,
            'get-last-zebra-day': commands.GetLastZebraDayCommand,
            'result-per-story': commands.ResultPerStoryCommand,
        }

        # define arguments and options
        parser = argparse.ArgumentParser(
            prog='lst',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            usage=usage
        )
        parser.add_argument("command", help="command to execute (see available commands above)")
        parser.add_argument("optional_argument", nargs='*', help="depends on the command to execute")
        parser.add_argument("--dev-mode", action="store_true", help="development mode")
        parser.add_argument("-u", "--user", nargs='*', help="specify user id(s). Optional, multiple argument (multiple syntax: -u 111 123 145)")
        parser.add_argument("-d", "--date", nargs='*', help="specify date(s). Optional, multiple argument (syntax: -d 22.03.2013)")

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
