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
from bl_journal import command

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

def initialize(test):
  '''Process an 'initialize' command'''
  if test is None:
    raise CLIError("Command 'init' needs a --test option")
  to_execute = getCommand("init")
  to_execute(os.environ["BEAKERLIB_DIR"])

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

  try:
    # Setup argument parser
    parser = ArgumentParser(description=program_license,
                            formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=command.getSupportedCommands(),
                        help="Initialize the bl_journal if it does not exist")
    parser.add_argument("--test", dest="test",
                        help="A test name related to this bl_journal action")
    # Process arguments
    args = parser.parse_args()
    if args.command == "init":
      initialize(args.test)
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
