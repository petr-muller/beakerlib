'''
Created on Jul 31, 2014

@author: Petr Muller
'''
import rpm
from journal import Journal
import os
import time
import socket
import re

class Environment(object):
  def __init__(self):
    pass

class EnvironmentProbe(object):
  TIMEFORMAT="%Y-%m-%d %H:%M:%S %Z"
  def __init__(self):
    self.rpm = rpm.ts()

  def collectEnvironmentVariables(self):
    self.environment.testid = os.environ.get("TESTID", None)
    self.environment.package = os.environ.get("PACKAGE", None)
    self.environment.testRpmVersion = os.environ.get("testversion", None)

  def collectRPMVersion(self, package):
    found = self.rpm.dbMatch("name", package)
    return "%(name)s-%(version)s-%(release)s" % found.next() if found else None

  def collectRPMs(self):
    self.environment.BLVersion = self.collectRPMVersion("beakerlib")
    self.environment.BLRedHatVersion = self.collectRPMVersion("beakerlib-redhat")

  def collectTimestamps(self):
    now = time.strftime(EnvironmentProbe.TIMEFORMAT)
    self.environment.timeStarted = now
    self.environment.timeFinished = now

  def getCPU(self):
    """Helper to read /proc/cpuinfo and grep count and type of CPUs from there"""
    expr = re.compile('^model name[\t ]+: +(.+)$')
    count = 0
    cputype = "unknown"
    try:
      with open('/proc/cpuinfo') as fd:
        for line in fd.readlines():
          match = expr.search(line)
          if match != None:
            count += 1
            cputype = match.groups()[0]
      return "%s x %s" % (count, cputype)
    except:
      return None

  def getRAM(self):
    """Helper to read /proc/meminfo and grep size of RAM from there"""
    size = 'unknown'
    expr = re.compile('^MemTotal: +([0-9]+) +kB$')
    try:
      with open('/proc/meminfo') as fd:
        for line in fd.readlines():
          match = expr.search(line)
          if match != None:
            size = int(match.groups()[0])/1024
            break
      return "%s MB" % size
    except:
      return None

  def getHDD(self):
    """Helper to parse size of disks from `df` output"""
    size = 0.0
    try:
      import subprocess
      output = subprocess.Popen(['df', '-k', '-P', '--local', '--exclude-type=tmpfs'], stdout=subprocess.PIPE).communicate()[0]
      output = output.split('\n')
    except ImportError:
      output = os.popen('df -k -P --local --exclude-type=tmpfs')
      output = output.readlines()
    expr = re.compile('^(/[^ ]+) +([0-9]+) +[0-9]+ +[0-9]+ +[0-9]+% +[^ ]+$')
    for line in output:
      match = expr.search(line)
      if match != None:
        size = size + float(match.groups()[1])/1024/1024
    if size == 0:
      return None
    else:
      return "%.1f GB" % size

  def collectHostInfo(self):
    self.environment.hostname = socket.getfqdn()
    self.environment.arch = os.uname()[-1]
    self.environment.cpu = self.getCPU()
    self.environment.ram = self.getRAM()
    self.environment.hdd = self.getHDD()

    try:
      with open("/etc/redhat-release", "r") as release_file:
        self.environment.release = release_file.read().strip()
    except IOError:
      self.environment.release = None

  def getTestRpmBuilt(self):
    package = os.environ.get("packagename", None)
    if not package:
      return None

    testinfo = self.rpm.dbMatch("name", package)
    if not testinfo:
      return None

    buildtime = time.gmtime(int(testinfo.next().format("%({BUILDTIME}")))
    return time.strftime(EnvironmentProbe.TIMEFORMAT, buildtime)

  def collectMiscellaneous(self):
    self.environment.testRPMBuiltTime = self.getTestRpmBuilt()

  def collect(self):
    self.environment = Environment()

    self.collectTimestamps()
    self.collectEnvironmentVariables()
    self.collectRPMs()
    self.collectHostInfo()
    self.collectMiscellaneous()

    return self.environment

class JournalFactory(object):
    '''
    This class is responsible for creating new journal instances.
    '''

    def createEmptyJournal(self, test):
      probe = EnvironmentProbe()
      return Journal(test, probe.collect())
