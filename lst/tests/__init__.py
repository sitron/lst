from lst.tests import (
    commands_test,
    helpers_test,
    parser_test,
    retrieve_jira_information_for_config_test,
)


def suite():
    import unittest
    suite = unittest.TestSuite()
    suite.addTests(retrieve_jira_information_for_config_test.suite())
    suite.addTests(commands_test.suite())
    suite.addTests(helpers_test.suite())
    suite.addTests(parser_test.suite())
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
