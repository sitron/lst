from ..commands import *
from ..models import *
from ..parser import *

import unittest
import mock
import json
import xml.etree.ElementTree as ET


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

    def testGetStoryData(self):
        mock_helper = MockHelper()
        jira_remote = JiraRemote('baseurl', 'username', 'pwd')
        data = mock_helper.get_mock_data('lst/tests/jira_project.xml')
        jira_remote.get_data = mock.MagicMock(return_value=data)
        command = BaseCommand()
        command.get_jira_remote = mock.MagicMock(return_value=jira_remote)
        story_data = command.get_story_data('xx-122')
        self.assertEquals('Project XX', story_data['project_name'])
        self.assertEquals('10636', story_data['project_id'])
        self.assertEquals('Sprint name', story_data['sprint_name'])
        self.assertEquals('Sprint+name', story_data['clean_sprint_name'])

    def testEnsureSprintInConfig(self):
        mock_helper = MockHelper()
        command = BaseCommand()

        s = mock_helper.get_sprint()
        command.config.get_sprint = mock.MagicMock(return_value=s)
        self.assertEquals(s, command.ensure_sprint_in_config('in config'))

        command.config.get_sprint = mock.MagicMock(return_value=None)
        self.assertRaises(InputParametersError, command.ensure_sprint_in_config, 'not in config')

    def testGetCurrentSprintNameIfNoArgsSpecified(self):
        command = BaseCommand()
        command.config.get_current_sprint_name = mock.MagicMock(return_value='sprint name')
        self.assertEquals('sprint name', command.get_sprint_name_from_args_or_current(list()))


class MockHelper:
    """A minimal class to simulate argparse return"""
    def __init__(self):
        self.optional_argument = list()

        AppContainer.secret = SecretParser()
        AppContainer.config = ConfigParser()

        AppContainer.secret.get_zebra = mock.MagicMock(
            return_value={
                'url': 'xx'
            }
        )
        AppContainer.secret.get_jira = mock.MagicMock(
            return_value={
                'url': 'xx'
            }
        )
        AppContainer.config.get_sprint = mock.MagicMock(return_value=self.get_sprint())

    def get_sprint(self):
        s = Sprint()
        s.name = 'my sprint'
        return s

    def get_zebra_remote(self):
        return ZebraRemote('baseurl', 'username', 'pwd')

    def get_jira_remote(self):
        return JiraRemote('baseurl', 'username', 'pwd')

    def get_mock_data(self, url):
        data = open(url)
        file_format = url[url.rfind('.') + 1:]
        if file_format == 'json':
            return json.load(data)
        if file_format == 'xml':
            tree = ET.fromstring(data.read())
            return tree


class CheckHoursTest(unittest.TestCase):
    """Unit tests for check-hours command in commands.py"""

    def testCommandBeforeOutput(self):
        """should return the correct list of projects"""
        mock_helper = MockHelper()
        mock_helper.user = [103]
        mock_helper.date = []
        zebra_remote = mock_helper.get_zebra_remote()
        data = mock_helper.get_mock_data('lst/tests/check_hours.json')
        zebra_remote.get_data = mock.MagicMock(return_value=data)

        command = CheckHoursCommand()
        command.get_zebra_remote = mock.MagicMock(return_value=zebra_remote)
        command._output = mock.MagicMock()
        command.run(mock_helper)
        entries = command._get_zebra_entries('xx')
        self.assertEquals(3, len(entries), 'should return 3 entries')
        grouped_entries = command._group_entries_by_project(entries)
        self.assertEquals(2, len(grouped_entries), 'there should be 2 projects')
        self.assertTrue(grouped_entries.has_key('Project 2'), 'should have a group Project 2')
        self.assertTrue(grouped_entries.has_key('Project 1'), 'should have a group Project 1')
        self.assertEquals(2, len(grouped_entries['Project 2']), 'project 2 should have 2 entries')
        self.assertEquals(1, len(grouped_entries['Project 1']), 'project 1 should have 1 entry')


class GetLastZebraEntryTest(unittest.TestCase):
    """Unit tests for get-last-zebra-day command in commands.py"""

    def testGetLastZebraEntry(self):
        mock_helper = MockHelper()
        data = mock_helper.get_mock_data('lst/tests/check_hours.json')
        zebra_remote = mock_helper.get_zebra_remote()
        zebra_remote.get_data = mock.MagicMock(return_value=data)

        command = GetLastZebraDayCommand()
        command.get_zebra_remote = mock.MagicMock(return_value=zebra_remote)
        url = 'xxx'
        last_entry = command.get_last_zebra_entry(url)

        self.assertEquals('2013-05-25', ZebraHelper.zebra_date(last_entry.date))
