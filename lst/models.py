import datetime


class AppContainer(object):
    config = None
    secret = None
    dev_mode = False
    user_args = None
    pass


class ZebraManager(object):

    @classmethod
    def group_by_project(cls, entries):
        """
        Group zebra entries by project id
        :param entries:list of zebra entries as returned by ZebraRemote.parse_entries
        :return:
        """
        projects = {}
        for zebra_entry in entries:

            if zebra_entry.project not in projects:
                projects[zebra_entry.project] = []

            projects[zebra_entry.project].append(zebra_entry)

        return projects


class ZebraEntry:
    def __init__(self):
        self.username = None
        self.time = 0
        self.date = None
        self.project = None
        self.id = 0
        self.description = None

    def readable_date(self):
        return self.date.strftime('%Y-%m-%d')


class ZebraDays(dict):
    def __init__(self, *args):
        dict.__init__(self, args)
        self.ordered_dates = None

    def get_ordered_dates(self):
        if self.ordered_dates is None:
            self.ordered_dates = sorted(set(self.keys()))
        return self.ordered_dates


class ZebraDay:
    def __init__(self):
        self.time = 0
        self.entries = list()  # list of ZebraEntry
        self.day = ''  # readable day (2012-07-31)
        self.entries_per_user = None

    def get_entries_per_user(self):
        if self.entries_per_user is None:
            self.entries_per_user = {}
            for entry in self.entries:
                try:
                    self.entries_per_user[entry.username] += entry.time
                except KeyError:
                    self.entries_per_user[entry.username] = entry.time
        return self.entries_per_user


class JiraEntry:
    # status codes considered as closed
    closed_status_ids = set()

    def __init__(self):
        self.story_points = 0
        self.business_value = 0
        self.id = None
        self.status = None
        self.close_date = None
        self.is_nice = False
        self.is_ignored = False

    def is_over(self):
        return self.status in JiraEntry.closed_status_ids

    def get_close_day(self):
        return self.close_date.strftime('%Y-%m-%d')


class JiraEntries(list):
    def __init__(self):
        list.__init__([])
        self.total_story_points = 0
        self.total_business_value = 0
        self.achieved_story_points = 0
        self.achieved_business_value = 0
        self.achieved_by_date = {}

    def close_story_filter(self, x):
        return x.is_over() and x.close_date is not None

    def get_achievement_by_day(self):
        if len(self.achieved_by_date) == 0:
            for story in filter(self.close_story_filter, self):
                day = story.get_close_day()
                if day in self.achieved_by_date:
                    self.achieved_by_date[day]['sp'] += story.story_points
                    self.achieved_by_date[day]['bv'] += story.business_value
                else:
                    o = {'sp': story.story_points, 'bv': story.business_value}
                    self.achieved_by_date[day] = o
        return self.achieved_by_date

    def get_achievement_for_day(self, day):
        return self.get_achievement_by_day().get(str(day))

    def get_commited_story_points(self):
        for s in self:
            if s.is_nice:
                continue
            self.total_story_points += s.story_points
        return self.total_story_points

    def get_achieved_story_points(self):
        for s in self:
            if s.is_over():
                self.achieved_story_points += s.story_points
        return self.achieved_story_points

    def get_commited_business_value(self):
        for s in self:
            if s.is_nice:
                continue
            self.total_business_value += s.business_value
        return self.total_business_value

    def get_achieved_business_value(self):
        for s in self:
            if s.is_over():
                self.achieved_business_value += s.business_value
        return self.achieved_business_value


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


class GraphEntries(dict):
    """keeps all the graph entries"""
    def get_ordered_data(self, date_limit=None):
        data = list()
        cumulated_bv = 0
        cumulated_sp = 0
        cumulated_time = 0
        cumulated_planned_time = 0
        for key in sorted(self.iterkeys()):
            value = self[key]
            cumulated_bv += value.business_value
            cumulated_sp += value.story_points
            cumulated_time += value.time
            cumulated_planned_time += value.planned_time
            value.planned_time = cumulated_planned_time / 8

            # only add data if before graph end date
            if date_limit is None or value.date <= date_limit:
                value.business_value = cumulated_bv
                value.story_points = cumulated_sp
                value.time = cumulated_time / 8
            else:
                value.business_value = None
                value.story_points = None
                value.time = None
            data.append(value.to_json())
        return data


class GraphEntry:
    date = None
    business_value = 0
    story_points = 0
    time = 0
    planned_time = 0

    def to_json(self):
        o = {
            'date': str(self.date),
            'planned': self.planned_time
        }
        if self.business_value is not None:
            o['businessValue'] = self.business_value
        if self.story_points is not None:
            o['storyPoints'] = self.story_points
        if self.time is not None:
            o['manDays'] = self.time
        return o
