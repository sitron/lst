import datetime, unittest
from ..helpers import *
import mock


class InputHelperTest(unittest.TestCase):
    """Unit tests for InputHelper in helpers.py"""

    def testSanitizeInputDates(self):
        """should always return a list"""
        san = InputHelper.sanitize_dates(None)
        self.assertListEqual([], san, 'should return an empty list if no dates are specified')
        san = InputHelper.sanitize_dates(['2013.05.22'])
        self.assertListEqual(['2013.05.22'], san, 'should return the same list if dates are specified')

    def testSanitizeInputUsers(self):
        """should return None if an empty list is given"""
        self.assertIsNone(InputHelper.sanitize_users([]))
        self.assertListEqual([111], InputHelper.sanitize_users([111]), 'should return the same users')
        self.assertListEqual([111, 112], InputHelper.sanitize_users([111, 112]), 'should return the same users')

    def testMax2DatesWith3Dates(self):
        """raise an error if more than 2 dates are specified"""
        dates = ['2013.05.22', '2013.05.21', '2013.05.20']
        self.assertRaises(InputParametersError, InputHelper.ensure_max_2_dates, dates)

    def testMax2DatesWith2Dates(self):
        """should not raise any error"""
        dates = ['2013.05.22', '2013.05.21']
        InputHelper.ensure_max_2_dates(dates)

    def testMax2DatesWith1Date(self):
        """should not raise any error"""
        dates = ['2013.05.22']
        InputHelper.ensure_max_2_dates(dates)

    def testGetUserInput(self):
        """test getting and formating user input"""
        self.assertEquals('string', InputHelper.get_user_input('input a string', str, lambda _:'string'))
        self.assertEquals(10, InputHelper.get_user_input('input an int', int, lambda _:10))
        self.assertEquals(10.00, InputHelper.get_user_input('input a float', float, lambda _:10.00))
        self.assertEquals(10.00, InputHelper.get_user_input('input a float', float, lambda _:'10'))
        date = datetime.date(2013, 05, 27)
        self.assertEquals(date, InputHelper.get_user_input('input a date', 'date', lambda _:'2013-05-27'))
        self.assertEquals(date, InputHelper.get_user_input('input a date', 'date', lambda _:'27.05.2013'))
        self.assertEquals(date, InputHelper.get_user_input('input a date', 'date', lambda _:'05.27.2013'))
        self.assertRaises(InputParametersError, InputHelper.get_user_input, 'not an int', int, lambda _:'not an int')
        self.assertRaises(
            InputParametersError, InputHelper.get_user_input, 'not a float', float, lambda _:'not a float'
        )


class DateHelperTest(unittest.TestCase):
    """Unit tests for DateHelper in helpers.py"""

    def testLastWeekDay(self):
        """should return yesterday or friday if today is monday"""
        monday = datetime.date(2013, 05, 20)
        friday = datetime.date(2013, 05, 17)
        today = datetime.date(2013, 05, 22)
        yesterday = datetime.date(2013, 05, 21)
        self.assertEquals(yesterday, DateHelper.get_last_week_day(today), 'if not monday, should return yesterday')
        self.assertEquals(friday, DateHelper.get_last_week_day(monday), 'if monday should return last friday')


class ZebraHelperTest(unittest.TestCase):
    """Unit test for ZebraHelper in helpers.py"""

    def testGetZebraUrlForActivitiesWithDefaultArgs(self):
        """returns correct url with default arguments"""
        wanted_url = 'timesheet/report/.json?option_selector=&users[]=*&activities[]=*&projects[]=*&start=2013-04-28&end=2013-04-28'
        start_date = datetime.datetime.strptime('20130428', "%Y%m%d").date()
        self.assertEquals(wanted_url, ZebraHelper.get_zebra_url_for_activities(start_date))

    def testGetZebraUrlForActivitiesWithOneUser(self):
        """returns correct url when specifying 1 user"""
        wanted_url = 'timesheet/report/.json?option_selector=&users[]=101&activities[]=*&projects[]=*&start=2013-04-28&end=2013-04-28'
        start_date = datetime.datetime.strptime('20130428', "%Y%m%d").date()
        users = 101
        self.assertEquals(wanted_url, ZebraHelper.get_zebra_url_for_activities(start_date, users=users))

    def testGetZebraUrlForActivitiesWithMultipleUsers(self):
        """returns correct url when specifying multiple users"""
        wanted_url = 'timesheet/report/.json?option_selector=&users[]=101&users[]=102&activities[]=*&projects[]=*&start=2013-04-28&end=2013-04-28'
        start_date = datetime.datetime.strptime('20130428', "%Y%m%d").date()
        users = [101, 102]
        self.assertEquals(wanted_url, ZebraHelper.get_zebra_url_for_activities(start_date, users=users))

    def testGetZebraUrlForActivitiesWithOneUserAsString(self):
        """returns correct url when specifying one user as string"""
        wanted_url = 'timesheet/report/.json?option_selector=&users[]=101&activities[]=*&projects[]=*&start=2013-04-28&end=2013-04-28'
        start_date = datetime.datetime.strptime('20130428', "%Y%m%d").date()
        users = '101'
        self.assertEquals(wanted_url, ZebraHelper.get_zebra_url_for_activities(start_date, users=users))

    def testGetZebraUrlForActivitiesWithOneActivity(self):
        """returns correct url when specifying one activity"""
        wanted_url = 'timesheet/report/.json?option_selector=&users[]=*&activities[]=101&projects[]=*&start=2013-04-28&end=2013-04-28'
        start_date = datetime.datetime.strptime('20130428', "%Y%m%d").date()
        activities = '101'
        self.assertEquals(wanted_url, ZebraHelper.get_zebra_url_for_activities(start_date, activities=activities))

    def testGetZebraUrlForActivitiesWithMultipleActivities(self):
        """returns correct url when specifying multiple activities"""
        wanted_url = 'timesheet/report/.json?option_selector=&users[]=*&activities[]=101&activities[]=102&projects[]=*&start=2013-04-28&end=2013-04-28'
        start_date = datetime.datetime.strptime('20130428', "%Y%m%d").date()
        activities = [101, 102]
        self.assertEquals(wanted_url, ZebraHelper.get_zebra_url_for_activities(start_date, activities=activities))

    def testZebraDate(self):
        """date format is correct"""
        date = datetime.datetime.strptime('20130428', "%Y%m%d").date()
        self.assertEquals('2013-04-28', ZebraHelper.zebra_date(date))

    def testGetActivityId(self):
        self.assertEquals('basepath/timesheet/123', ZebraHelper.get_activity_url('basepath', 123))


class JiraHelperTest(unittest.TestCase):
    """Unit test for JiraHelper in helpers.py"""

    def testGetUrlForProjectLookupByStoryId(self):
        wanted_url = "/sr/jira.issueviews:searchrequest-xml/temp/SearchRequest.xml" \
                     "?jqlQuery=key+%3D+'xx-112'" \
                     "&tempMax=1000"
        story_id = 'xx-112'
        self.assertEquals(wanted_url, JiraHelper.get_url_for_project_lookup_by_story_id(story_id))

    def testSanitizeSprintName(self):
        self.assertEquals(
            'my+sprint+name',
            JiraHelper.sanitize_sprint_name('my sprint name')
        )
        self.assertEquals(
            'MySprintName',
            JiraHelper.sanitize_sprint_name('MySprintName')
        )
