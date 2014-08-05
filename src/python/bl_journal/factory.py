'''
Created on Jul 31, 2014

@author: Petr Muller
'''

from bl_journal.journal import Journal
import os
import time
import socket
import re
from bl_journal.util import JournalException

class EnvironmentProbeError(JournalException):
  """Error thrown whenever an environment probe fails to retrieved necessary information"""
  pass

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

def extractCpuInfo(lines):
  """Extract information from /proc/cpuinfo file"""
  expr = re.compile('^model name[\t ]+: +(.+)$')
  count = 0
  cputype = "unknown"

  for line in lines:
    match = expr.search(line)
    if match:
      count += 1
      cputype = match.groups()[0]
  return "%s x %s" % (count, cputype)

def extractMemInfo(lines):
  """Extract information from /proc/meminfo file"""
  size = 'unknown'
  expr = re.compile('^MemTotal: +([0-9]+) +kB$')
  for line in lines:
    match = expr.search(line)
    if match:
      size = int(match.groups()[0])/1024
      break
  return "%s MB" % size

def extractHddInfo(lines):
  """Extract information from df command"""
  size = 0.0
  expr = re.compile('^(/[^ ]+) +([0-9]+) +[0-9]+ +[0-9]+ +[0-9]+% +[^ ]+$')
  for line in lines:
    match = expr.search(line)
    if match:
      size = size + float(match.groups()[1])/1024/1024
  return ("%.1f GB" % size) if size else None

class EnvironmentProbe(object):
  """A class responsible for extracting information about test run environment from the system"""

  TIMEFORMAT = "%Y-%m-%d %H:%M:%S %Z"

  # Environmental variables
  EV_TESTID = "TESTID"
  EV_PACKAGE = "PACKAGE"
  EV_TEST_VERSION = "testversion"
  EV_PACKAGE_NAME = "packagename"
  DEFAULT_CPUINFO = "/proc/cpuinfo"
  DEFAULT_MEMINFO = "/proc/meminfo"
  DEFAULT_DF = ('df', '-k', '-P', '--local', '--exclude-type=tmpfs')

  def __init__(self, rpm=None, fqdn=socket.getfqdn, cpuinfo=DEFAULT_CPUINFO, meminfo=DEFAULT_MEMINFO, df=DEFAULT_DF):
    self.rpm = rpm.ts() if rpm else None
    self.getfqdn = fqdn
    self.cpuinfo = cpuinfo
    self.meminfo = meminfo
    self.df_command = df
    self.environment = {}

  def getCPU(self):
    """Helper to extract CPU count and type from /proc/cpuinfo"""
    try:
      with open(self.cpuinfo) as cpuinfo_file:
        return extractCpuInfo(cpuinfo_file.readlines())
    except IOError:
      return None

  def getRAM(self):
    """Helper to extract RAM size from /proc/meminfo"""
    try:
      with open(self.meminfo) as meminfo_file:
        return extractMemInfo(meminfo_file.readlines())
    except IOError:
      return None

  def getHDD(self):
    """Helper to parse size of disks from `df` output"""
    try:
      try:
        import subprocess
        output = subprocess.Popen(self.df_command, stdout=subprocess.PIPE).communicate()[0]
        output = output.split('\n')
      except ImportError:
        output = os.popen("".join(self.df_command))
        output = output.readlines()
    except OSError:
      return None

    return extractHddInfo(output)

  def collectEnvironmentVariables(self):
    """Collect interesting environment variable values"""
    self.environment[RECORDS.TESTID] = os.environ.get(EnvironmentProbe.EV_TESTID, None)
    self.environment[RECORDS.PACKAGE] = os.environ.get(EnvironmentProbe.EV_PACKAGE, None)
    self.environment[RECORDS.TEST_RPM_VERSION] = os.environ.get(EnvironmentProbe.EV_TEST_VERSION, None)

  def collectRPMVersion(self, package):
    """Determines a N-V-R for installed packages. Returns None if package is not installed"""
    # pylint: disable=no-member
    if not self.rpm:
      raise EnvironmentProbeError("RPM not supported on this system")
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
    self.environment[RECORDS.HOSTNAME] = self.getfqdn()
    self.environment[RECORDS.ARCH] = os.uname()[-1]

    self.environment[RECORDS.CPU] = self.getCPU()
    self.environment[RECORDS.RAM] = self.getRAM()
    self.environment[RECORDS.HDD] = self.getHDD()

    try:
      with open("/etc/redhat-release", "r") as release_file:
        self.environment[RECORDS.RELEASE] = release_file.read().strip()
    except IOError:
      pass

  def getTestRpmBuilt(self):
    """Determines date/time when a test RPM was built. The test RPM name is passed to the test in 'packagename'
       environmental variable"""
    if self.rpm is None:
      raise EnvironmentProbeError("RPM is not supported on this system")

    package = os.environ.get(EnvironmentProbe.EV_PACKAGE_NAME, None)
    if not package:
      return None

    # pylint: disable=no-member
    testinfo = self.rpm.dbMatch("name", package) if self.rpm else None
    if not testinfo:
      return None

    buildtime = time.gmtime(int(testinfo.next().format("%(BUILDTIME)")))
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
  try:
    import rpm
    probe = EnvironmentProbe(rpm)
  except ImportError:
    probe = EnvironmentProbe()
  return Journal(probe.collect())
