'''
Created on Aug 5, 2014

@author: Petr Muller
'''
import os
from bl_journal.factory import EnvironmentProbe, RECORDS, EnvironmentProbeError, extractCpuInfo, extractMemInfo,\
  extractHddInfo
import time
import calendar

def test_getCPU():
  """Tests correct usage of /proc/cpuinfo file"""
  probe = EnvironmentProbe()
  assert probe.getCPU() is not None

  probe = EnvironmentProbe(cpuinfo="/nosuchfile")
  assert probe.getCPU() is None

def test_getRAM():
  """Tests correct usage of /proc/meminfo file"""
  probe = EnvironmentProbe()
  assert probe.getRAM() is not None

  probe = EnvironmentProbe(meminfo="/nosuchfile")
  assert probe.getRAM() is None

def test_getHDD():
  """Tests correct usage of df command"""
  probe = EnvironmentProbe()
  assert probe.getHDD() is not None

  probe = EnvironmentProbe(df="nosuchcommand")
  assert probe.getHDD() is None

def test_extractCpuInfo():
  """Test that model names and CPU counts are correctly extracted"""
  model_line = "model name  : Intel(R) Core(TM) i7-3520M CPU @ 2.90GHz"
  model = "Intel(R) Core(TM) i7-3520M CPU @ 2.90GHz"
  assert extractCpuInfo([model_line]) == ("1 x " + model)
  assert extractCpuInfo([model_line, model_line, model_line]) == ("3 x " + model)
  assert extractCpuInfo(["unknown", "content"]) == ("0 x unknown")

def test_extractMemInfo():
  """Test that RAM amount is correctly extracted"""
  memtotal_line = "MemTotal:        1810432 kB"
  assert extractMemInfo(["buffer", memtotal_line, "buffer"]) == "1768 MB"
  assert extractMemInfo(["unknown", "content"]) == "unknown MB"

def test_extractHddInfo():
  """Test that HDD sizes are correctly extracted"""
  df_header = "Filesystem                   1024-blocks     Used Available Capacity Mounted on"
  df_line_1 = "/dev/sda1                         487652   111334    346622      25% /boot"
  df_line_2 = "/dev/sda2                         184037460 53349904 121315908      31% /home"

  assert extractHddInfo([df_header, df_line_1]) == "0.5 GB"
  assert extractHddInfo([df_header, df_line_1, df_line_1]) == "0.9 GB"
  assert extractHddInfo([df_header, df_line_1, df_line_1, df_line_2]) == "176.4 GB"
  assert extractHddInfo([df_header]) is None

def test_collectEnvironmentVariables():
  """Test that the probe collects information from interesting env variable"""
  test_id = "TEST_ID_12345"
  package = "PACKAGE_UNDER_TEST"
  test_version = "TEST_VERSION"

  os.environ[EnvironmentProbe.EV_TESTID] = test_id
  os.environ[EnvironmentProbe.EV_PACKAGE] = package
  os.environ[EnvironmentProbe.EV_TEST_VERSION] = test_version

  probe = EnvironmentProbe()
  probe.collectEnvironmentVariables()
  assert probe.environment[RECORDS.TESTID] == test_id
  assert probe.environment[RECORDS.PACKAGE] == package
  assert probe.environment[RECORDS.TEST_RPM_VERSION] == test_version

class FakeRpmIterator(object):
  """Mimics rpm module query iterator"""
  # pylint: disable = too-few-public-methods
  def __init__(self, package):
    self.package = package

  def __getitem__(self, key):
    return self.package[key]

  def next(self):
    """Mimics rpm module iterator next method"""
    return self

  # pylint: disable = unused-argument
  def format(self, frmt):
    """Mimics usage of format method of rpm module iterator"""
    return self.package["BUILDTIME"]

