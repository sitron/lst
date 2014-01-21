import json
from mock import Mock, MagicMock

from lst.models import AppContainer, Sprint
from lst.parser import SecretParser, ConfigParser
from lst.managers.zebraManager import ZebraManager
from lst.managers.jiraManager import JiraManager


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
