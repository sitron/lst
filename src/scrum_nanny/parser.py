import json
from models import Project
from models import Sprint

class SecretParser:
    def __init__(self, url):
        json_file = open(url)
        settings = json.load(json_file)
        json_file.close()
        self.zebra_data = settings['zebra']
        self.jira_data = settings['jira']

    def get_zebra(self, key):
        return self.zebra_data[key]

    def get_jira(self, key):
        return self.jira_data[key]

class ConfigParser:
    def __init__(self, user_project, user_index):
        self.u_project = user_project
        self.u_index = user_index

    def load_config(self, url):
        json_file = open(url)
        settings = json.load(json_file)
        json_file.close()
        return settings

    def parse(self, jsonData):
        # check if the project specified exists
        for proj in jsonData['projects']:
            if proj['name'] == self.u_project:
                project = Project()
                project.set_name(proj['name'])
                projectData = proj
                break
        try:
            print "Project %s found in config" % (project.get_name())
        except:
            print "Project %s not found. Make sure it's defined in your settings file" % (userProject)
            return

        # if a sprint index is specified check that it exists
        if self.u_index is not None:
            try:
                projectData['sprints']
            except:
                print "There is no sprint defined in your config for the project %s" % (project.get_name())
                return

            for spr in projectData['sprints']:
                if unicode(spr['index']) == self.u_index:
                    break
        else:
            print "No sprint index specified, taking last defined per default"
            spr = projectData['sprints'][len(projectData['sprints']) - 1]

        try:
            sprint = Sprint()
            sprint.set_index(unicode(spr['index']))
            sprint.set_jira_data(spr['jira'])
            sprint.set_zebra_data(spr['zebra'])
            sprint.commited_man_days = unicode(spr['commited_man_days'])
            project.set_sprint(sprint)
            print "Sprint %s found in config" % (sprint.get_index())
#            print project.get_sprint().get_jira_data('url')
#            print project.get_sprint().get_zebra_data('client_id')
        except:
            print "Either the sprint you specified was not found or there was no sprint defined in your config"
            return

        return project


