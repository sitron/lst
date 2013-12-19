import unittest
from mock import Mock, MagicMock

from lst.tests.mock_helper import MockHelper

from lst.models.jiraModels import Story
from lst.commands.retrieve_jira_information_for_config import RetrieveJiraInformationForConfigCommand


class RetrieveJiraInformationForConfigTest(unittest.TestCase):
    """Unit tests for jira-config-helper command"""

    def testCommand(self):
        """should return the correct data for the story"""

        # mock user arguments
        mock_helper = MockHelper()
        mock_helper.story_id = 'pro-xx'
        data = Story()
        data.sprint_name = 'my sprint name'

        # mock the jira manager and its return values
        jira_manager = mock_helper.get_jira_manager()
        jira_manager.get_story = MagicMock(return_value=data)

        command = RetrieveJiraInformationForConfigCommand()
        command.get_jira_manager = MagicMock(return_value=jira_manager)

        output_mock = Mock()
        command._output = output_mock
        command.run(mock_helper)
        self.assertEquals((data, 'my+sprint+name'), output_mock.call_args[0])


def suite():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTest(loader.loadTestsFromTestCase(RetrieveJiraInformationForConfigTest))
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
