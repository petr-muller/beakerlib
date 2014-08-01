'''
Created on Jul 31, 2014

@author: Petr Muller
'''

import xml.etree.cElementTree as ET

class TAGS:
  class HEADER:
    TESTID="test_id"

class JournalWriter(object):
    '''
    This class handles writing new records (or whole journals) to an XML file.
    '''

    def __init__(self, journalFile):
      self.file = journalFile

    def buildHeader(self, root, environment):
      elTestId = ET.SubElement(root, TAGS.HEADER.TESTID)
      elTestId.text = environment.testid if environment.testid else "unset"

    def writeJournal(self, journal):
      root = ET.Element("BEAKER_TEST")
      self.buildHeader(root, journal.environment)
      ET.ElementTree(root).write(self.file, "UTF-8")