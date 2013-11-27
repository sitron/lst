import datetime
from collections import OrderedDict

from helpers import MathHelper


class AppContainer(object):
    config = None
    secret = None
    dev_mode = False
    user_args = None
    pass


class Serie(list):
    def __init__(self):
        list.__init__([])
        self.name = ''
        self.ideal_value = None

    def get_max_value(self):
        return 0 if len(self) == 0 else self[-1]

    def get_commited_value(self):
        return self.ideal_value

    def get_values_as_percent(self):
        return MathHelper.get_values_as_percent(self, (0, self.get_commited_value()))

    def get_result_as_percent(self):
        if self.get_max_value() == 0:
            return 0
        return (self.get_max_value() / self.get_commited_value()) * 100

    def cumulate(self, value):
        """
        Adds a new value which is the last serie value + the new one
        Works also if serie is empty and/or the new element is None
        :param value:float value to add to list
        """
        last = 0 if len(self) == 0 else self[-1]
        if value is None:
            self.append(last)
        else:
            self.append(last + value)


class ManDaySerie(Serie):
    def __init__(self):
        super(ManDaySerie, self).__init__()

    def get_max_value(self):
        return 0 if len(self) == 0 else self[-1] / 8

    def get_commited_value(self):
        return self.ideal_value / 8

    def get_values_as_percent(self):
        values = MathHelper.get_values_as_percent(self, (0, self.ideal_value))
        return values


class SerieCollection(OrderedDict):
    def __init__(self):
        super(SerieCollection, self).__init__()

    def get_series_for_chart(self):
        series = OrderedDict()
        for name, serie in self.items():
            if serie.get_commited_value() != 0 and serie.get_commited_value() is not None:
                series[name] = serie

        return series


class SprintBurnupSeries(SerieCollection):
    def __init__(self):
        super(SprintBurnupSeries, self).__init__()

        # initialize sprint burnup series series
        self.serie_names = ['md', 'sp', 'bv', 'planned']
        for serie_name in self.serie_names:
            if serie_name == 'md':
                self[serie_name] = ManDaySerie()
            else:
                self[serie_name] = Serie()
            self[serie_name].name = serie_name


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
        self.timesheet_collection = None  # TimeSheetCollection
        self.story_collection = None  # StoryCollection
        self.serie_collection = None  # SerieCollection

    def get_serie(self, name):
        if self.serie_collection is None:
            return None
        else:
            return self.serie_collection.get(name)

    def get_expected_velocity(self):
        return self.get_serie('sp').get_commited_value() / self.get_serie('md').get_commited_value()

    def get_actual_velocity(self):
        return self.get_serie('sp').get_max_value() / self.get_serie('md').get_max_value()

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
