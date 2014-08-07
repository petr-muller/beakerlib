'''
Created on Jul 31, 2014

@author: Petr Muller
'''

import xml.etree.cElementTree as ET
from bl_journal.factory import RECORDS

class TAGS(object):
  # pylint: disable=too-few-public-methods
  """XML tags for Journal"""
  class HEADER(object):
    """XML tags for Journal header"""
    TESTID = "test_id"

def buildHeader(root, environment):
  """Create XML elements for journal header, extracting values from a given
     environment and puts them into a given root element"""
  el_test_id = ET.SubElement(root, TAGS.HEADER.TESTID)
  el_test_id.text = environment[RECORDS.TESTID] if environment[RECORDS.TESTID] else "unset"

def writeJournal(journal_file, journal):
  """Writes a XML representation of a journal into a file"""
  root = ET.Element("BEAKER_TEST")
  buildHeader(root, journal.environment)
  ET.ElementTree(root).write(journal_file, "UTF-8")

def readJournalAsXML(journal_file):
  """Read a BeakerLib journal and return it as ElementTree XML tree"""
  journal = ET.parse(journal_file)
  return journal
