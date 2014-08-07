'''
Created on Jul 31, 2014

@author: Petr Muller
'''

class Journal(object):
  """An object representing the journal"""
  # pylint: disable=too-few-public-methods

  def __init__(self, test, environment):
    self.environment = environment
    self.test = test
