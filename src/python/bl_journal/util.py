'''
Created on Jul 31, 2014

@author: Petr Muller
'''

class JournalException(Exception):
  """General exception for everything related to the Journal"""
  pass

def getJournalFilename():
  """Returns a name of the bl_journal file, to be placed into BEAKERLIB_DIR"""
  return "bl_journal.xml"
