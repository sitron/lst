import argparse
import os

from parser import ConfigParser
from parser import SecretParser
from commands import SprintGraphCommand, TestInstallCommand
from models import AppContainer

"""LST, helps keep your sprint commitment safe"""
class Lst(object):
    def __init__(self):
        usage = """%(prog)s command [options]

available commands:
  sprint-graph \t\tprints a burn up chart for a given sprint
  test-install \t\ttest the installation"""

        SETTINGS_PATH = os.path.expanduser('~/.lst.yml')
        SECRET_PATH = os.path.expanduser('~/.lst-secret.yml')

        available_actions = {
            'sprint-graph': SprintGraphCommand,
            'test-install' : TestInstallCommand,
        }

        # define arguments and options
        parser = argparse.ArgumentParser(
            prog='lst',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            usage=usage
        )
        parser.add_argument("command", help="command to execute (see available commands above)")

        parser.add_argument("-p", "--project", help="project's name, as stated in your config")
        parser.add_argument("-s", "--sprint-index", help="sprint index, as stated in your config", type=unicode)
        parser.add_argument("--dev-mode", action="store_true", help="development mode")

        # read command line arguments
        args = parser.parse_args()

        # read config
        print 'Reading config'
        config = ConfigParser()
        config.load_config(SETTINGS_PATH)

        # read usernames and passwords for jira/zebra
        secret = SecretParser(SECRET_PATH)

        # create globally accessible app container
        AppContainer.config = config
        AppContainer.secret = secret
        AppContainer.dev_mode = args.dev_mode

        if args.command not in available_actions:
            raise SyntaxError("Command %s does not exist." % (args.command))

        action = available_actions[args.command]()
        action.run(args.project, args.sprint_index)

if __name__ == '__main__':
    lst = Lst()

