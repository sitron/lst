class Story:
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
        self.project_id = None
        self.project_name = None
        self.sprint_name = None

    def is_over(self):
        return self.status in Story.closed_status_ids

    def get_close_day(self):
        return self.close_date.strftime('%Y-%m-%d')


class StoryCollection(list):
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

    def get_commited(self, value_name):
        """
        Alias to get_commited_story_points and get_commited_business_value
        :param value_name: sp or bv
        """
        if value_name == 'bv':
            return self.get_commited_business_value()
        else:
            return self.get_commited_story_points()

    def get_commited_story_points(self):
        total = 0
        for s in self:
            if s.is_nice:
                continue
            total += s.story_points
        return total

    def get_achieved_story_points(self):
        for s in self:
            if s.is_over():
                self.achieved_story_points += s.story_points
        return self.achieved_story_points

    def get_commited_business_value(self):
        total = 0
        for s in self:
            if s.is_nice:
                continue
            total += s.business_value
        return total

    def get_achieved_business_value(self):
        for s in self:
            if s.is_over():
                self.achieved_business_value += s.business_value
        return self.achieved_business_value
