'''
Created on Jul 31, 2014

@author: Petr Muller
'''

try:
  import rpm
except ImportError:
  # RPMs not supported
  # pylint: disable=invalid-name
  rpm = None

from bl_journal.journal import Journal
import os
import time
import socket
import re

class RECORDS(object):
  # pylint: disable=too-few-public-methods
  """Enum listing keys for storing records in an environment"""
  TESTID = "testid"
  PACKAGE = "package"
  TEST_RPM_VERSION = "test_rpm_version"
  BL_VERSION = "bl_version"
  BLRH_VERSION = "blrh_version"
  TIME_START = "time_start"
  TIME_END = "time_end"
  HOSTNAME = "hostname"
  ARCH = "arch"
  CPU = "cpu"
  RAM = "ram"
  HDD = "hdd"
  RELEASE = "release"
  TEST_BUILT = "test_rpm_built"

def getCPU():
  """Helper to extract CPU count and type from /proc/cpuinfo"""
  expr = re.compile('^model name[\t ]+: +(.+)$')
  count = 0
  cputype = "unknown"
  try:
    with open('/proc/cpuinfo') as cpuinfo_file:
      for line in cpuinfo_file.readlines():
        match = expr.search(line)
        if match != None:
          count += 1
          cputype = match.groups()[0]
    return "%s x %s" % (count, cputype)
  except IOError:
    return None

def getRAM():
  """Helper to extract RAM size from /proc/meminfo"""
  size = 'unknown'
  expr = re.compile('^MemTotal: +([0-9]+) +kB$')
  try:
    with open('/proc/meminfo') as meminfo_file:
      for line in meminfo_file.readlines():
        match = expr.search(line)
        if match != None:
          size = int(match.groups()[0])/1024
          break
    return "%s MB" % size
  except IOError:
    return None

def getHDD():
  """Helper to parse size of disks from `df` output"""
  size = 0.0
  cmd = ['df', '-k', '-P', '--local', '--exclude-type=tmpfs']
  try:
    import subprocess
    output = subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()[0]
    output = output.split('\n')
  except ImportError:
    output = os.popen("".join(cmd))
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

class EnvironmentProbe(object):
  """A class responsible for extracting information about test run environment from the system"""

  TIMEFORMAT = "%Y-%m-%d %H:%M:%S %Z"

  # Environmental variables
  EV_TESTID = "TESTID"
  EV_PACKAGE = "PACKAGE"
  EV_TEST_VERSION = "testversion"
  EV_PACKAGE_NAME = "packagename"

  def __init__(self):
    self.rpm = rpm if rpm else None
    self.environment = None

  def collectEnvironmentVariables(self):
    """Collect interesting environment variable values"""
    self.environment[RECORDS.TESTID] = os.environ.get(EnvironmentProbe.EV_TESTID, None)
    self.environment[RECORDS.PACKAGE] = os.environ.get(EnvironmentProbe.EV_PACKAGE, None)
    self.environment[RECORDS.TEST_RPM_VERSION] = os.environ.get(EnvironmentProbe.EV_TEST_VERSION, None)

  def collectRPMVersion(self, package):
    """Determines a N-V-R for installed packages. Returns None if package is not installed"""
    # pylint: disable=no-member
    found = self.rpm.dbMatch("name", package) if self.rpm else None
    return "%(name)s-%(version)s-%(release)s" % found.next() if found else None

  def collectRPMs(self):
    """Collect versions of RPMs relevant to the test run"""
    self.environment[RECORDS.BL_VERSION] = self.collectRPMVersion("beakerlib")
    self.environment[RECORDS.BLRH_VERSION] = self.collectRPMVersion("beakerlib-redhat")

  def collectTimestamps(self):
    """Collect start and end times of the test runs"""
    now = time.strftime(EnvironmentProbe.TIMEFORMAT)
    self.environment[RECORDS.TIME_START] = now
    self.environment[RECORDS.TIME_END] = now

  def collectHostInfo(self):
    """Collect information about a test run host"""
    self.environment[RECORDS.HOSTNAME] = socket.getfqdn()
    self.environment[RECORDS.ARCH] = os.uname()[-1]
    self.environment[RECORDS.CPU] = getCPU()
    self.environment[RECORDS.RAM] = getRAM()
    self.environment[RECORDS.HDD] = getHDD()

    try:
      with open("/etc/redhat-release", "r") as release_file:
        self.environment[RECORDS.RELEASE] = release_file.read().strip()
    except IOError:
      self.environment[RECORDS.RELEASE] = None

  def getTestRpmBuilt(self):
    """Determines date/time when a test RPM was built. The test RPM name is passed to the test in 'packagename'
       environmental variable"""
    package = os.environ.get(EnvironmentProbe.EV_PACKAGE_NAME, None)
    if not package:
      return None

    # pylint: disable=no-member
    testinfo = self.rpm.dbMatch("name", package) if self.rpm else None
    if not testinfo:
      return None

    buildtime = time.gmtime(int(testinfo.next().format("%({BUILDTIME}")))
    return time.strftime(EnvironmentProbe.TIMEFORMAT, buildtime)

  def collectMiscellaneous(self):
    """Collect miscellaneous additional info about test run environment"""
    self.environment[RECORDS.TEST_BUILT] = self.getTestRpmBuilt()

  def collect(self):
    """Collects information about test run environment"""
    self.environment = {}

    self.collectTimestamps()
    self.collectEnvironmentVariables()
    self.collectRPMs()
    self.collectHostInfo()
    self.collectMiscellaneous()

    return self.environment

def createEmptyJournal():
  """Creates a new empty journal, with environment collected from the host"""
  probe = EnvironmentProbe()
  return Journal(probe.collect())
