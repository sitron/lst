import unittest
import json
import datetime
from mock import Mock, MagicMock

from lst.models import AppContainer, Sprint
from lst.parser import SecretParser, ConfigParser
from lst.commands import BaseCommand
from lst.commands.check_hours import CheckHoursCommand
from lst.managers.zebraManager import ZebraManager
from lst.managers.jiraManager import JiraManager
from lst.errors import InputParametersError
from lst.helpers import ZebraHelper, DateHelper


class MockHelper:
    """A minimal class to simulate argparse return"""
    def __init__(self):
        self.optional_argument = list()

        AppContainer.secret = SecretParser()
        AppContainer.config = ConfigParser()

        AppContainer.secret.get_zebra = MagicMock(
            return_value={
                'url': 'xx'
            }
        )
        AppContainer.secret.get_jira = MagicMock(
            return_value={
                'url': 'xx'
            }
        )
        AppContainer.config.get_sprint = MagicMock(return_value=self.get_sprint())

    def get_sprint(self):
        s = Sprint()
        s.name = 'my sprint'
        return s

    def get_zebra_manager(self):
        return ZebraManager(AppContainer)

    def get_jira_manager(self):
        return JiraManager(AppContainer)

    def get_mock_data(self, url):
        data = open(url)
        file_format = url[url.rfind('.') + 1:]
        if file_format == 'json':
            return json.load(data)
        if file_format == 'xml':
            tree = ET.fromstring(data.read())
            return tree


class BaseCommandTest(unittest.TestCase):
    """Unit tests for BaseCommand in commands.py"""

    def testStartAndEndDates(self):
        """should return a tuple with start and end dates as zebra dates"""
        base_command = BaseCommand()
        self.assertEquals(
            ('2013-05-22', None),
            base_command.get_start_and_end_date(['2013.05.22']),
            'test input format 1'
        )
        self.assertEquals(
            ('2013-05-22', None),
            base_command.get_start_and_end_date(['22.05.2013']),
            'test input format 2'
        )
        self.assertNotEquals(
            (None, None),
            base_command.get_start_and_end_date([]),
            'if no date is specified, date_start should not be None'
        )
        last_week_day = ZebraHelper.zebra_date(DateHelper.get_last_week_day())
        self.assertEquals(
            (last_week_day, None),
            base_command.get_start_and_end_date([]),
            'if no date is specified, date_start should be last week day'
        )

    def testEnsureSprintInConfig(self):
        mock_helper = MockHelper()
        command = BaseCommand()

        s = mock_helper.get_sprint()
        command.config.get_sprint = MagicMock(return_value=s)
        self.assertEquals(s, command.ensure_sprint_in_config('in config'))

        command.config.get_sprint = MagicMock(return_value=None)
        self.assertRaises(InputParametersError, command.ensure_sprint_in_config, 'not in config')

    def testGetCurrentSprintNameIfNoArgsSpecified(self):
        command = BaseCommand()
        command.config.get_current_sprint_name = MagicMock(return_value='sprint name')
        self.assertEquals('sprint name', command.get_sprint_name_from_args_or_current(list()))


class CheckHoursTest(unittest.TestCase):
    """Unit tests for check-hours command in commands.py"""

    def testCommand(self):
        """should return the correct list of projects"""

        # mock user arguments
        mock_helper = MockHelper()
        mock_helper.user = [103]
        mock_helper.date = []
        data = mock_helper.get_mock_data('lst/tests/check_hours.json')

        # mock the zebra manager and its return values
        zebra_manager = mock_helper.get_zebra_manager()
        timesheets = zebra_manager._parse_timesheets(data)
        zebra_manager.get_all_timesheets = MagicMock(return_value=timesheets)

        command = CheckHoursCommand()
        command.get_zebra_manager = MagicMock(return_value=zebra_manager)

        # verify the projects data returned
        projects = command._get_projects(mock_helper.date, mock_helper.user)

        self.assertEquals(2, len(projects), 'The should be 2 projects')
        self.assertTrue('A Project 1' == projects[0][0], 'Projects should be ordered alphabetically')
        self.assertTrue('B Project 2' == projects[1][0], 'Projects should be ordered alphabetically')
        self.assertEquals(1, len(projects[0][1]), 'A Project should contain 1 timesheets')
        self.assertEquals(2, len(projects[1][1]), 'B Project should contain 2 timesheets')

        # run the command
        command._output = Mock()
        command.run(mock_helper)


def suite():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTest(loader.loadTestsFromTestCase(CheckHoursTest))
    suite.addTest(loader.loadTestsFromTestCase(BaseCommandTest))
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
