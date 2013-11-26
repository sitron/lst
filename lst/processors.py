class JiraStoryProcessor(object):
    """Base class for all Jira post processors"""

    def post_process(self, story):
        """
        Post processing on story (check close date for ex.) for optional checks

        :param story: Story
        :return modified story or None if story should be discarted
        """
        pass


class CloseDateProcessor(JiraStoryProcessor):
    def __init__(self, closed_status_names, jira_manager):
        self.closed_status_names = closed_status_names
        self.jira_manager = jira_manager

    def post_process(self, story):
        # check on what day the story was closed
        if story.is_over():
            story.close_date = self.jira_manager.get_story_close_date(
                story.id,
                self.closed_status_names
            )
            if story.close_date is None:
                print 'Story %s seems to be over, but i can\'t find a closing date for it (looking for statuses \'%s\' in its activity logs). Story will be discarded for sprint graph' % (
                    story.id,
                    self.closed_status_names
                )
                return None
        return story
