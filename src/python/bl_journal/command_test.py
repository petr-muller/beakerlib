'''
Created on Aug 1, 2014

@author: Petr Muller
'''
import os
import tempfile

from nose.tools import raises

from bl_journal.command import getSupportedCommands, getCommand, JournalCommandException, executeInitialization
from bl_journal.util import getJournalFilename
import shutil


def test_getSupportedCommands():
  """Test proper function of getSupportedCommands"""
  commands = getSupportedCommands()
  assert "init" in commands
  assert "dump" in commands
  assert "log" in commands
  assert "test" in commands
  assert "addphase" in commands
  assert "finphase" in commands
  assert "printlog" in commands

def test_getCommand():
  """Test that getCommand returns sensible results for existing command"""
  assert getCommand("init") is not None
  assert getCommand("dump") is not None
  assert getCommand("log") is not None
  assert getCommand("test") is not None
  assert getCommand("addphase") is not None
  assert getCommand("finphase") is not None
  assert getCommand("printlog") is not None

@raises(JournalCommandException)
def test_getCommandNonExistent():
  """Test JournalCommandException is raised when asked for nonexistent command"""
  getCommand("a-command-which-does-not-exist")

@raises(JournalCommandException)
def test_executeInitializationNoDir():
  """Tests that JournalCommandException is raised when journal is supposed to initialize in nonexistend directory"""
  executeInitialization("/some/test/name", "/nosuchdirectory")

def test_executeInitialization():
  """Tests that journal is created in provided directory"""
  test_dir = tempfile.mkdtemp()
  executeInitialization("/some/test/name/", test_dir)
  assert os.path.exists(os.path.join(test_dir, getJournalFilename()))
  shutil.rmtree(test_dir)

def test_executeInitNoOverwrite():
  """Tests that journal is not overwritten if it exists"""
  test_dir = tempfile.mkdtemp()
  journal_path = os.path.join(test_dir, getJournalFilename())
  with open(journal_path, "w") as journal_file:
    journal_file.write("whatever\n")
  executeInitialization("/some/test/name", test_dir)
  with open(journal_path, "r") as journal_file:
    assert journal_file.readline().strip() == "whatever"
  shutil.rmtree(test_dir)
