'''
Created on Jul 31, 2014

@author: Petr Muller
'''

class JournalException(Exception):
  pass

def getJournalFilename():
  return "journal.xml"