class FakeRpm(object):
  """Mimics the behavior of RPM module"""
  def __init__(self):
    self.packages = {}

  # pylint: disable = invalid-name
  def ts(self):
    """Mimics ts() method of rpm module"""
    return self

  # pylint: disable = unused-argument
  def dbMatch(self, name, package):
    """Mimics dbMatch method of rpm module"""
    package_record = self.packages.get(package, None)
    return FakeRpmIterator(package_record) if package_record else None

  def asNVR(self, package):
    """Obtains a NVR string for a package supposed to be installed"""
    return "%(name)s-%(version)s-%(release)s" % self.packages[package]

def test_collectRPMVersion():
  """Tests that collect RPM version works:
       - returns N-V-R if RPM enabled and package installed
       - returns None of RPM enabled and package not installed
       - throws EnvironmentProbeError if RPM not enabled"""
  installed_package = "installed"
  noninstalled_package = "not-installed"

  rpm = FakeRpm()
  rpm.packages[installed_package] = {"name": "installed", "version": "1", "release": "2"}
  enviroment_with_rpm = EnvironmentProbe(rpm)
  nvr = enviroment_with_rpm.collectRPMVersion(installed_package)
  assert nvr == rpm.asNVR(installed_package)
  nvr = enviroment_with_rpm.collectRPMVersion(noninstalled_package)
  assert nvr is None

  environment_without_rpm = EnvironmentProbe(None)
  try:
    nvr = environment_without_rpm.collectRPMVersion(installed_package)
    assert False
  except EnvironmentProbeError:
    assert True

def test_collectRPMs():
  """Tests a collection of NVRs of interesting RPM packages.
     Tests EnvironmentProbeError is thrown when RPM is not supported"""
  rpm = FakeRpm()
  rpm.packages["beakerlib"] = {"name" : "beakerlib", "version": "1.9", "release": "0"}
  rpm.packages["beakerlib-redhat"] = {"name" : "beakerlib-redhat", "version": "1", "release": "12"}
  environment = EnvironmentProbe(rpm)
  environment.collectRPMs()
  assert environment.environment[RECORDS.BL_VERSION] == rpm.asNVR("beakerlib")
  assert environment.environment[RECORDS.BLRH_VERSION] == rpm.asNVR("beakerlib-redhat")

  environment = EnvironmentProbe()
  try:
    environment.collectRPMs()
    assert False
  except EnvironmentProbeError:
    assert True

def test_collectTimestamps():
  """Tests that identical times are collected as start and end times"""
  environment = EnvironmentProbe()
  environment.collectTimestamps()
  assert environment.environment[RECORDS.TIME_START] == environment.environment[RECORDS.TIME_END]
  assert environment.environment[RECORDS.TIME_START] is not None

def test_collectHostInfo():
  """Tests that the host information is collected in string form.
     There is no test that the collected information is actually correct"""
  environment = EnvironmentProbe(fqdn=lambda: "hostname")
  environment.collectHostInfo()
  assert environment.environment[RECORDS.HOSTNAME] == "hostname"
  assert environment.environment[RECORDS.CPU] is not None
  assert environment.environment[RECORDS.RAM] is not None
  assert environment.environment[RECORDS.HDD] is not None
  assert environment.environment[RECORDS.ARCH] is not None

def test_getTestRpmBuilt():
  """Tests the package built time is extracted correctly
       RPM enabled and package passed => buildtime
       RPM enabled and package not-passed => None
       RPM not enabled => raises EnvironmentProbeError"""
  rpm = FakeRpm()
  rpm.packages["package"] = {"BUILDTIME": "1403632922"}
  os.environ[EnvironmentProbe.EV_PACKAGE_NAME] = "package"
  environment = EnvironmentProbe(rpm)
  assert calendar.timegm(time.strptime(environment.getTestRpmBuilt(), EnvironmentProbe.TIMEFORMAT)) == 1403632922

  os.environ[EnvironmentProbe.EV_PACKAGE_NAME] = "no-such-stuff"
  assert environment.getTestRpmBuilt() is None

  environment = EnvironmentProbe()
  try:
    environment.getTestRpmBuilt()
    assert False
  except EnvironmentProbeError:
    assert True

def test_collect():
  """Tests the overall environment information collection"""
  rpm = FakeRpm()
  probe = EnvironmentProbe(rpm, lambda: "hostname")
  probe.collect()

