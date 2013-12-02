from lst.commands import BaseCommand
from lst.helpers import InputHelper, ArgParseHelper, ZebraHelper


class CheckHoursCommand(BaseCommand):
    """
    Command to retrieve all Zebra hours for a specific date and/or user_id, and group them by project
    Usage:  check-hours [-d date] [-u user_id]
            check-hours [-d date] [-u user1_id user2_id]
            check-hours [-u user_id]
            check-hours [-d date]

    """
    def add_command_arguments(self, subparsers):
        parser = subparsers.add_parser('check-hours')
        parser.add_argument(
            "-d", "--date", nargs='*', help="format: -d dd.mm.yyyy. specify either one or two dates (-d start end)"
        )
        ArgParseHelper.add_user_argument(parser)
        return parser

    def run(self, args):
        # parse and verify user arguments
        users = InputHelper.sanitize_users(args.user)
        dates = InputHelper.sanitize_dates(args.date)
        InputHelper.ensure_max_2_dates(dates)

        # print output to console
        self._output(self._get_projects(dates, users), users)

    def _get_projects(self, dates, users):
        start_date, end_date = self.get_start_and_end_date(dates)

        # retrieve zebra data
        zebra_manager = self.get_zebra_manager()
        zebra_entries = zebra_manager.get_all_timesheets(
            start_date=start_date,
            end_date=end_date,
            users=users
        )

        if len(zebra_entries) == 0:
            return

        return self._sort_groups_alphabetically(
            zebra_entries.group_by_project()
        )

    def _sort_groups_alphabetically(self, projects):
        """sort grouped entries alphabetically"""
        return sorted(projects.items(), key=lambda kv: kv[0])

    def _output(self, projects, users=None):
        # formated output
        print ''
        print 'Projects:'
        found_users = []
        zebra_url = self.secret.get_zebra('url')
        for name, entries in projects:
            print '- %s' % name

            total = 0
            template = "  {time:<12} {username:<23} {description:<45} ({url:<15})"
            for entry in entries:
                d = dict()
                d['time'] = str(entry.time) + ' hours'
                d['username'] = entry.username
                if entry.username not in found_users:
                    found_users.append(entry.username)
                d['description'] = entry.description[:44]
                d['url'] = ZebraHelper.get_activity_url(zebra_url, entry.id)
                print template.format(**d)
                total += entry.time

            print '  Total: %s' % (total)
            print ''

        if users is not None:
            if len(users) == len(found_users):
                print '(found entries for all users)'
            else:
                print 'Found entries for %d out of %d users (%s)' % \
                      (len(found_users), len(users), ','.join(found_users))
