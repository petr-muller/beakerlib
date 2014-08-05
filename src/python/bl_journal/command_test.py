'''
Created on Aug 1, 2014

@author: Petr Muller
'''
from bl_journal.command import getSupportedCommands, getCommand

def test_getSupportedCommands():
  """Test proper function of getSupportedCommands"""
  commands = getSupportedCommands()
  assert "init" in commands

def test_getCommand():
  """Test that getCommand returns sensible results for existing command"""
  init = getCommand("init")
  assert init is not None

  try:
    nonexistent = getCommand("a-command-which-does-not-exist")
    assert nonexistent is not nonexistent
  except KeyError:
    assert True
