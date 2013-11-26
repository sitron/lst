import datetime


class AppContainer(object):
    config = None
    secret = None
    dev_mode = False
    user_args = None
    pass


class Sprint:
    def __init__(self):
        self.name = ''
        self.raw = None
        self.forced = dict()
        self.planned = dict()
        self.commited_man_days = 0
        self.jira_data = None
        self.zebra_data = None
        self.raw = None
        self.default_closed_statuses = {6: 'closed'}
        self.timesheets = None  # TimeSheetCollection
        self.stories = None  # StoryCollection

    def get_closed_statuses(self):
        statuses = self.get_jira_data('closed_statuses')
        return self.default_closed_statuses if statuses is None else statuses

    def get_closed_status_codes(self):
        statuses = self.get_closed_statuses()
        return statuses.keys()

    def get_closed_status_names(self):
        statuses = self.get_closed_statuses()
        return statuses.values()

    def get_forced_data(self, date, default):
        forced = self.forced.get(date, default)
        if type(forced) == str:
            return default + float(forced)
        return forced

    def get_planned_data(self, date):
        return self.planned.get(date)

    def get_zebra_data(self, key):
        return self.zebra_data.get(key)

    def get_jira_data(self, key):
        return self.jira_data.get(key)

    def get_all_days(self, max_today=True):
        """return all days from sprint start to sprint end or today (depending on the max_today value)"""
        start = self.get_zebra_data('start_date')
        end = self.get_zebra_data('end_date')
        all_days = list()

        if max_today:
            today = datetime.datetime.now().date()
            if end > today:
                end = today

        dateDelta = end - start

        for i in range(dateDelta.days + 1):
            date = start + datetime.timedelta(days=i)
            all_days.append(date)
        return all_days

    def get_title(self):
        return self.jira_data.get('sprint_name').replace('+', ' ') + ' (' + self.name + ')'
