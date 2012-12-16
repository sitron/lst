class JiraStoryProcessor(object):
    """Base class for all Jira post processors"""

    def post_process(self):
        pass

class SprintBurnUpJiraProcessor(JiraStoryProcessor):
    def __init__(self, closed_status, jira_remote):
        self.closed_status = closed_status
        self.jira_remote = jira_remote

    def post_process(self, story):
        # make sure the story shound not be ignored
        if story.is_ignored:
            return None

        # check on what day the story was closed
        if story.is_over():
            try:
                story.close_date = self.jira_remote.get_story_close_date(
                    story.id,
                    self.closed_status
                )
            except AttributeError:
                print 'Can\'t find closing date for story %s (looking for status \'%s\'). Story will be discarded for sprint graph' % (
                    story.id,
                    self.closed_status
                )
                return None
        return story

