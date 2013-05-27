from ..commands import BaseCommand, CheckHoursCommand
from ..helpers import *
import unittest
import mock


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


class MockArgs:
    """A minimal class to simulate argparse return"""
    pass

from ..models import AppContainer
from ..parser import SecretParser
from ..remote import ZebraRemote
import json

class CheckHoursTest(unittest.TestCase):
    """Unit tests for check-hours command in commands.py"""

    def testCommandBeforeOutput(self):
        """should return the correct list of projects"""
        args = MockArgs()
        args.user = [103]
        args.date = []
        AppContainer.secret = SecretParser()
        AppContainer.secret.get_zebra = mock.MagicMock(return_value = {'url': 'xx'})
        zebra_remote = ZebraRemote('baseurl', 'username', 'pwd')
        json_data=open('lst/tests/check_hours.json')
        data = json.load(json_data)
        zebra_remote.get_data = mock.MagicMock(return_value=data)

        command = CheckHoursCommand()
        command.get_zebra_remote = mock.MagicMock(return_value=zebra_remote)
        command._output = mock.MagicMock()
        command.run(args)
        entries = command._get_zebra_entries('xx')
        self.assertEquals(3, len(entries), 'should return 3 entries')
        grouped_entries = command._group_entries_by_project(entries)
        self.assertEquals(2, len(grouped_entries), 'there should be 2 projects')
        self.assertTrue(grouped_entries.has_key('Project 2'), 'should have a group Project 2')
        self.assertTrue(grouped_entries.has_key('Project 1'), 'should have a group Project 1')
        self.assertEquals(2, len(grouped_entries['Project 2']), 'project 2 should have 2 entries')
        self.assertEquals(1, len(grouped_entries['Project 1']), 'project 1 should have 1 entry')
