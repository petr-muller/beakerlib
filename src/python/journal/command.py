'''
Created on Jul 31, 2014

@author: Petr Muller
'''
import util
import os
from writer import JournalWriter
from factory import JournalFactory


class JournalCommandException(util.JournalException):
  pass

class CommandInitialize(object):
  def __init__(self):
    pass

  def execute(self, directory, test):
    if not os.path.isdir(directory):
      raise JournalCommandException("Not an existing directory: '%s'" % directory)

    journalFile = os.path.join(directory, util.getJournalFilename())
    if not os.path.exists(journalFile):
      writer = JournalWriter(journalFile)
      factory = JournalFactory()
      writer.writeJournal(factory.createEmptyJournal(test))

COMMANDS = { "init" : CommandInitialize() }

def getSupportedCommands():
  return COMMANDS.keys()

def getCommand(command):
  return COMMANDS[command]