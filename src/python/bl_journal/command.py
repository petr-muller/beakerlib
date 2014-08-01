'''
Created on Jul 31, 2014

@author: Petr Muller
'''
import bl_journal.util as util
import os
from bl_journal.writer import writeJournal
from bl_journal.factory import createEmptyJournal


class JournalCommandException(util.JournalException):
  """Exception thrown whenever any Journal command fails"""
  pass


def executeInitialization(directory):
  """Initialize the Journal.

     Parameter directory needs to exist and be writable.
     If journal file already exists, no action is executed (the original journal is not overwritten)."""
  if not os.path.isdir(directory):
    raise JournalCommandException("Not a directory: '%s'" % directory)

  journal_file = os.path.join(directory, util.getJournalFilename())
  if not os.path.exists(journal_file):
    writeJournal(journal_file, createEmptyJournal())

COMMANDS = {"init" : executeInitialization}

def getSupportedCommands():
  """Returns a list of supported commands"""
  return COMMANDS.keys()

def getCommand(command):
  """Returns a command object for passed command string"""
  return COMMANDS[command]
