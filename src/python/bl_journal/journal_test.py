'''
Created on Aug 6, 2014

@author: Petr Muller
'''
from bl_journal.journal import Journal

def test_journalBasics():
  """Tests the basic functionality of a journal"""
  journal = Journal("/a/test", None)
  assert journal is not None
  assert journal.test == "/a/test"

