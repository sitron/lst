import yaml
import datetime
import dateutil
import os

from models import Sprint, AppContainer, Team

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

    def create_sprint(self, name, sprint):
        if self.data is None:
            self.data = {
                'sprints': dict()
            }

        self.data['sprints'][name] = sprint

        self.write_config()

    def create_team(self, name, users):
        self._init_config()
        teams = self.data.get('_teams', {})
        teams.update({name: {'users': users}})

        self.data.update({'_teams': teams})

        self.write_config()

    def _init_config(self):
        if self.data is None:
            self.data = {}

    def write_config(self):
        try:
            with open(self.url, 'w') as config:
                config.write(yaml.dump(self.data, default_flow_style=False))
        except:
            raise Exception('Unable to write to config file')

        print 'Your config file was updated. Check it at %s' % (self.url)

    def parse_sprint(self, name, data):
        sprint = Sprint()
        sprint.name = unicode(name)
        sprint.raw = data
        sprint.jira_data = data['jira']
        sprint.zebra_data = data['zebra']
        sprint.commited_man_days = unicode(data['commited_man_days'])
        try:
            sprint.forced = self.parse_forced(data['zebra']['force'])
        except:
            pass
        return sprint

    def get_sprint(self, name):
        sprint = None
        for k,v in self.data['sprints'].items():
            if k == name:
                sprint = self.parse_sprint(k, v)
                break
        return sprint

    def get_team(self, name):
        team = None
        for k,v in self.data['_teams'].items():
            if k == name:
                team = self.parse_team(k, v)
                break
        return team

    def parse_team(self, name, data):
        team = Team()
        team.name = unicode(name)
        team.users = data
        return team

    def get_sprints(self):
        return self.data['sprints']

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
