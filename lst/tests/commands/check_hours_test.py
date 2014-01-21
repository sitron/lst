import unittest
from mock import Mock, MagicMock

from lst.tests.mock_helper import MockHelper

from lst.commands.check_hours import CheckHoursCommand


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
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
