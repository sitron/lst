import yaml
import datetime
import dateutil
import os

from models import Sprint, AppContainer
from errors import FileNotFoundError, SyntaxError

class SecretParser:
    def __init__(self):
        self.zebra_data = None
        self.jira_data = None
        self.output_dir = None

    def parse(self, url):
        try:
            data_file = open(url)
            settings = yaml.load(data_file)
            data_file.close()
        except IOError as e:
            raise FileNotFoundError('Please make sure you have a file called .lst-secret.yml in your home directory (see README, setup section)')

        self.extract_data(settings)

    def extract_data(self, settings):
        try:
            self.zebra_data = settings['zebra']
            self.jira_data = settings['jira']
            self.output_dir = settings['output_dir']
        except KeyError as e:
            raise SyntaxError('Your .lst-secret.yml does not contain all necessary information (key problem: %s)' % (e))

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
        if 'force' in data['zebra']:
            sprint.forced = self.parse_forced(data['zebra']['force'])
        if 'planned' in data['zebra']:
            sprint.planned = self.parse_planned(data['zebra']['planned'], data['zebra']['start_date'], data['zebra']['end_date'])
        return sprint

    def get_sprint(self, name = None):
        sprint = None
        if name is None:
            name = self.get_current_sprint_name()

        if name is not None:
            for k,v in self.data['sprints'].items():
                if k == name:
                    sprint = self.parse_sprint(k, v)
                    break
        return sprint

    def get_current_sprint_name(self):
        sprint_name = self.data.get('_current')
        return sprint_name

    def get_sprints(self):
        return self.data['sprints']

    def parse_forced(self, force):
        dates = dict()
        forced = dict()
        for f in force:
            dates = self.parse_date(f['date'])
            time = f['time']
            for d in dates:
                forced[d.strftime("%Y-%m-%d")] = time
        return forced

    def parse_planned(self, plan, start_date, end_date):
        dates = dict()
        planned = dict()

        # Check for single value list (like [1,2,3])
        if type(plan[0]) is int:
            d = start_date
            position = 0
            while d <= end_date:
                if d.isoweekday() <> 6 and d.isoweekday() <> 7:
                    if position >= len(plan):
                        raise SyntaxError( "The planned list must contain one value per business day, there is not enough values")
                    planned[d.strftime("%Y-%m-%d")] = plan[position]
                    position += 1
                d += datetime.timedelta(days=1)
            if position < len(plan):
                raise SyntaxError( "The planned list must contain one value per business day, there is too much values")
            return planned

        # Check for date list
        for f in plan:
            dates = self.parse_date(f['date'])
            time = f['time']
            for d in dates:
                planned[d.strftime("%Y-%m-%d")] = time
        return planned

    def parse_date(self, date):
        # single date
        if type(date) == datetime.date:
            return [date]

        # multiple dates (list)
        elif type(date) == list:
            return date

        # date range (str as start/end)
        else:
            try:
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
            except:
                raise SyntaxError( "The date should be specified as either a single date, a list of dates, or a string formated as start_date/end_date, given: %s" % (date))
