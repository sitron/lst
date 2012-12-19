import argparse
import os

from parser import ConfigParser
from parser import SecretParser
from commands import SprintGraphCommand
from models import AppContainer

"""LST, helps keep your sprint commitment safe"""
class Lst(object):
    def __init__(self):
        usage = """Usage: lst command

        Available commands:
        sprint-graph \t\tprints a burn up chart for a given sprint

        """

        SETTINGS_PATH = os.path.expanduser('~/.lst.yml')
        SECRET_PATH = os.path.expanduser('~/.lst-secret.yml')

        # define arguments and options
        parser = argparse.ArgumentParser()
        parser.add_argument("command", help="command to execute")

        parser.add_argument("-p", "--project", help="project's name, as stated in your config")
        parser.add_argument("-s", "--sprint-index", help="sprint index, as stated in your config", type=unicode)

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

        available_actions = {
            'sprint-graph': SprintGraphCommand,
        }

        if args.command not in available_actions:
            raise SyntaxError("Command %s does not exist." % (args.command))

        action = available_actions[args.command]()
        action.run(args.project, args.sprint_index)

if __name__ == '__main__':
    lst = Lst()

