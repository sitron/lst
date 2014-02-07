from lst.commands import BaseCommand
from lst.errors import IOError


class RetrieveUserIdCommand(BaseCommand):
    """
    Usage: get-user-id [last_name] Retrieves the Zebra user id from his/her last name
    """

    def add_command_arguments(self, subparsers):
        parser = subparsers.add_parser('get-user-id')
        parser.add_argument("lastname", nargs='+', help="user(s) lastname")
        return parser

    def run(self, args):
        names = [x.lower() for x in args.lastname]

        zebra_manager = self.get_zebra_manager()
        all_users = zebra_manager.get_all_users()
        if len(all_users) == 0:
            raise IOError(
                "No user found at all! (check that you are connected to internet)"
            )

        users = []
        for user in all_users:
            if user.last_name.lower() in names:
                users.append(user)

        self._output(users, names)

    def _output(self, users, names):
        if len(users) == 0:
            print 'No user found with lastname {}'.format(', '.join(names))
            return

        for user in users:
            print 'found {} ({}) with id {}'.format(
                user.last_name,
                user.first_name,
                user.id,
            )
