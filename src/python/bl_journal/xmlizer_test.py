'''
Created on Aug 6, 2014

@author: Petr Muller
'''
import os
import tempfile

from bl_journal.factory import createEmptyJournal, EnvironmentProbe
from bl_journal.xmlizer import writeJournal, TAGS, readJournalAsXML


def test_writeAndReadAsXML():
  """Tests the basic read-and-write behavior of the xmlizer"""
  os.environ[EnvironmentProbe.EV_TESTID] = "test_writeAndReadAsXML_id"
  journal = createEmptyJournal("/the/test")
  journal_file = tempfile.mkstemp()[1]
  writeJournal(journal_file, journal)
  read_journal = readJournalAsXML(journal_file)
  assert read_journal.find(TAGS.HEADER.TESTID).text == "test_writeAndReadAsXML_id"
  os.unlink(journal_file)
