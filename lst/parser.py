import yaml
import datetime
import dateutil
import os

from models import Project
from models import Sprint
from models import AppContainer

class SecretParser:
    def __init__(self, url):
        try:
            data_file = open(url)
            settings = yaml.load(data_file)
            data_file.close()

            self.zebra_data = settings['zebra']
            self.jira_data = settings['jira']
            self.output_dir = settings['output_dir']
        except IOError as e:
            raise Exception('Please make sure you have a file called .lst-secret.yml in your home directory (see README, setup section)')

    def get_zebra(self, key):
        return self.zebra_data[key]

    def get_jira(self, key):
        return self.jira_data[key]

    def get_output_dir(self):
        if self.output_dir[-1] != '/':
            return self.output_dir + '/'
        return self.output_dir

class ConfigParser:
    def __init__(self):
        self.data = None
        self.url = None

    def load_config(self, url):
        # check that the config file exists
        try:
            with open(url) as f: pass
        except IOError as e:
            raise Exception('Please make sure you have a file called .lst.yml in your home directory (see README, setup section)')

        self.url = url
        try:
            data_file = open(url)
            self.data = yaml.load(data_file)
            data_file.close()
        except:
            raise Exception('Couldn\'t load your setup file (.lst.yml) check that it exists and that it is yaml compliant')

    def create_project(self, project):
        if self.data is None:
            self.data = {
                'projects': list()
            }

        # check if the project already exist, if so replace it
        p = self.get_raw_project(project['name'])
        if p is not None:
            p = project
        else:
            self.data['projects'].append({'project': project})

        self.write_config()

    def update_project(self, project):
        p = self.get_raw_project(project.name)
        if p is None:
            print 'Project %s was not found, and thus can\'t be updated' % (project.name)
            return
        p = project
        self.write_config()

    def write_config(self):
        try:
            with open(self.url, 'w') as config:
                config.write(yaml.dump(self.data, default_flow_style=False))
        except:
            raise Exception('Unable to write to config file')

        print 'Your config file was updated. Check it at %s' % (self.url)

    def parse_project(self, data):
        project = Project()
        project.name = unicode(data['name'])
        project.raw = data
        return project

    def parse_sprint(self, data):
        sprint = Sprint()
        sprint.index = unicode(data['index'])
        sprint.jira_data = data['jira']
        sprint.zebra_data = data['zebra']
        sprint.commited_man_days = unicode(data['commited_man_days'])
        try:
            sprint.forced = self.parse_forced(data['zebra']['force'])
        except:
            pass
        return sprint

    def get_project(self, name):
        project = None
        for proj in self.data['projects']:
            p = proj['project']
            if p['name'] == name:
                project = self.parse_project(p)
                for spr in p['sprints']:
                    s = spr['sprint']
                    sprint = self.parse_sprint(s)
                    project.sprints[sprint.index] = sprint
                break
        return project

    def get_raw_project(self, name):
        for proj in self.data['projects']:
            p = proj['project']
            if p['name'] == name:
                return p
        return None

    def get_projects(self):
        l = []
        try:
            for proj in self.data['projects']:
                l.append(proj['project'])
        except TypeError as e:
            print 'No projects defined'
        return l

    def parse_forced(self, force):
        dates = dict()
        forced = dict()
        for f in force:
            static = f['static']
            dates = self.parse_date(static['date'])
            time = static['time']
            for d in dates:
                forced[d.strftime("%Y-%m-%d")] = time
        return forced

    def parse_date(self, date):
        if type(date) == datetime.date:
            return [date]

        # it's a date delta str as start/end
        if date.find('/') != -1:
            b = list()
            a = date.split('/')
            if len(a) != 2:
                raise SyntaxError( "A date delta should be specified as a string (date1/date2), given: %s" % (date))

            start = dateutil.parser.parse(a[0])
            end = dateutil.parser.parse(a[1])
            if start > end:
                raise SyntaxError( "The first date in a delta should be smaller than the second one, given: %s" % (date))

            dateDelta = end - start
            for i in range(dateDelta.days + 1):
                b.append(start + datetime.timedelta(days = i))
            return b

        # it's multiple dates separated by comma
        if date.find(',') != -1:
            b = list()
            a = date.split(',')
            for d in a:
                b.append(dateutil.parser.parse(d))
            return b

