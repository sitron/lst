import datetime
import dateutil
import os
import shlex
import subprocess
import unicodedata
import re

from errors import *


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
        return dateutil.parser.parse(date, dayfirst=True).date()

    @classmethod
    def get_last_week_day(cls, today=None):
        """get yesterday or friday if today is monday"""
        today = datetime.date.today() if today is None else today
        delta = 1 if today.weekday() != 0 else 3
        return today - datetime.timedelta(days=delta)

    @classmethod
    def get_all_days(cls, start_date, end_date, include_weekend=False):
        all_days = list()
        dateDelta = end_date - start_date

        for i in range(dateDelta.days + 1):
            date = start_date + datetime.timedelta(days=i)

            if not include_weekend and (date.weekday() == 5 or date.weekday() == 6):
                continue

            all_days.append(date)

        return all_days

    @classmethod
    def get_future_days(cls, end_date, include_today=True, include_weekend=False):
        today = datetime.date.today()
        start = today if include_today else today + datetime.timedelta(days=1)

        return DateHelper.get_all_days(start, end_date, include_weekend)


class ZebraHelper(object):

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


class ArgParseHelper(object):

    @classmethod
    def add_sprint_name_argument(cls, parser):
        parser.add_argument("sprint_name", nargs='*', help="name of the sprint (from your config)")

    @classmethod
    def add_date_argument(cls, parser):
        parser.add_argument(
            "-d",
            "--date",
            nargs='*',
            help="specify date(s). Optional, multiple argument (syntax: -d dd.mm.yyyy or yyyy.mm.dd)"
        )

    @classmethod
    def add_user_argument(cls, parser):
        parser.add_argument(
            "-u",
            "--user",
            nargs='*',
            help="specify user id(s). Optional, multiple argument (multiple syntax: -u 111 123 145)"
        )

    @classmethod
    def add_user_story_id_argument(cls, parser):
        parser.add_argument("story_id", help="specify user story id (ie. jlc-111)")


class MathHelper(object):

    @classmethod
    def get_values_as_percent(cls, values, old_range):
        new_range = (0, 100)
        ranged = []
        for value in values:
            if value is not None:
                ranged.append(
                    ((value - old_range[0]) * (new_range[1] - new_range[0]) / (old_range[1] - old_range[0]))
                    + new_range[0]
                )
        return ranged


class UrlHelper(object):

    @staticmethod
    def slugify(s):
        slug = unicodedata.normalize('NFKD', s)
        slug = slug.encode('ascii', 'ignore').lower()
        slug = re.sub(r'[^a-z0-9]+', '-', slug).strip('-')
        slug = re.sub(r'[-]+', '-', slug)
        return slug
