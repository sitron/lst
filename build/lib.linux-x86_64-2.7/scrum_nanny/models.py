class ZebraEntries(dict):
    def __init__(self):
        self.ordered_dates = None

    def get_ordered_dates(self):
        if self.ordered_dates is None:
            self.ordered_dates = sorted(set(self.keys()))
        return self.ordered_dates

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

    def get_total_story_points(self):
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

    def get_total_business_value(self):
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

