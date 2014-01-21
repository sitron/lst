import distutils
import sys

from lst.commands import BaseCommand


class TestInstallCommand(BaseCommand):
    """
    Usage:  test-install

    """
    def add_command_arguments(self, subparsers):
        parser = subparsers.add_parser('test-install')
        return parser

    def run(self, args):
        print 'Will dump some useful variable to debug'
        print 'My sys.prefix is {}'.format(sys.prefix)
        print 'My modules are installed in {}'.format(distutils.sysconfig.get_python_lib())
