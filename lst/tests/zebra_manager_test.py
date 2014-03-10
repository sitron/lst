import unittest

from lst.managers.zebraManager import ZebraManager
from lst.models import AppContainer
from lst.errors import DevelopmentError


class GetZebraUrlForActivitiesTest(unittest.TestCase):
    """Unit tests for _get_zebra_url_for_activities"""

    def testNoExternalProjects(self):
        """should return a url with projects[]=*"""
        zebraManager = ZebraManager(AppContainer)

        projects = None
        start_date = '2013-02-02'

        url = zebraManager._get_zebra_url_for_activities(start_date=start_date, projects=projects)
        self.assertIn('projects[]=*', url)
        self.assertNotIn('internal[]=', url)

    def testListOfExternalProjects(self):
        """should return a url with projects[]= for each project"""
        zebraManager = ZebraManager(AppContainer)

        projects = [12, 14]
        start_date = '2013-02-02'

        url = zebraManager._get_zebra_url_for_activities(start_date=start_date, projects=projects)
        self.assertIn('projects[]=12', url)
        self.assertIn('projects[]=14', url)
        self.assertNotIn('projects[]=*', url)
        self.assertNotIn('internal[]=', url)

    def testStringOfExternalProjects(self):
        """should return a url with projects[]=string"""
        zebraManager = ZebraManager(AppContainer)

        projects = '12'
        start_date = '2013-02-02'

        url = zebraManager._get_zebra_url_for_activities(start_date=start_date, projects=projects)
        self.assertIn('projects[]=12', url)
        self.assertNotIn('projects[]=*', url)
        self.assertNotIn('internal[]=', url)

    def testNoInternalProjects(self):
        """should return a url without internal[]"""
        zebraManager = ZebraManager(AppContainer)

        projects = None
        internal_projects = None
        start_date = '2013-02-02'
        project_type_to_consider = 'external'

        url = zebraManager._get_zebra_url_for_activities(
            start_date=start_date,
            projects=projects,
            internal_projects=internal_projects,
            project_type_to_consider=project_type_to_consider
        )
        self.assertIn('projects[]=*', url)
        self.assertNotIn('internal[]=', url)

    def testInternalProjects(self):
        """should return a url with internal[]= for each internal project"""
        zebraManager = ZebraManager(AppContainer)

        projects = None
        internal_projects = [12, 14]
        start_date = '2013-02-02'
        project_type_to_consider = 'internal'

        url = zebraManager._get_zebra_url_for_activities(
            start_date=start_date,
            projects=projects,
            internal_projects=internal_projects,
            project_type_to_consider=project_type_to_consider
        )
        self.assertNotIn('projects[]=', url)
        self.assertIn('internal[]=12', url)
        self.assertIn('internal[]=14', url)

    def testAllProjects(self):
        """should return a url with both internal[]= and projects[]= for each project"""
        zebraManager = ZebraManager(AppContainer)

        projects = [2, 3]
        internal_projects = [12, 14]
        start_date = '2013-02-02'
        project_type_to_consider = 'all'

        url = zebraManager._get_zebra_url_for_activities(
            start_date=start_date,
            projects=projects,
            internal_projects=internal_projects,
            project_type_to_consider=project_type_to_consider
        )
        self.assertNotIn('projects[]=*', url)
        self.assertNotIn('internal[]=*', url)
        self.assertIn('internal[]=12', url)
        self.assertIn('internal[]=14', url)
        self.assertIn('projects[]=2', url)
        self.assertIn('projects[]=3', url)

    def testAllProjectsUsingDefault(self):
        """should return a url with both internal[]=* and projects[]=*"""
        zebraManager = ZebraManager(AppContainer)

        projects = None
        internal_projects = None
        start_date = '2013-02-02'
        project_type_to_consider = 'all'

        url = zebraManager._get_zebra_url_for_activities(
            start_date=start_date,
            projects=projects,
            internal_projects=internal_projects,
            project_type_to_consider=project_type_to_consider
        )
        self.assertIn('projects[]=*', url)
        self.assertIn('internal[]=*', url)

    def testNoStartDate(self):
        """should raise an error"""
        zebraManager = ZebraManager(AppContainer)

        projects = [2, 3]
        start_date = None

        self.assertRaises(
            DevelopmentError,
            zebraManager._get_zebra_url_for_activities,
            start_date=start_date,
            projects=projects
        )


def suite():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTest(loader.loadTestsFromTestCase(GetZebraUrlForActivitiesTest))
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
