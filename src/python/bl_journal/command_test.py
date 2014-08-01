'''
Created on Aug 1, 2014

@author: Petr Muller
'''
from bl_journal.command import getSupportedCommands

def test_getSupportedCommands():
  """Test proper function of getSupportedCommands"""
  commands = getSupportedCommands()
  assert "init" in commands
