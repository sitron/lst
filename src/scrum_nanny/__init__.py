import argparse
import json
from string import Template
from pprint import pprint
from datetime import datetime
import unicodedata
import re
import os

from parser import ConfigParser
from parser import SecretParser
from remote import ZebraRemote
from remote import JiraRemote
from models import JiraEntry
from models import GraphEntry
from models import GraphEntries

"""scrum nanny, helps you keep your sprint commitment safe"""
def main():
    SETTINGS_PATH = os.path.expanduser('~/.scrum-nanny.yml')
    SECRET_PATH = os.path.expanduser('~/.scrum-nanny-secret.yml')

    # read command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("project", help="project's name, as stated in your config")
    parser.add_argument("-i", "--sprint-index", help="sprint index, as stated in your config", type=unicode)
    args = parser.parse_args()

    # read config
    config_parser = ConfigParser(args.project, args.sprint_index)
    settings = config_parser.load_config(SETTINGS_PATH)

    # read usernames and passwords for jira/zebra
    secret = SecretParser(SECRET_PATH)

    print 'Reading config'
    project = config_parser.parse(settings)

    print 'Start fetching Zebra'
    zebra = ZebraRemote(secret.get_zebra('url'), secret.get_zebra('username'), secret.get_zebra('password'))
    zebra_days = zebra.get_data(project)
    print 'End Zebra'

    print 'Start fetching Jira'
    JiraEntry.closed_status =  set(project.get_closed_status_codes())
    jira = JiraRemote(secret.get_jira('url'), secret.get_jira('username'), secret.get_jira('password'))
    jira_entries = jira.get_data(project)
    print 'End Jira'

    print 'Mixing retrieved values'
    graph_entries = GraphEntries()
    for day,z in zebra_days.items():
        graph_entry = GraphEntry()
        graph_entry.time = z.time
        graph_entries[day] = graph_entry
    for day,j in jira_entries.get_achievement_by_day().items():
        graph_entry = graph_entries.get(day, GraphEntry())
        graph_entry.story_points = j['sp']
        graph_entry.business_value = j['bv']
        graph_entries[day] = graph_entry

    data = graph_entries.get_ordered_data()

    commited_values = {}
    commited_values['storyPoints'] = jira_entries.get_commited_story_points()
    commited_values['businessValue'] = jira_entries.get_commited_business_value()
    commited_values['manDays'] = project.sprint.commited_man_days

    sprint_data = {}
    sprint_data['startDate'] = project.sprint.get_zebra_data('start_date').strftime('%Y-%m-%d')
    sprint_data['endDate'] = project.sprint.get_zebra_data('end_date').strftime('%Y-%m-%d')

    # write the graph
    print 'Retrieving base graph'
    try:
        graph_file = open('src/scrum_nanny/graph_base.html')
        graph_str = graph_file.read()
        template = Template(graph_str)
        graph_file.close()
    except Exception as e:
        print 'Couldnt find the base graph file', e

    print 'Writing graph'
    try:
       # use this to debug
       # data_output = open('graphs/data.json', 'w')
       # data_output.write(json.dumps(data))
       # data_output.close()
        graph_output_file = 'graphs/' + slugify(project.get_name()) + '-' + project.get_sprint().get_index() + '-' + datetime.now().strftime("%Y%m%d") +'.html'
        graph_output_file_absolute = os.path.abspath(graph_output_file)
        graph_output = open(graph_output_file, 'w')
        graph_output.write(template.safe_substitute(base_path='../', data=json.dumps(data), commited_values=json.dumps(commited_values), sprint=json.dumps(sprint_data)))
        graph_output.close()
        print 'Check your new graph at ' + graph_output_file_absolute
    except Exception as e:
        print 'Problem with the generation of the graph file', e

def slugify(s):
    slug = unicodedata.normalize('NFKD', s)
    slug = slug.encode('ascii', 'ignore').lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug).strip('-')
    slug = re.sub(r'[-]+', '-', slug)
    return slug

if __name__ == '__main__':
    main()

