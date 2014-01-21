import yaml
import os
import sys
import distutils.sysconfig
import datetime
import dateutil
import re

from lst.remote import ZebraRemote, JiraRemote
from lst.models.jiraModels import *
from lst.models.zebraModels import *
from lst.models import *
from lst.output import *
from lst.errors import *
from lst.helpers import *
from lst.parser import ConfigParser
from lst.managers.jiraManager import JiraManager
from lst.managers.zebraManager import ZebraManager


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
            raise InputParametersError("Sprint %s not found. Make sure it's defined in your settings file" % (sprint_name))

        print "Sprint %s found in config" % (sprint.name)

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


class GetLastZebraDayCommand(BaseCommand):
    """
    Usage:  get-last-zebra-day [sprint_name]

    Get the last day for which data was pushed to zebra (on specified sprint)
    """
    def add_command_arguments(self, subparsers):
        parser = subparsers.add_parser('get-last-zebra-day')
        ArgParseHelper.add_sprint_name_argument(parser)
        return parser

    def run(self, args):
        sprint_name = self.get_sprint_name_from_args_or_current(args.sprint_name)
        sprint = self.ensure_sprint_in_config(sprint_name)

        # force sprint end_date to today
        end_date = datetime.date.today()
        sprint.zebra_data['end_date'] = end_date

        zebra_manager = self.get_zebra_manager()
        zebra_entries = zebra_manager.get_timesheets_for_sprint(sprint)
        last_entry = zebra_entries[-1]

        self._output(sprint_name, last_entry)

    def _output(self, sprint_name, last_entry):
        print ''
        print 'last date for sprint {}: {}'.format(sprint_name, last_entry.readable_date())
