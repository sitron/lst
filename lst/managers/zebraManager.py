import dateutil.parser
import pickle

from remote import ZebraRemote
from helpers import ZebraHelper
from models.zebraModels import TimeSheetCollection, TimeSheet


class ZebraManager:
    """
    Responsible for interfacing the application with ZebraRemote
    """
    def __init__(self, app_container):
        self.app_container = app_container

    def get_timesheets_for_sprint(self, sprint):
        report_url = self._get_url_for_activities_by_sprint(sprint)

        return self.get_timesheets_by_url(report_url)

    def get_all_timesheets(self, start_date=None, end_date=None, users=None):
        url = self._get_zebra_url_for_activities(
            start_date=start_date,
            end_date=end_date,
            users=users,
            project_type_to_consider='all'
        )

        return self.get_timesheets_by_url(url)

    def get_all_users(self):
        url = 'user/.json'
        remote = self._get_zebra_remote()
        result = remote.get_data(url)
        users = self._parse_users(result)

        return users

    def get_timesheets_by_url(self, url):
        remote = self._get_zebra_remote()
        zebra_json_result = remote.get_data(url)
        timesheets = self._parse_timesheets(zebra_json_result)

        return timesheets

    def _parse_users(self, response_json):
        users = response_json['command']['users']['user']

        return users

    def _parse_timesheets(self, response_json):
        """
        Parse json response received from ZebraRemote to application data

        :param response_json: json data
        :return:TimeSheetCollection list of TimeSheet(s)
        """
        zebra_entries = []

        try:
            entries = response_json['command']['reports']['report']
            print 'Will now parse %d entries found in Zebra' % len(entries)
        except:
            print 'No entries found in Zebra'
            return zebra_entries

        for entry in entries:
            # zebra last entries are totals, and dont have a tid
            if entry['tid'] == '':
                continue

            zebra_entry = self._parse_entry(entry)
            zebra_entries.append(zebra_entry)

        return TimeSheetCollection(zebra_entries)

    def _parse_entry(self, entry):
        """
        Parse single json node to TimeSheet

        :param entry:json node
        :return:TimeSheet
        """
        timesheet = TimeSheet()
        timesheet.username = str(entry['username'].encode('utf-8'))
        timesheet.time = float(entry['time'])
        timesheet.project = (entry['project'].encode('utf-8'))
        timesheet.date = dateutil.parser.parse(entry['date'], dayfirst=True)
        timesheet.id = int(entry['tid'])
        timesheet.description = str(entry['description'].encode('utf-8'))

        return timesheet

    def _get_zebra_remote(self):
        return ZebraRemote(
            self.app_container.secret.get_zebra('url'),
            self.app_container.secret.get_zebra('username'),
            self.app_container.secret.get_zebra('password')
        )

    def _get_url_for_activities_by_sprint(self, sprint):
        users = sprint.get_zebra_data('users')
        client_id = sprint.get_zebra_data('client_id')
        activities = sprint.get_zebra_data('activities')
        start_date = sprint.get_zebra_data('start_date')
        end_date = sprint.get_zebra_data('end_date')

        return self._get_zebra_url_for_activities(start_date, end_date, client_id, users, activities)

    def _get_zebra_url_for_activities(
            self,
            start_date,
            end_date=None,
            projects=None,
            users=None,
            activities=None,
            internal_projects=None,
            project_type_to_consider='external'
    ):
        """
        Get zebra url to retrieve project's activities

        :param start_date: date string
        :param end_date:  date string
        :param projects: list of project ids
        :param users: list of user ids
        :param activities: list of activity ids (project is divided in multiple activities
        :param internal_projects: list of internal project ids
        :param project_type_to_consider: external/internal/all. Zebra stores internal/external projects differently
        :return: string Zebra url
        """
        report_url = 'timesheet/report/.json?option_selector='

        if end_date is None:
            end_date = start_date

        if users is None:
            report_url += '&users[]=*'
        elif type(users) == list:
            for user in users:
                report_url += '&users[]=' + str(user)
        else:
            report_url += '&users[]=' + str(users)

        if activities is None:
            report_url += '&activities[]=*'
        elif type(activities) == list:
            for activity in activities:
                report_url += '&activities[]=' + `activity`
        else:
            report_url += '&activities[]=' + str(activities)

        if project_type_to_consider != 'internal':
            if projects is None:
                report_url += '&projects[]=*'
            elif type(projects) == list:
                for project in projects:
                    report_url += '&projects[]=' + `project`
            else:
                report_url += '&projects[]=' + str(projects)

        if project_type_to_consider != 'external':
            if internal_projects is None:
                report_url += '&internal[]=*'
            elif type(internal_projects) == list:
                for internal_project in internal_projects:
                    report_url += '&internal[]=' + `internal_project`
            else:
                report_url += '&internal[]=' + str(internal_projects)

        report_url += '&start=' + str(start_date)
        report_url += '&end=' + str(end_date)

        return report_url
