from lst.commands import BaseCommand
from lst.helpers import ArgParseHelper, JiraHelper


class RetrieveJiraInformationForConfigCommand(BaseCommand):
    """
    Usage: jira-config-helper [story-id] (ie: jira-config-helper jlc-112)

    """
    def add_command_arguments(self, subparsers):
        parser = subparsers.add_parser('jira-config-helper')
        ArgParseHelper.add_user_story_id_argument(parser)
        return parser

    def run(self, args):
        story_id = args.story_id.upper()

        jira_manager = self.get_jira_manager()
        story = jira_manager.get_story(story_id)
        clean_sprint_name = JiraHelper.sanitize_sprint_name(story.sprint_name)

        self._output(story, clean_sprint_name)

    def _output(self, story, clean_sprint_name):
        print ''
        print 'Project info for story {}'.format(story.id)
        print 'id: {}'.format(story.project_id)
        print 'name: {}'.format(story.project_name)
        print 'sprint name: {}'.format(story.sprint_name)
        print 'sprint name for config: {}'.format(clean_sprint_name)
