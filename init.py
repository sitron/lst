import json
import argparse

"""scrum nanny, helps you keep your sprint commitment safe"""
def init():
    parser = argparse.ArgumentParser()
    parser.add_argument("project", help="project's name, as stated in your config")
    parser.add_argument("-i", "--sprint-index", help="sprint index, as stated in your config", type=unicode)
    args = parser.parse_args()

    config_parser = ConfigParser(args.project, args.sprint_index)
    settings = config_parser.load_config('settings.json')

    project = config_parser.parse(settings)

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
            project.set_sprint(sprint)
            print "Sprint %s found in config" % (sprint.get_index())
#            print project.get_sprint().get_jira_data('url')
#            print project.get_sprint().get_zebra_data('client_id')
        except:
            print "Either the sprint you specified was not found or there was no sprint defined in your config"
            return

        return project



class Project:
    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def set_sprint(self, sprint):
        self.sprint = sprint

    def get_sprint(self):
        return self.sprint

class Sprint:
    def get_index(self):
        return self.index

    def set_index(self, index):
        self.index = index

    def set_jira_data(self, data):
        self.jira_data = data

    def get_jira_data(self, key):
        return self.jira_data[key]

    def set_zebra_data(self, data):
        self.zebra_data = data

    def get_zebra_data(self, key):
        return self.zebra_data[key]

if __name__ == '__main__':
    init()

