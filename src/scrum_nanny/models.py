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
    def __init__(self):
        self.story_points = 0
        self.business_value = 0
        self.id = None
        self.status = None
        self.close_date = None
        self.is_nice = False

    def is_over(self):
        # 6: PO review, 10008: closed
        return self.status == 6 or self.status == 10008

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
    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def set_sprint(self, sprint):
        self.sprint = sprint

    def get_sprint(self):
        return self.sprint

class Sprint:
    commited_man_days = 0

    def get_index(self):
        return self.index

    def set_index(self, index):
        self.index = index

    def set_jira_data(self, data):
        self.jira_data = data

    def get_jira_data(self, key):
        return self.jira_data[key]

    def set_zebra_data(self, data):
        self.zebra_data = data

    def get_zebra_data(self, key):
        return self.zebra_data[key]

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
