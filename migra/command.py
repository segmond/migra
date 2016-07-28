from __future__ import unicode_literals, print_function

from sqlbag import S
import argparse
import sys

from .migra import Migration
from .statements import UnsafeMigrationException


def parse_args(args):
    parser = argparse.ArgumentParser(
        description='Generate a database migration.')

    parser.add_argument(
        '--unsafe',
        dest='unsafe',
        action='store_true',
        help='Prevent migra from erroring upon generation of drop statements.')

    parser.add_argument(
        'dburl_from',
        help='The database you want to migrate.')

    parser.add_argument(
        'dburl_target',
        help='The database you want to use as the target.')

    return parser.parse_args(args)


def run(args, out=None, err=None):
    if not out:
        out = sys.stdout  # pragma: no cover

    if not err:
        err = sys.stderr  # pragma: no cover

    with S(args.dburl_from) as s0, S(args.dburl_target) as s1:
        m = Migration(s0, s1)

        if args.unsafe:
            m.set_safety(False)
        m.add_all_changes()

        try:
            print(m.sql, file=out)
        except UnsafeMigrationException:
            print('-- ERROR: destructive statements generated. Use the --unsafe flag to suppress this error.', file=err)
            return 3

        if not m.statements:
            return 0
        else:
            return 2


def do_command():  # pragma: no cover
    args = parse_args(sys.argv[1:])
    status = run(args)
    sys.exit(status)
