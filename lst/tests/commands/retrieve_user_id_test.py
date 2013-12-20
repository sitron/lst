import unittest
from mock import Mock, MagicMock

from lst.tests.mock_helper import MockHelper

from lst.commands.retrieve_user_id import RetrieveUserIdCommand
from lst.errors import IOError


class RetrieveUserIdTest(unittest.TestCase):
    """Unit tests for get-user-id command"""

    mock_users = [
        {'employee_lastname': 'prodon', 'employee_firstname': 'laurent', 'id': 1},
        {'employee_lastname': 'mao', 'employee_firstname': 'rolf', 'id': 2},
        {'employee_lastname': 'tsetung', 'employee_firstname': 'mao', 'id': 3},
    ]

    def testSingleUser(self):
        """should return the correct user id"""


        # mock user arguments
        mock_helper = MockHelper()
        mock_helper.lastname = ['prodon']

        # mock the zebra manager and its return values
        zebra_manager = mock_helper.get_zebra_manager()
        zebra_manager.get_all_users = MagicMock(return_value=self.mock_users)

        command = RetrieveUserIdCommand()
        command.get_zebra_manager = MagicMock(return_value=zebra_manager)

        # run the command
        output_mock = command._output = Mock()
        command.run(mock_helper)

        expected_result = self.mock_users[0]

        self.assertEquals(([expected_result], ['prodon']), output_mock.call_args[0])

    def testMultipleUsers(self):
        """should return the correct user ids"""

        # mock user arguments
        mock_helper = MockHelper()
        mock_helper.lastname = ['prodon', 'tsetung']

        # mock the zebra manager and its return values
        zebra_manager = mock_helper.get_zebra_manager()
        zebra_manager.get_all_users = MagicMock(return_value=self.mock_users)

        command = RetrieveUserIdCommand()
        command.get_zebra_manager = MagicMock(return_value=zebra_manager)

        # run the command
        output_mock = command._output = Mock()
        command.run(mock_helper)

        expected_result = [self.mock_users[0], self.mock_users[2]]

        self.assertEquals((expected_result, ['prodon', 'tsetung']), output_mock.call_args[0])

    def testIOProblem(self):
        """should raise an IOError"""

        # mock user arguments
        mock_helper = MockHelper()
        mock_helper.lastname = ['prodon', 'tsetung']

        # mock the zebra manager and its return values
        zebra_manager = mock_helper.get_zebra_manager()
        zebra_manager.get_all_users = MagicMock(return_value=[])

        command = RetrieveUserIdCommand()
        command.get_zebra_manager = MagicMock(return_value=zebra_manager)

        # run the command
        command._output = Mock()
        self.assertRaises(IOError, command.run, mock_helper)


def suite():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTest(loader.loadTestsFromTestCase(RetrieveUserIdTest))
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
