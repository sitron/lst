import argparse
from pprint import pprint

from parser import ConfigParser
from parser import SecretParser
from remote import ZebraRemote
from remote import JiraRemote

"""scrum nanny, helps you keep your sprint commitment safe"""
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("project", help="project's name, as stated in your config")
    parser.add_argument("-i", "--sprint-index", help="sprint index, as stated in your config", type=unicode)
    args = parser.parse_args()

    config_parser = ConfigParser(args.project, args.sprint_index)
    settings = config_parser.load_config('settings.json')

    secret = SecretParser('secret.json')

    print 'Reading config'
    project = config_parser.parse(settings)

    print 'Start fetching Zebra'
    zebra = ZebraRemote(secret.get_zebra('url'), secret.get_zebra('username'), secret.get_zebra('password'))
    zebra_days = zebra.get_data(project)
    print 'End Zebra'

    print 'Start fetching Jira'
    jira = JiraRemote(secret.get_jira('url'), secret.get_jira('username'), secret.get_jira('password'))
    jira_entries = jira.get_data(project)
    print 'End Jira'

    pprint(jira_entries.get_achievement_by_day())

if __name__ == '__main__':
    main()

