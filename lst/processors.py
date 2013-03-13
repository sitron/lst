class JiraStoryProcessor(object):
    """Base class for all Jira post processors"""

    def post_process(self):
        pass

class SprintBurnUpJiraProcessor(JiraStoryProcessor):
    def __init__(self, closed_status_names, jira_remote):
        self.closed_status_names = closed_status_names
        self.jira_remote = jira_remote

    def post_process(self, story):
        # check on what day the story was closed
        if story.is_over():
            story.close_date = self.jira_remote.get_story_close_date(
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

