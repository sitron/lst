class AppContainer(object):
    config = None
    secret = None
    pass

class ZebraEntry:
    def __init__(self):
        self.username = None
        self.time = 0

class ZebraDays(dict):
    def __init__(self):
        self.ordered_dates = None

    def get_ordered_dates(self):
        if self.ordered_dates is None:
            self.ordered_dates = sorted(set(self.keys()))
        return self.ordered_dates

class ZebraDay:
    time = 0
    entries = list()
    day = '' # readable day (2012-07-31)

class JiraEntry:
    # status codes considered as closed
    closed_status = set()

    def __init__(self):
        self.story_points = 0
        self.business_value = 0
        self.id = None
        self.status = None
        self.close_date = None
        self.is_nice = False

    def is_over(self):
        return self.status in JiraEntry.closed_status

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

class Project:
    def __init__(self):
        self.name = ''
        self.sprints = dict()
        self.raw = None

    def get_sprint(self, index, use_unique = False):
        sprint = self.sprints.get(index)
        if sprint is not None:
            return sprint
        if use_unique == True and self.nb_sprints() == 1:
            return self.get_first_sprint()
        else:
            return None

    def get_first_sprint(self):
        items = self.sprints.values()
        return items[0]

    def has_sprints(self):
        return len(self.sprints) > 0

    def nb_sprints(self):
        return len(self.sprints)

class Sprint:
    def __init__(self):
        self.forced = dict()
        self.commited_man_days = 0
        self.index = 0
        self.jira_data = None
        self.zebra_data = None
        self.raw = None
        self.default_closed_status_id = 6
        self.default_closed_status_name = 'closed'

    def get_closed_status_codes(self):
        codes = self.get_jira_data('closed_status_codes')
        return [self.default_closed_status_id] if codes is None else codes

    def get_closed_status_name(self):
        name = self.get_jira_data('closed_status')
        return self.default_closed_status_name if name is None else name

    def get_forced_data(self, date, default):
        forced = self.forced.get(date, default)
        if type(forced) == str:
            return default + float(forced)
        return forced

    def get_zebra_data(self, key):
        return self.zebra_data.get(key)

    def get_jira_data(self, key):
        return self.jira_data.get(key)

class GraphEntries(dict):
    ''' keeps all the graph entries '''
    def get_ordered_data(self):
        data = list()
        cumulated_bv = 0
        cumulated_sp = 0
        cumulated_time = 0
        for key in sorted(self.iterkeys()):
            value = self[key]
            value.date = key
            cumulated_bv += value.business_value
            cumulated_sp += value.story_points
            cumulated_time += value.time
            value.business_value = cumulated_bv
            value.story_points = cumulated_sp
            value.time = cumulated_time / 8
            data.append(value.to_json())
        return data

class GraphEntry:
    date = None
    business_value = 0
    story_points = 0
    time = 0

    def to_json(self):
        return {'date': self.date, 'businessValue': self.business_value, 'storyPoints': self.story_points, 'manDays': self.time}
