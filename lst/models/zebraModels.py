import collections


class TimeSheet:
    def __init__(self):
        self.username = None
        self.time = 0
        self.date = None
        self.project = None
        self.id = 0
        self.description = None

    def readable_date(self):
        return self.date.strftime('%Y-%m-%d')


class TimeSheetCollection(list):
    def group_by_day(self):
        """
        Group zebra timesheets by date
        :rtype : collections.OrderedDict
        :return: orderedDict of ZebraDay(s)
        """
        zebra_days = collections.OrderedDict()

        for timesheet in self:
            readable_date = timesheet.readable_date()

            zebra_day = zebra_days.get(readable_date, ZebraDay())
            zebra_day.add_entry(timesheet)
            zebra_days[readable_date] = zebra_day

        return zebra_days

    def group_by_project(self):
        """
        Group zebra timesheets by project id
        :rtype : dict
        :return: dictionary of projects (key=project name, values=list of timesheets)
        """
        projects = {}

        for timesheet in self:
            if timesheet.project not in projects:
                projects[timesheet.project] = []

            projects[timesheet.project].append(timesheet)

        return projects


class ZebraDay:
    def __init__(self):
        self.time = 0
        self.entries = list()  # list of timesheets
        self.day = ''  # readable day (2012-07-31)
        self.entries_per_user = None

    def add_entry(self, entry):
        self.entries.append(entry)
        self.time += entry.time
        self.day = entry.readable_date()

    def get_entries_per_user(self):
        if self.entries_per_user is None:
            self.entries_per_user = {}
            for entry in self.entries:
                try:
                    self.entries_per_user[entry.username] += entry.time
                except KeyError:
                    self.entries_per_user[entry.username] = entry.time
        return self.entries_per_user
