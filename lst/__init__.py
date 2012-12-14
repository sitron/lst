import argparse
import os

from parser import ConfigParser
from parser import SecretParser
from commands import SprintGraphCommand


"""LST, helps keep your sprint commitment safe"""
def main():
    SETTINGS_PATH = os.path.expanduser('~/.lst.yml')
    SECRET_PATH = os.path.expanduser('~/.lst-secret.yml')

    # read command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("project", help="project's name, as stated in your config")
    parser.add_argument("-i", "--sprint-index", help="sprint index, as stated in your config", type=unicode)
    args = parser.parse_args()

    # read config
    config_parser = ConfigParser(args.project, args.sprint_index)
    settings = config_parser.load_config(SETTINGS_PATH)

    # todo move this to command
    print 'Reading config'
    project = config_parser.parse(settings)

    # read usernames and passwords for jira/zebra
    secret = SecretParser(SECRET_PATH)

    app_container = AppContainer()
    app_container.settings = settings
    app_container.secret = secret
    app_container.project = project

    action = SprintGraphCommand(app_container)
    action.run(args.project, args.sprint_index)

class AppContainer(object):
    pass

if __name__ == '__main__':
    main()

