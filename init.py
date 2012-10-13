import json
import argparse
import urllib, urllib2, urlparse, cookielib
import xml.etree.ElementTree as ET
from pprint import pprint

"""scrum nanny, helps you keep your sprint commitment safe"""
def init():
    parser = argparse.ArgumentParser()
    parser.add_argument("project", help="project's name, as stated in your config")
    parser.add_argument("-i", "--sprint-index", help="sprint index, as stated in your config", type=unicode)
    args = parser.parse_args()

    config_parser = ConfigParser(args.project, args.sprint_index)
    settings = config_parser.load_config('settings.json')

    secret = SecretParser('secret.json')

    project = config_parser.parse(settings)

    zebra = ZebraRemote(secret.get_zebra('url'), secret.get_zebra('username'), secret.get_zebra('password'))
    zebra_entries = zebra.get_data(project)

    jira = JiraRemote(secret.get_jira('url'), secret.get_jira('username'), secret.get_jira('password'))
    jira_entries = jira.get_data(project)

class ZebraEntries(dict):
    def __init__(self):
        self.ordered_dates = None

    def get_ordered_dates(self):
        if self.ordered_dates is None:
            self.ordered_dates = sorted(set(self.keys()))
        return self.ordered_dates

class Remote(object):
    def __init__(self, base_url):
        self.base_url = base_url

    def _get_request(self, url, body = None, headers = {}):
        return urllib2.Request('%s/%s' % (self.base_url, url), body, headers)

    def _request(self, url, body = None, headers = {}):
        request = self._get_request(url, body, headers)
        opener = urllib2.build_opener()
        response = opener.open(request)
        return response

    def login(self):
        pass

    def get_data(self, project):
        pass

class JiraRemote(Remote):
    def __init__(self, base_url, username, password):
        super(JiraRemote, self).__init__(base_url)

        self.username = username
        self.password = password

    def _get_request(self, url, body = None, headers = {}):
        if 'User-Agent' not in headers:
            headers['User-Agent'] = 'ScrumNanny Zebra Client';
        return super(JiraRemote, self)._get_request(url, body, headers)

    def _request(self, url, body = None, headers = {}):
        request = self._get_request(url, body, headers)
        opener = urllib2.build_opener()

        try:
            response = opener.open(request)
        except urllib2.URLError:
            raise Exception('Unable to connect to Jira. Check your connection status and try again.')

        return response

    def login(self):
        pass

    def get_data(self, project):
        url = project.get_sprint().get_jira_data('url')

        url += '&os_username=' + str(self.username)
        url += '&os_password=' + str(self.password)

        response = self._request(url)
        response_body = response.read()

        response_xml = ET.fromstring(response_body)
        stories = response_xml[0].findall('item')

        jira_entries = JiraEntries()
        for s in stories:
            story = JiraEntry()
            story.id = s.find('key').text
            story.status = int(s.find('status').get('id'))
            try:
                story.business_value = float(s.find('./customfields/customfield/[@id="customfield_10064"]/customfieldvalues/customfieldvalue').text)
            except AttributeError:
                print 'Story ' + story.id + ' has no business value defined'
            try:
                story.story_points = float(s.find('./customfields/customfield/[@id="customfield_10040"]/customfieldvalues/customfieldvalue').text)
            except AttributeError:
                print 'Story ' + story.id + ' has no story points defined'
            jira_entries.append(story)
        return jira_entries

class JiraEntry:
    def __init__(self):
        self.story_points = 0
        self.business_value = 0
        self.id = None
        self.status = None

    def is_over(self):
        # 6: PO review, 10008: closed
        return self.status == 6 or self.status == 10008

class JiraEntries(list):
    def __init__(self):
        list.__init__([])
        self.total_story_points = 0
        self.total_business_value = 0
        self.achieved_story_points = 0
        self.achieved_business_value = 0

    def get_total_story_points(self):
        for s in self:
            self.total_story_points += s.story_points
        return self.total_story_points

    def get_achieved_story_points(self):
        for s in self:
            if s.is_over():
                self.achieved_story_points += s.story_points
        return self.achieved_story_points

    def get_total_business_value(self):
        for s in self:
            self.total_business_value += s.business_value
        return self.total_business_value

    def get_achieved_business_value(self):
        for s in self:
            if s.is_over():
                self.achieved_business_value += s.business_value
        return self.achieved_business_value

class ZebraRemote(Remote):
    def __init__(self, base_url, username, password):
        super(ZebraRemote, self).__init__(base_url)

        self.cookiejar = cookielib.CookieJar()
        self.logged_in = False
        self.username = username
        self.password = password

    def _get_request(self, url, body = None, headers = {}):
        if 'User-Agent' not in headers:
            headers['User-Agent'] = 'ScrumNanny Zebra Client';
        return super(ZebraRemote, self)._get_request(url, body, headers)

    def _request(self, url, body = None, headers = {}):
        request = self._get_request(url, body, headers)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookiejar))

        try:
            response = opener.open(request)
        except urllib2.URLError:
            raise Exception('Unable to connect to Zebra. Check your connection status and try again.')

        self.cookiejar.extract_cookies(response, request)

        return response

    def _login(self):
        if self.logged_in:
            return

        login_url = '/login/user/%s.json' % self.username
        parameters = urllib.urlencode({
            'username': self.username,
            'password': self.password,
        })

        response = self._request(login_url, parameters)
        response_body = response.read()

        if not response.info().getheader('Content-Type').startswith('application/json'):
            self.logged_in = False
            raise Exception('Unable to login')
        else:
            self.logged_in = True

    def get_data(self, project):
        report_url = 'timesheet/report/.json?option_selector='

        users = project.get_sprint().get_zebra_data('users')
        client_id = project.get_sprint().get_zebra_data('client_id')
        activities = project.get_sprint().get_zebra_data('activities')
        start_date = project.get_sprint().get_zebra_data('start_date')
        end_date = project.get_sprint().get_zebra_data('end_date')

        for user in users:
            report_url += '&users[]=' + `user`

        report_url += '&projects[]=' + `client_id`
        report_url += '&activities[]=' + str(activities)
        report_url += '&start=' + str(start_date)
        report_url += '&end=' + str(end_date)

        self._login()

        response = self._request(report_url)
        response_body = response.read()

        response_json = json.loads(response_body)
        entries = response_json['command']['reports']['report']
        print 'Will now parse %d entries found in Zebra' % len(entries)

        return self.parse_entries(entries)

    def parse_entries(self, entries):
        entries_per_date = ZebraEntries()
        for entry in entries:
            if entry['tid'] == '':
                continue
            e = self.parse_entry(entry)
            if entry['date'] in entries_per_date:
                entries_per_date[entry['date']]['entries'].append(e)
                entries_per_date[entry['date']]['total_time'] += e['time']
            else:
                o = {'entries': [e], 'total_time': e['time']}
                entries_per_date[entry['date']] = o
        return entries_per_date

    def parse_entry(self, entry):
        return {'username': str(entry['username']), 'time': float(entry['time'])}


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

