import datetime
from collections import OrderedDict

from lst.helpers import MathHelper


class AppContainer(object):
    config = None
    secret = None
    dev_mode = False
    user_args = None
    pass


class Serie(list):
    def __init__(self):
        """
        Base serie. Just a list with some extra attributes for commitment and serie name
        """
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
        """
        Serie for Man Days. Returns all values in MD (rather than hours)
        """
        super(ManDaySerie, self).__init__()

    def get_max_value(self):
        return 0 if len(self) == 0 else self[-1] / 8

    def get_commited_value(self):
        return self.ideal_value / 8

    def get_values_as_percent(self):
        values = MathHelper.get_values_as_percent(self, (0, self.ideal_value))
        return values


class PlannedSerie(Serie):
    def __init__(self):
        """
        Serie for "planned" man days. Doesn't have a commit value, just use the maximum as commit
        """
        super(PlannedSerie, self).__init__()

    def get_commited_value(self):
        return self.get_max_value()


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

        # initialize sprint burnup series
        self.serie_names = ['md', 'sp', 'bv', 'planned']
        for serie_name in self.serie_names:
            if serie_name == 'md':
                self[serie_name] = ManDaySerie()
            elif serie_name == 'planned':
                self[serie_name] = PlannedSerie()
            else:
                self[serie_name] = Serie()
            self[serie_name].name = serie_name


class ResultPerStorySeries(SerieCollection):
    def __init__(self):
        super(ResultPerStorySeries, self).__init__()

        # initialize result per story series
        self.serie_names = ['planned', 'actual']
        for serie_name in self.serie_names:
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
        return self.story_collection.get_commited_story_points() / float(self.commited_man_days)

    def get_actual_velocity(self):
        try:
            return self.get_serie('sp').get_max_value() / self.get_serie('md').get_max_value()
        except ZeroDivisionError:
            return 0

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

    def get_title(self):
        return self.jira_data.get('sprint_name').replace('+', ' ') + ' (' + self.name + ')'
