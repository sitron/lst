class JiraStoryProcessor(object):
    """Base class for all Jira post processors"""

    def post_process(self):
        pass

class SprintBurnUpJiraProcessor(JiraStoryProcessor):
    def __init__(self, closed_status, jira_remote):
        self.closed_status = closed_status
        self.jira_remote = jira_remote

    def post_process(self, story):
        # discard story if it's closed but didn't have the PO review status
        if story.is_over():
            try:
                story.close_date = self.jira_remote.get_story_close_date(
                    story.id,
                    self.closed_status
                )
            except AttributeError:
                print 'Story ' + story.id + ' is discarded as it is closed, but never had the status ' + self.closed_status
                return None
        return story

