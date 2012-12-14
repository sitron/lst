import json
import os
from string import Template
from pprint import pprint
from datetime import datetime
import unicodedata
import re

from remote import ZebraRemote
from remote import JiraRemote
from models import JiraEntry
from models import GraphEntry
from models import GraphEntries

class BaseCommand:
    def __init__(self, app_container):
        self.app_container = app_container
        self.secret = app_container.secret

    def run(self):
        pass

class SprintGraphCommand(BaseCommand):
    """
    Usage:  sprint-graph [project_id] (uses last sprint defined in this project)
            sprint-graph [project_id] [-i sprint_index]

    """

    def run(self, project_id, sprint_index = None):
        print 'Start fetching Zebra'
        zebra = ZebraRemote(self.secret.get_zebra('url'), self.secret.get_zebra('username'), self.secret.get_zebra('password'))

        # todo: get project from config based on project_id
        project = self.app_container.project

        # todo: get sprint from config based on sprint_index
        sprint = project.sprint

        zebra_days = zebra.get_data(project)
        print 'End Zebra'

        print 'Start fetching Jira'
        JiraEntry.closed_status = set(project.get_closed_status_codes())
        jira = JiraRemote(self.secret.get_jira('url'), self.secret.get_jira('username'), self.secret.get_jira('password'))
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
        commited_values['manDays'] = sprint.commited_man_days

        sprint_data = {}
        sprint_data['startDate'] = sprint.get_zebra_data('start_date').strftime('%Y-%m-%d')
        sprint_data['endDate'] = sprint.get_zebra_data('end_date').strftime('%Y-%m-%d')

        # write the graph
        print 'Retrieving base graph'
        try:
            graph_file = open('lst/graph_base.html')
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
            graph_output_file = 'graphs/' + Helper.slugify(project.get_name()) + '-' + project.get_sprint().get_index() + '-' + datetime.now().strftime("%Y%m%d") +'.html'
            graph_output_file_absolute = os.path.abspath(graph_output_file)
            graph_output = open(graph_output_file, 'w')
            graph_output.write(template.safe_substitute(base_path='../', data=json.dumps(data), commited_values=json.dumps(commited_values), sprint=json.dumps(sprint_data)))
            graph_output.close()
            print 'Check your new graph at ' + graph_output_file_absolute
        except Exception as e:
            print 'Problem with the generation of the graph file', e

class Helper(object):
    @staticmethod
    def slugify(s):
        slug = unicodedata.normalize('NFKD', s)
        slug = slug.encode('ascii', 'ignore').lower()
        slug = re.sub(r'[^a-z0-9]+', '-', slug).strip('-')
        slug = re.sub(r'[-]+', '-', slug)
        return slug
