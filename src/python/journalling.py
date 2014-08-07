#!/usr/bin/python
# encoding: utf-8
'''
journalling -- A CLI interface to BeakerLib Journal

This is a simple CLI interface to create a BeakerLib bl_journal.
To be used mainly in BeakerLib tests.eclipse

@author:     Petr Muller

@copyright:  2014 Red Hat. All rights reserved.

@license:    GPLv3

@contact:    muller@redhat.com
@deffield    updated: Updated
'''

import sys
import os

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from bl_journal.command import getCommand
import traceback

__all__ = []
__version__ = 0.1
__date__ = '2014-07-31'
__updated__ = '2014-07-31'

DEBUG = 1
TESTRUN = 0
PROFILE = 0

class CLIError(Exception):
  '''Generic exception to raise and log different fatal errors.'''
  def __init__(self, msg):
    super(CLIError).__init__(type(self))
    self.msg = "E: %s" % msg
  def __str__(self):
    return self.msg
  def __unicode__(self):
    return self.msg

def initialize(args):
  '''Process an 'initialize' command'''
  to_execute = getCommand("init")
  to_execute(args.test, os.environ["BEAKERLIB_DIR"])

def dump(args):
  """Process a 'dump' command"""
  to_execute = getCommand("dump")
  to_execute(args.type)

def log(args):
  """Process a log command"""
  to_execute = getCommand("log")
  to_execute(args.message, args.severity)

def add_phase(args):
  """Process a command to add a phase"""
  to_execute = getCommand("addphase")
  args = args
  to_execute()

def finish_phase(args):
  """Process a command to finish a phase"""
  to_execute = getCommand("finphase")
  args = args
  to_execute()

def print_log(args):
  """Process a command to add new log to a journal"""
  to_execute = getCommand("printlog")
  args = args
  to_execute()

def add_test(args):
  """Process a command to add new test record to a journal"""
  to_execute = getCommand("test")
  args = args
  to_execute()

def add_init_command(subparsers):
  """Create a parser of a 'init' subcommand"""
  init_parser = subparsers.add_parser("init")
  init_parser.add_argument("--test", dest="test", help="A test for which the journal is initialized")
  init_parser.set_defaults(func=initialize)

def add_log_command(subparsers):
  """Create a parser of a 'log' subcommand"""
  log_parser = subparsers.add_parser("log")
  log_parser.add_argument("--message", dest="message", help="Message to log")
  log_parser.add_argument("--severity", dest="severity", choices=("WARNING", "LOG", "DEBUG", "INFO"),
                          help="Severity of the message")
  log_parser.set_defaults(func=log)

def add_dump_command(subparsers):
  """Create a parser for a 'dump' subcommand"""
  dump_parser = subparsers.add_parser("dump")
  dump_parser.add_argument("--type", default="raw", dest="type", choices=("pretty", "raw"),
                           help="Sets how the XML is emitted")
  dump_parser.set_defaults(func=dump)

def add_addphase_command(subparsers):
  """Create a parser for a 'addphase' subcommand"""
  addphase_parser = subparsers.add_parser("addphase")
  addphase_parser.add_argument("--name", required=True, dest="name",
                               help="A title of the phase")
  addphase_parser.add_argument("--type", required=True, dest="type", choices=("FAIL", "WARN"),
                               help="A result this phase should give if any enclosed assertion fails")
  addphase_parser.set_defaults(func=add_phase)

def add_finphase_command(subparsers):
  """Create a parser for a 'finphase' subcommand"""
  finphase_parser = subparsers.add_parser("finphase")
  finphase_parser.set_defaults(func=finish_phase)

def add_printlog_command(subparsers):
  """Create a parser for a 'printlog' subcommand"""
  printlog_parser = subparsers.add_parser("printlog")
  printlog_parser.add_argument("--severity", dest="severity", choices=("INFO", "DEBUG", "WARNING", "ERROR", "FATAL"),
                               help="A threshold severity for messages. Messages with lower severity won't be printed.")
  printlog_parser.set_defaults(func=print_log)

def add_test_command(subparsers):
  """Create a parser for a 'test' subcommand"""
  test_parser = subparsers.add_parser("test")
  test_parser.add_argument("--message", required=True, dest="message",
                           help="A message to accompany the test")
  test_parser.add_argument("--result", required=True, dest="result", choices=("PASS", "FAIL"),
                           help="A result of the assertion")
  test_parser.set_defaults(func=add_test)

def main(argv=None):  # IGNORE:C0111
  '''Command line options.'''
  if argv is None:
    argv = sys.argv
  else:
    sys.argv.extend(argv)

  program_name = os.path.basename(sys.argv[0])
  program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
  program_license = '''%s

  Created by Petr Muller on %s.
  Copyright 2014 Red Hat Inc.. All rights reserved.

  Licensed under the GPLv3.
USAGE
''' % (program_shortdesc, str(__date__))

  # pylint: disable=broad-except
  try:
    # Setup argument parser
    parser = ArgumentParser(description=program_license,
                            formatter_class=RawDescriptionHelpFormatter)
    subparsers = parser.add_subparsers()
    add_init_command(subparsers)
    add_log_command(subparsers)
    add_dump_command(subparsers)
    add_finphase_command(subparsers)
    add_addphase_command(subparsers)
    add_printlog_command(subparsers)
    add_test_command(subparsers)

    # Process arguments
    args = parser.parse_args()
    args.func(args)
    return 0
  except KeyboardInterrupt:
    ### handle keyboard interrupt ###
    return 0
  except Exception, caught_exception:
    if DEBUG or TESTRUN:
      traceback.print_exc()
      raise caught_exception
    indent = len(program_name) * " "
    sys.stderr.write(program_name + ": " + repr(caught_exception) + "\n")
    sys.stderr.write(indent + "  for help use --help")
    return 2

if __name__ == "__main__":
  if DEBUG:
    pass
  if TESTRUN:
    import doctest
    doctest.testmod()
  if PROFILE:
    import cProfile
    import pstats
    PROFILE_FILENAME = 'journalling_profile.txt'
    cProfile.run('main()', PROFILE_FILENAME)
    STATSFILE = open("profile_stats.txt", "wb")
    P = pstats.Stats(PROFILE_FILENAME, stream=STATSFILE)
    STATS = P.strip_dirs().sort_stats('cumulative')
    STATS.print_stats()
    STATSFILE.close()
    sys.exit(0)
  sys.exit(main())
