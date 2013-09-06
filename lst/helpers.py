from errors import *
import datetime
import dateutil
import os
import shlex
import subprocess


class InputHelper(object):
    """Help to sanitize user input"""

    @classmethod
    def sanitize_users(cls, users):
        """Ensure that we get either a list of users or None"""
        if users is not None and len(users) == 0:
            users = None
        return users

    @classmethod
    def sanitize_dates(cls, dates):
        """Ensure that we get either a list of dates or an empty list"""
        return [] if dates is None else dates

    @classmethod
    def check_nb_arguments(cls, args, minLimit=0, maxLimit=None):
        """Check that the number of arguments is within an definite range (raise an error if not)"""
        if len(args) > maxLimit or len(args) < minLimit:
            raise InputParametersError("Number of arguments is out of range")

    @classmethod
    def ensure_max_2_dates(cls, dates):
        """Ensure that max 2 dates are input"""
        try:
            cls.check_nb_arguments(dates, 0, 2)
        except InputParametersError:
            raise InputParametersError("You can't specify more than 2 dates (start and end)")

    @classmethod
    def get_user_input(cls, question, format_method=str, input_method=raw_input):
        input = input_method(question)
        if format_method == 'date':
            try:
                return DateHelper.sanitize_date(input)
            except:
                raise InputParametersError('could not parse your input "%s" to %s' % (input, str(format_method)))
        try:
            return format_method(input)
        except:
            raise InputParametersError('could not parse your input "%s" to %s' % (input, str(format_method)))


class DateHelper(object):
    """Help to sanitize and uniform dates"""

    @classmethod
    def sanitize_date(cls, date):
        """From a user input string date returns a date object"""
        return dateutil.parser.parse(date).date()

    @classmethod
    def get_last_week_day(cls, today=None):
        """get yesterday or friday if today is monday"""
        today = datetime.date.today() if today is None else today
        delta = 1 if today.weekday() != 0 else 3
        return today - datetime.timedelta(days=delta)


class ZebraHelper(object):

    @classmethod
    def get_zebra_url_for_activities(
            cls,
            start_date,
            end_date = None,
            projects = None,
            users = None,
            activities = None,
            internal_projects = None,
            project_type_to_consider = 'external'
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

    @classmethod
    def get_zebra_url_for_sprint_last_day(cls, sprint):
        """
        Returns zebra url to retrieve all sprint days from start date to today

        :param sprint:Sprint
        :return:string url to call on zebra remote
        """
        users = sprint.get_zebra_data('users')
        client_id = sprint.get_zebra_data('client_id')
        activities = sprint.get_zebra_data('activities')
        start_date = sprint.get_zebra_data('start_date')
        end_date = datetime.date.today()

        return cls.get_zebra_url_for_activities(start_date, end_date, client_id, users, activities)

    @classmethod
    def zebra_date(cls, date_object):
        """
        Returns a Zebra compatible date string from a Date object

        :param date_object:date
        :return:string date as YYYY-MM-DD
        """
        return date_object.strftime('%Y-%m-%d')

    @classmethod
    def get_activity_url(cls, base_url, activity_id):
        """
        Returns a zebra activity url

        :param base_url: base zebra url
        :param activity_id: activity id
        :return: string, url
        """
        return base_url + '/timesheet/' + str(activity_id)


class JiraHelper(object):

    @classmethod
    def get_url_for_project_lookup_by_story_id(cls, story_id):
        return "/sr/jira.issueviews:searchrequest-xml/temp/SearchRequest.xml" \
               "?jqlQuery=key+%3D+'" + str(story_id) + "'" \
               "&tempMax=1000"

    @classmethod
    def sanitize_sprint_name(cls, sprint_name):
        """
        Converts "human readable" sprint name to what jira expects (blanks replaced by +)

        :param sprint_name:string sprint name
        :return:string
        """
        return sprint_name.replace(' ', '+')

class FileHelper(object):

    @classmethod
    def open_for_edit(cls, filepath, editor=None):
        """
        Launch the edition of the requested file
        Cherry picked from taxi: https://github.com/sephii/taxi/blob/master/taxi/utils/file.py#L14-L30
        """
        if editor is None:
            editor = 'sensible-editor'

        editor = shlex.split(editor)
        editor.append(filepath)

        try:
            subprocess.call(editor)
        except OSError:
            if 'EDITOR' not in os.environ:
                raise Exception("Can't find any suitable editor. Check your EDITOR "
                                " env var.")

            editor = shlex.split(os.environ['EDITOR'])
            editor.append(filepath)
            subprocess.call(editor)