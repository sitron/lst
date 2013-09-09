from ..parser import SecretParser
from ..parser import ConfigParser
from ..errors import FileNotFoundError, SyntaxError
import unittest
from datetime import date

class ParserTest(unittest.TestCase):
    """Unit tests for parser.py"""

    def testFileNotFound(self):
        """a FileNotFoundError should be raised if .lst-secret.yml is not found"""
        secret = SecretParser()
        self.assertRaises(FileNotFoundError, secret.parse, 'xx')

    def testExtractData(self):
        """extract_data should not raise any error"""
        secret = SecretParser()
        config = {'zebra': 'xx', 'jira': 'xx', 'output_dir': 'xx'}
        secret.extract_data(config)
        self.assertTrue(secret.zebra_data is not None)
        self.assertTrue(secret.jira_data is not None)
        self.assertTrue(secret.output_dir is not None)

    def testSyntaxErrorOnExtractData(self):
        """a SyntaxError should be raised if .lst-secret.yml structure is not ok"""
        secret = SecretParser()
        config = {'zebra': 'xx', 'jira': 'xx'}
        self.assertRaises(SyntaxError, secret.extract_data, config)

    def testOutputDirEndsWithSlash(self):
        """get_output_dir should end with a slash"""
        secret = SecretParser()
        config = {'zebra': 'xx', 'jira': 'xx', 'output_dir': 'xx'}
        secret.extract_data(config)
        self.assertEquals('xx/', secret.get_output_dir())

    def testParsingPlannedSection(self):
        parser = ConfigParser()
        config = [1,2,0,3]
        result = parser.parse_planned(config, date(2005, 1, 5), date(2005, 1, 10))
        self.assertEquals({'2005-01-05': 1, '2005-01-06': 2, '2005-01-07': 0, '2005-01-10': 3}, result)
        with self.assertRaises(SyntaxError):
            parser.parse_planned([1,2,3], date(2005, 1, 5), date(2005, 1, 10))
        with self.assertRaises(SyntaxError):
            parser.parse_planned([1,2,3,4,5], date(2005, 1, 5), date(2005, 1, 10))

