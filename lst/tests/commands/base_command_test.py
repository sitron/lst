import unittest
from mock import Mock, MagicMock

from lst.tests.mock_helper import MockHelper

from lst.commands import BaseCommand
from lst.errors import InputParametersError
from lst.helpers import ZebraHelper, DateHelper


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


def suite():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTest(loader.loadTestsFromTestCase(BaseCommandTest))
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
