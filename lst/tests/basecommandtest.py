from ..commands import BaseCommand
from ..errors import *
import datetime, unittest

class BaseCommandTest(unittest.TestCase):
    """Unit tests for BaseCommand in commands.py"""

    def testZebraDate(self):
        """date format is correct"""
        base_command = BaseCommand()
        date = datetime.datetime.strptime('20130428', "%Y%m%d").date()
        self.assertEquals('2013-04-28', base_command.zebra_date(date))

    def testGetZebraUrlForActivitiesWithDefaultArgs(self):
        """returns correct url with default arguments"""
        base_command = BaseCommand()
        wanted_url = 'timesheet/report/.json?option_selector=&users[]=*&activities[]=*&projects[]=*&start=2013-04-28&end=2013-04-28'
        start_date = datetime.datetime.strptime('20130428', "%Y%m%d").date()
        self.assertEquals(wanted_url, base_command._get_zebra_url_for_activities(start_date))

    def testGetZebraUrlForActivitiesWithOneUser(self):
        """returns correct url when specifying 1 user"""
        base_command = BaseCommand()
        wanted_url = 'timesheet/report/.json?option_selector=&users[]=101&activities[]=*&projects[]=*&start=2013-04-28&end=2013-04-28'
        start_date = datetime.datetime.strptime('20130428', "%Y%m%d").date()
        users = 101
        self.assertEquals(wanted_url, base_command._get_zebra_url_for_activities(start_date, users=users))

    def testGetZebraUrlForActivitiesWithMultipleUsers(self):
        """returns correct url when specifying multiple users"""
        base_command = BaseCommand()
        wanted_url = 'timesheet/report/.json?option_selector=&users[]=101&users[]=102&activities[]=*&projects[]=*&start=2013-04-28&end=2013-04-28'
        start_date = datetime.datetime.strptime('20130428', "%Y%m%d").date()
        users = [101, 102]
        self.assertEquals(wanted_url, base_command._get_zebra_url_for_activities(start_date, users=users))

    def testGetZebraUrlForActivitiesWithOneUserAsString(self):
        """returns correct url when specifying one user as string"""
        base_command = BaseCommand()
        wanted_url = 'timesheet/report/.json?option_selector=&users[]=101&activities[]=*&projects[]=*&start=2013-04-28&end=2013-04-28'
        start_date = datetime.datetime.strptime('20130428', "%Y%m%d").date()
        users = '101'
        self.assertEquals(wanted_url, base_command._get_zebra_url_for_activities(start_date, users=users))

    def testGetZebraUrlForActivitiesWithOneActivity(self):
        """returns correct url when specifying one activity"""
        base_command = BaseCommand()
        wanted_url = 'timesheet/report/.json?option_selector=&users[]=*&activities[]=101&projects[]=*&start=2013-04-28&end=2013-04-28'
        start_date = datetime.datetime.strptime('20130428', "%Y%m%d").date()
        activities = '101'
        self.assertEquals(wanted_url, base_command._get_zebra_url_for_activities(start_date, activities=activities))

    def testGetZebraUrlForActivitiesWithMultipleActivities(self):
        """returns correct url when specifying multiple activities"""
        base_command = BaseCommand()
        wanted_url = 'timesheet/report/.json?option_selector=&users[]=*&activities[]=101&activities[]=102&projects[]=*&start=2013-04-28&end=2013-04-28'
        start_date = datetime.datetime.strptime('20130428', "%Y%m%d").date()
        activities = [101, 102]
        self.assertEquals(wanted_url, base_command._get_zebra_url_for_activities(start_date, activities=activities))

    def testMax2DatesWith3Dates(self):
        """raise an error if more than 2 dates are specified"""
        base_command = BaseCommand()
        dates = ['2013.05.22', '2013.05.21', '2013.05.20']
        self.assertRaises(InputParametersError, base_command.ensure_max_2_dates, dates)

    def testMax2DatesWith2Dates(self):
        """should not raise any error"""
        base_command = BaseCommand()
        dates = ['2013.05.22', '2013.05.21']
        base_command.ensure_max_2_dates(dates)

    def testMax2DatesWith1Date(self):
        """should not raise any error"""
        base_command = BaseCommand()
        dates = ['2013.05.22']
        base_command.ensure_max_2_dates(dates)

    def testSanitizeInputDates(self):
        """should always return a list"""
        base_command = BaseCommand()
        san = base_command.sanitize_input_dates(None)
        self.assertListEqual([], san, 'should return an empty list if no dates are specified')
        san = base_command.sanitize_input_dates(['2013.05.22'])
        self.assertListEqual(['2013.05.22'], san, 'should return the same list if dates are specified')

    def testSanitizeInputUsers(self):
        """should return None if an empty list is given"""
        base_command = BaseCommand()
        self.assertIsNone(base_command.sanitize_input_users([]))
        self.assertListEqual([111], base_command.sanitize_input_users([111]), 'should return the same users')
        self.assertListEqual([111, 112], base_command.sanitize_input_users([111, 112]), 'should return the same users')

    def testStartAndEndDates(self):
        """should return a tuple with start and end dates as zebra dates"""
        base_command = BaseCommand()
        self.assertEquals(('2013-05-22', None), base_command.get_start_and_end_date(['2013.05.22']))
        self.assertEquals(('2013-05-22', None), base_command.get_start_and_end_date(['22.05.2013']))
        self.assertNotEquals((None, None), base_command.get_start_and_end_date([]), 'if not date is specified, date_start should be yesterday')
        self.assertEquals(('2013-05-21', None), base_command.get_start_and_end_date([]), 'if not date is specified, date_start should be yesterday')

    def testLastWeekDay(self):
        """should return yesterday or friday if today is monday"""
        base_command = BaseCommand()
        monday = datetime.date(2013, 05, 20)
        friday = datetime.date(2013, 05, 17)
        today = datetime.date(2013, 05, 22)
        yesterday = datetime.date(2013, 05, 21)
        self.assertEquals(yesterday, base_command.get_last_week_day(today), 'should return yesterday')
        self.assertEquals(friday, base_command.get_last_week_day(monday), 'should return last friday')
