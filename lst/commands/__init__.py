import dateutil

from lst.errors import DevelopmentError, InputParametersError
from lst.models import AppContainer
from lst.helpers import DateHelper, ZebraHelper
from lst.managers.zebraManager import ZebraManager
from lst.managers.jiraManager import JiraManager


class BaseCommand(object):
    def __init__(self):
        self.secret = AppContainer.secret
        self.config = AppContainer.config
        self.dev_mode = AppContainer.dev_mode

    def add_common_arguments(self, parser):
        parser.add_argument("--dev-mode", action="store_true", help="development mode")
        return parser

    def add_command_arguments(self, subparsers):
        # has to be implemented in all actions
        # the minimum being:
        #   parser = subparsers.add_parser('my-command-name')
        #   return parser
        raise DevelopmentError('Method add_command_arguments must be implemented in all commands')

    def run(self, args):
        pass

    def get_start_and_end_date(self, dates):
        """
        Get a tuple with start and end dates. Default is none for end date, and last week-day for start_date

        :param dates:list of dates
        :return:tuple (start,end)
        """
        date_objects = [dateutil.parser.parse(d, dayfirst=True) for d in dates]

        # default values is None for end_date and last week-day for start_date
        start_date = None
        end_date = None
        if date_objects is None or len(date_objects) == 0:
            date_objects.append(DateHelper.get_last_week_day())

        if len(date_objects) == 1:
            start_date = ZebraHelper.zebra_date(date_objects[0])
        if len(date_objects) == 2:
            start_date = ZebraHelper.zebra_date(min(date_objects))
            end_date = ZebraHelper.zebra_date(max(date_objects))

        return (start_date, end_date)

    def ensure_sprint_in_config(self, sprint_name):
        """

        :rtype : models.Sprint
        """
        sprint = self.config.get_sprint(sprint_name)
        if sprint is None:
            raise InputParametersError(
                "Sprint {} not found. Make sure it's defined in your settings file".format(sprint_name)
            )

        print "Sprint {} found in config".format(sprint_name)

        return sprint

    def get_sprint_name_from_args_or_current(self, optional_argument):
        """
        get a sprint name by parsing command args or by using _current sprint in config

        :param optional_argument:list user input arguments
        :return: string sprint name
        """
        if len(optional_argument) != 0:
            sprint_name = optional_argument[0]
        else:
            sprint_name = self.config.get_current_sprint_name()

        return sprint_name

    def get_jira_manager(self):
        return JiraManager(AppContainer)

    def get_zebra_manager(self):
        return ZebraManager(AppContainer)
