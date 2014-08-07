'''
Created on Jul 31, 2014

@author: Petr Muller
'''
import bl_journal.util as util
import os
from bl_journal.xmlizer import writeJournal
from bl_journal.factory import createEmptyJournal


class JournalCommandException(util.JournalException):
  """Exception thrown whenever any Journal command fails"""
  pass


def executeInitialization(test, directory):
  """Initialize the Journal.

     Parameter directory needs to exist and be writable.
     If journal file already exists, no action is executed (the original journal is not overwritten)."""
  if not os.path.isdir(directory):
    raise JournalCommandException("Not a directory: '%s'" % directory)

  journal_file = os.path.join(directory, util.getJournalFilename())
  if not os.path.exists(journal_file):
    writeJournal(journal_file, createEmptyJournal(test))

def executeDump(xml_type):
  """Dump the journal XML"""
  xml_type = xml_type

def insertLog(message, severity):
  """Adds a new log record to the journal"""
  message = message
  severity = severity

def insertTest():
  """Adds a new test record to the journal"""
  pass

def addPhase():
  """Adds a new phase to the journal"""
  pass

def finishPhase():
  """Finish and evaluate currently open phase"""
  pass

def printLog():
  """Prints a textual log representation"""
  pass

COMMANDS = {"init" : executeInitialization,
            "dump" : executeDump,
            "log" : insertLog,
            "test" : insertTest,
            "addphase" : addPhase,
            "finphase" : finishPhase,
            "printlog" : printLog}

def getSupportedCommands():
  """Returns a list of supported commands"""
  return COMMANDS.keys()

def getCommand(command):
  """Returns a command object for passed command string"""
  try:
    return COMMANDS[command]
  except KeyError:
    raise JournalCommandException("No such command: '%s'" % command)
