from lst.tests import (
    helpers_test,
    parser_test,
    zebra_manager_test,
)
from lst.tests.commands import (
    retrieve_jira_information_for_config_test,
    base_command_test,
    check_hours_test,
    retrieve_user_id_test,
)


def suite():
    import unittest
    suite = unittest.TestSuite()
    suite.addTests(retrieve_jira_information_for_config_test.suite())
    suite.addTests(base_command_test.suite())
    suite.addTests(retrieve_user_id_test.suite())
    suite.addTests(check_hours_test.suite())
    suite.addTests(helpers_test.suite())
    suite.addTests(parser_test.suite())
    suite.addTests(zebra_manager_test.suite())
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
