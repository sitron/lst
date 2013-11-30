import pickle

from models.jiraModels import StoryCollection, Story
from remote import JiraRemote
from processors import CloseDateProcessor


class JiraManager:
    """
    Responsible for interfacing the application with JiraRemote
    """
    def __init__(self, app_container):
        self.app_container = app_container

    def get_stories_for_sprint_with_end_date(self, sprint):
        """
        Get stories for specified sprint and retrieve each story "close" date (by running a specific post processor)

        :param sprint:Sprint
        :return:StoryCollection
        """
        closed_status_names = sprint.get_closed_status_names()
        post_processor = CloseDateProcessor(closed_status_names, self)

        return self._get_stories_for_sprint(sprint, post_processor)

    def get_stories_for_sprint(self, sprint):
        """
        Get stories for specified sprint

        :param sprint:Sprint
        :return:StoryCollection
        """
        return self._get_stories_for_sprint(sprint)

    def get_story(self, story_id):
        """
        Get a single story by id

        :param story_id:string
        :return:Story|None
        """
        remote = self._get_jira_remote()
        url = remote.get_url_for_project_lookup_by_story_id(story_id)
        stories = self.get_stories_by_url(url)

        if len(stories) == 0:
            print 'No story found with id {}'.format(story_id)
            return None

        return stories[0]

    def get_stories_by_url(self, url, nice_identifier=None, ignored=None, post_processor=None):
        """
        Get stories by specifying a jira url

        :param url:string jira url
        :param nice_identifier:string part of story title which enables to identify "nice to have" stories
        :param ignored:list list of story ids that should be discarded
        :param post_processor:JiraStoryPostProcessor last action called on each story after parsing
        :return:StoryCollection
        """
        remote = self._get_jira_remote()
        result = remote.get_data(url)
        stories = self.parse_stories(
            result,
            nice_identifier,
            ignored,
            post_processor
        )
        # pickle.dump(stories, open("jira_entries.p", "wb"))
        # stories = pickle.load(open("jira_entries.p", "rb"))

        return stories

    def _get_stories_for_sprint(self, sprint, post_processor=None):
        url = self._get_url_for_sprint_burnup(sprint)
        return self.get_stories_by_url(url,
                                       nice_identifier=sprint.get_jira_data('nice_identifier'),
                                       ignored=sprint.get_jira_data('ignored'),
                                       post_processor=post_processor
                                       )

    def get_story_close_date(self, id, closed_status_names):
        return self._get_jira_remote().get_story_close_date(id, closed_status_names)

    def parse_stories(
            self,
            response_xml,
            nice_identifier=None,
            ignored=None,
            post_processor=None
    ):
        """
        Parse xml result into list of stories

        :param response_xml:xml xml result from remote call
        :param nice_identifier:string story title substring
        :param ignored:list list of story ids to be ignored
        :param post_processor:JiraStoryProcessor Subclass of JiraStoryProcessor
        :return:StoryCollection list of Story(s)
        """
        stories = StoryCollection()

        xml_stories = response_xml[0].findall('item')

        for s in xml_stories:
            story = Story()
            story.id = s.find('key').text

            # check if the story should be ignored (see ignore in config)
            if ignored is not None and story.id in ignored:
                print 'story {} is ignored'.format(story.id)
                continue

            # check if the story is a 'nice to have'
            if nice_identifier is not None:
                story.is_nice = s.find('title').text.find(nice_identifier) != -1

            # status
            story.status = int(s.find('status').get('id'))

            # business value
            try:
                story.business_value = float(
                    s.find(
                        './customfields/customfield/[@id="customfield_10064"]/customfieldvalues/customfieldvalue'
                    ).text
                )
            except AttributeError:
                print 'Story {} has no business value defined, 0 taken as default'.format(story.id)

            # story points
            try:
                story.story_points = float(
                    s.find(
                        './customfields/customfield/[@id="customfield_10040"]/customfieldvalues/customfieldvalue'
                    ).text
                )
            except AttributeError:
                print 'Story {} has no story points defined, 0 taken as default'.format(story.id)

            # post processor
            if post_processor is not None:
                story = post_processor.post_process(story)
                if story is None:
                    continue

            # other attributes
            if s.find('project') is not None and s.find('project').get('id') is not None:
                story.project_id = s.find('project').get('id')
                story.project_name = s.find('project').text
            if s.find('fixVersion') is not None:
                story.sprint_name = s.find('fixVersion').text

            stories.append(story)

        return stories

    def _get_jira_remote(self):
        return JiraRemote(
            self.app_container.secret.get_jira('url'),
            self.app_container.secret.get_jira('username'),
            self.app_container.secret.get_jira('password')
        )

    def _get_url_for_sprint_burnup(self, sprint):
        return "/sr/jira.issueviews:searchrequest-xml/temp/SearchRequest.xml?jqlQuery=project+%3D+'" + str(sprint.get_jira_data('project_id')) + "'+and+fixVersion+%3D+'" + sprint.get_jira_data('sprint_name') + "'&tempMax=1000"
