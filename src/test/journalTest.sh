# Copyright (c) 2006 Red Hat, Inc. All rights reserved. This copyrighted material 
# is made available to anyone wishing to use, modify, copy, or
# redistribute it subject to the terms and conditions of the GNU General
# Public License v.2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# Authors:
#   Ales Zelinka <azelinka@redhat.com>
#   Petr Splichal <psplicha@redhat.com>

test_rlStartJournal(){ return 0; } # this is tested below, we keep this just for
                                   # compatibility
test_rlJournalStart(){
    assertTrue "journal started" "rlJournalStart"
    assertTrue "directory set & created" "[ -d $BEAKERLIB_DIR ]"
    assertTrue "journal file created" "[ -f $BEAKERLIB_JOURNAL ]"
    assertTrue "journal is well-formed XML" "xmllint $BEAKERLIB_JOURNAL >/dev/null"

    # existing journal is not overwritten
    silentIfNotDebug 'rlLog "I am"'
    rlJournalStart
    assertTrue "existing journal not overwritten" \
            "grep 'I am' $BEAKERLIB_JOURNAL"

    # if TESTID is unset, use user-provided BEAKERLIB_DIR, if available
    local OLDTESTID="$TESTID"
    unset TESTID
    local OLDDIR="$BEAKERLIB_DIR"
    local NEWDIR="$( mktemp -d /tmp/beakerlib-test-XXXXXXXX )" # no-reboot
    export BEAKERLIB_DIR="$NEWDIR"
    local OLDJOURNAL="$BEAKERLIB_JOURNAL"

    journalReset
    assertTrue "A new user-provided dir created when no TESTID available" \
            "[ '$BEAKERLIB_DIR' = '$NEWDIR' -a -d $BEAKERLIB_DIR ]"
    assertTrue "A new journal created in user-provided directory" \
	    "[ '$BEAKERLIB_JOURNAL' != '$OLDJOURNAL' -a -f $BEAKERLIB_JOURNAL ]"

    rm -rf "$NEWDIR"
    export TESTID="$OLDTESTID"
    export BEAKERLIB_DIR="$OLDDIR"
    export BEAKERLIB_JOURNAL="$OLDJOURNAL"
    unset OLDTESTID OLDDIR NEWDIR OLDJOURNAL

    # if both TESTID and BEAKERLIB_DIR are unset, a temp dir should be created
    local OLDTESTID="$TESTID"
    unset TESTID
    local OLDDIR="$BEAKERLIB_DIR"
    unset BEAKERLIB_DIR
    local OLDJOURNAL="$BEAKERLIB_JOURNAL"

    journalReset
    assertTrue "A new random dir created when no TESTID available" \
            "[ '$BEAKERLIB_DIR' -a -d $BEAKERLIB_DIR ]"
    assertTrue "A new journal created in random directory" \
	    "[ '$BEAKERLIB_JOURNAL' != '$OLDJOURNAL' -a -f $BEAKERLIB_JOURNAL ]"

    rm -rf "$BEAKERLIB_DIR"
    export TESTID="$OLDTESTID"
    export BEAKERLIB_DIR="$OLDDIR"
    export BEAKERLIB_JOURNAL="$OLDJOURNAL"
    unset OLDTESTID OLDDIR OLDJOURNAL
}

test_rlJournalPrint(){
    #add something to journal
    silentIfNotDebug "rlPhaseStart FAIL"
    silentIfNotDebug 'rlAssert0 "failed" 1'
    silentIfNotDebug 'rlAssert0 "passed" 0'
    silentIfNotDebug 'rlPhaseEnd'
    silentIfNotDebug 'rlLog "loginek"'
    assertTrue "rlJournalPrint dump is wellformed xml" \
            "rlJournalPrint |xmllint -"
    assertTrue "rlPrintJournal dump still works" \
            "rlPrintJournal | grep -v 'rlPrintJournal is obsoleted by rlJournalPrint' | xmllint -"
    assertTrue "rlPrintJournal emits obsolete warnings" \
            "rlPrintJournal | grep 'rlPrintJournal is obsoleted by rlJournalPrint' -q"
    rm -rf $BEAKERLIB_DIR
}

test_rlJournalPrintText(){
    #this fnc is used a lot in other function's tests
    #so here goes only some specific (regression?) tests

    #must not tracedump on an empty log message
    #outside-of-phase log
    silentIfNotDebug 'rlLog ""'
    silentIfNotDebug 'rlPhaseStart FAIL'
    #inside-phase log
    silentIfNotDebug 'rlLog ""'
    assertFalse "no traceback during log creation" \
            "rlJournalPrintText 2>&1 | grep Traceback"
    rm -rf $BEAKERLIB_DIR
    silentIfNotDebug rlJournalStart

    #no traceback on non-ascii characters (bz471257)
    silentIfNotDebug 'rlPhaseStart FAIL'
    assertTrue "no traceback on non-ascii chars (rlLog)" \
      'rlLog "ščřžýáíéーれっどはっと"'
    assertFalse "no traceback on non-ascii chars (rlJournalPrintText)" \
            "rlJournalPrintText 2>&1 | grep Traceback"
    rm -rf $BEAKERLIB_DIR

    # no traceback on non-xml garbage
    journalReset
    silentIfNotDebug 'rlPhaseStart FAIL'
    local X00="$( echo $'\x00' )"
    assertTrue "no traceback on non-xml characters [1] (rlLog)" "rlLog '$X00'"
    assertFalse "no traceback on non-xml characters [1] (rlJournalPrintText)" \
            "rlJournalPrintText 2>&1 | grep Traceback"
    local X0C="$( echo $'\x0c' )"
    assertTrue "no traceback on non-xml characters [2] (rlLog)" "rlLog '$X0C'"
    assertFalse "no traceback on non-xml characters [2] (rlJournalPrintText)" \
            "rlJournalPrintText 2>&1 | grep Traceback"
    local X1F="$( echo $'\x1F' )"
    assertTrue "no traceback on non-xml characters [3] (rlLog)" "rlLog '$X1F'"
    assertFalse "no traceback on non-xml characters [3] (rlJournalPrintText)" \
            "rlJournalPrintText 2>&1 | grep Traceback"
    local FF="$( echo $'\xFF' )"
    assertTrue "rlLog '\\xFF' does not give a traceback" \
               "rlLog '$FF' &> /dev/null"
    assertTrue "rlPass '\\xFF' does not give a traceback" \
               "rlPass '$FF' &> /dev/null"
    local A2=$(mktemp)
    cat > $A2 << EOF
in: 0x2083010, size: 12, use: 8
out: 0x2083060, size: 24, use: 0
handler: 0x2083be0, name: ISO-8859-5, input: (nil), iconv_in: 0x2083c30
xmlCharEncInFunc result: 21
out: 0x2083060, size: 24, use: 21
e2 (�) 84 (�) 96 (�) e2 (�) 84 (�) 96 (�) e2 (�) 84 (�) 96 (�) e2 (�) 84 (�) 96 (�) e2 (�) 84 (�) 96 (�) e2 (�) 84 (�) 96 (�) e2 (�) 84 (�) 96 (�) 
EOF
    assertTrue "rlLog with specific UTF-8 characters won't give a traceback" \
               "rlLog '$(cat $A2 )' &>/dev/null"
    assertFalse "rlJournalPrintText won't give a traceback" \
               "rlJournalPrintText 2>&1 | grep Traceback"
    rm -f $A2
    rm -rf $BEAKERLIB_DIR

    # multiline logs
    journalReset

    local MULTILINE="$( echo -e 'line1\nline2' )"
    silentIfNotDebug "rlLog '$MULTILINE'"
    rlJournalPrintText | grep -v "line2" | grep -q "LOG.*line1" &&
            rlJournalPrintText | grep -v "line1" | grep -q "LOG.*line2"
    assertTrue "multiline logs tagged on each line" "[ $? -eq 0 ]"
    rm -rf $BEAKERLIB_DIR

    # obsoleted rlCreateLogFromJournal still works
    journalReset
    assertTrue "Checking the rlCreateLogFromJournal still works" \
            "rlCreateLogFromJournal | grep -q 'TEST PROTOCOL'"
    assertTrue "Obsoleted message for rlCreateLogFromJournal" \
            "rlCreateLogFromJournal | grep -q 'obsoleted by rlJournalPrintText'"
    rm -rf $BEAKERLIB_DIR

    # whole test summary (Bug 464155 -  [RFE] summary of phase results in logfile)
    ( journalReset
      rlPhaseStart FAIL failed ; rlAssert0 "assert" 1 ; rlAssert0 "assert" 1 ; rlPhaseEnd;
      rlPhaseStart FAIL failed2 ; rlAssert0 "assert" 1 ; rlPhaseEnd;
      rlJournalEnd; ) &>/dev/null
    assertTrue "failed test counted in summary" "rlJournalPrintText |grep 'Phases: 0 good, 2 bad'"
    assertTrue "whole test reported as FAILed" "rlJournalPrintText |grep '\[ *FAIL *\].* RESULT: beakerlib-unit-tests'"
    rm -rf $BEAKERLIB_DIR
    ( journalReset
      rlPhaseStart FAIL passed ; rlAssert0 "assert" 0 ; rlPhaseEnd
      rlPhaseStart FAIL passed2 ; rlAssert0 "assert" 0 ; rlPhaseEnd
      rlJournalEnd; ) &>/dev/null
    assertTrue "passed test counted in summary" "rlJournalPrintText |grep 'Phases: 2 good, 0 bad'"
    assertTrue "whole test reported as PASSed" "rlJournalPrintText |grep '\[ *PASS *\].* RESULT: beakerlib-unit-tests'"
    rm -rf $BEAKERLIB_DIR
    ( journalReset
      rlPhaseStart FAIL passed ; rlAssert0 "assert" 0 ; rlPhaseEnd
      rlPhaseStart FAIL failed ; rlAssert0 "assert" 1 ; rlPhaseEnd
      rlPhaseStart FAIL passed2 ; rlAssert0 "assert" 0 ; rlPhaseEnd
      rlJournalEnd; ) &>/dev/null
    assertTrue "both failed and passed phases counted in summary" "rlJournalPrintText |grep 'Phases: 2 good, 1 bad'"
    assertTrue "whole test reported as FAILed" "rlJournalPrintText |grep '\[ *FAIL *\].* RESULT: beakerlib-unit-tests'"
    rm -rf $BEAKERLIB_DIR
  }

test_journalOptionalFields() {
    rm -rf $BEAKERLIB_DIR

    export testversion="t3st.1.2.3"
    export packagename="glibc"
    journalReset &>/dev/null
    silentIfNotDebug 'rlRun "true"'
    rlJournalEnd &>/dev/null

    assertFalse "Checking the rlJournalPrintText does not show CPU line" \
        "rlJournalPrintText | grep 'CPUs'"
    assertFalse "Checking the rlJournalPrintText does not show RAM line" \
        "rlJournalPrintText | grep 'RAM size'"
    assertFalse "Checking the rlJournalPrintText does not show HDD line" \
        "rlJournalPrintText | grep 'HDD size'"
    assertTrue "Checking the rlJournalPrintText --full-journal shows CPU line" \
        "rlJournalPrintText --full-journal | grep 'CPUs'"
    assertTrue "Checking the rlJournalPrintText --full-journal shows RAM line" \
        "rlJournalPrintText --full-journal | grep 'RAM size'"
    assertTrue "Checking the rlJournalPrintText --full-journal shows HDD line" \
        "rlJournalPrintText --full-journal | grep 'HDD size'"
    assertTrue "rlJournalPrintText shows beakerlib version" \
        "rlJournalPrintText | grep 'beakerlib RPM'"
    assertTrue "rlJournalPrintText shows beakerlib-redhat version" \
        "rlJournalPrintText | grep 'bl-redhat RPM'"
    assertTrue "rlJournalPrintText shows test version" \
        "rlJournalPrintText | grep 'Test version  : $testversion'"
    assertTrue "rlJournalPrintText shows test built date" \
        "rlJournalPrintText | grep 'Test built    :'"

    unset testversion
    unset packagename
    journalReset &>/dev/null
    silentIfNotDebug 'rlRun "true"'
    rlJournalEnd &>/dev/null

    assertFalse "rlJournalPrintText does not show test version" \
        "rlJournalPrintText | grep 'Test version  : $testversion'"
    assertFalse "rlJournalPrintText does not show test built date" \
        "rlJournalPrintText | grep 'Test built    :'"
}

test_rlGetTestState(){
    #test this in developer mode to verify BZ#626953
    TESTID_BACKUP=$TESTID
    unset TESTID
    journalReset
    assertRun "rlPhaseStart FAIL phase1"
    rlGetTestState ; assertTrue "rlGetTestState return 0 at the beginning of the test" "[ $? -eq 0 ]"
    rlGetPhaseState ; assertTrue "rlGetPhaseState return 0 at the beginning of the test" "[ $? -eq 0 ]"
    assertRun 'rlAssert0 "failing assert#1" 1' 1
    rlGetTestState ; assertTrue "rlGetTestState return 1 after assert failed" "[ $? -eq 1 ]"
    rlGetPhaseState ; assertTrue "rlGetPhaseState return 1 after assert failed" "[ $? -eq 1 ]"
    assertRun 'rlAssert0 "failing assert#2" 1' 1
    rlGetTestState ; assertTrue "rlGetTestState return 2 after assert failed" "[ $? -eq 2 ]"
    rlGetPhaseState ; assertTrue "rlGetPhaseState return 2 after assert failed" "[ $? -eq 2 ]"
    assertRun 'for i in $(seq 3 260) ; do rlAssert0 "failing assert#$i" 1; done' 1 "Creating 260 failed asserts"
    rlGetTestState ; assertTrue "rlGetTestState return 255 after more that 255 asserts failed" "[ $? -eq 255 ]"
    rlGetPhaseState ; assertTrue "rlGetPhaseState return 255 after more that 255 asserts failed" "[ $? -eq 255 ]"
    assertRun "rlPhaseEnd"

    assertRun "rlPhaseStart FAIL phase2"
    rlGetTestState ; assertTrue "rlGetTestState return non-zero in passing phase but failing test" "[ $? -ne 0 ]"
    rlGetPhaseState ; assertTrue "rlGetPhaseState return 0 in passing phase but failing test" "[ $? -eq 0 ]"
    assertRun "rlPhaseEnd"
    TESTID=$TESTID_BACKUP
}

test_rlGetPhaseState(){
    assertLog "Tests for this function are included in rlGetTestState since it is more or less the same"
}

test_packageLogging(){
  journalReset
  silentIfNotDebug 'rlPhaseStartTest'
  silentIfNotDebug 'rlAssertRpm glibc'
  assertTrue "One <pkgdetails> tag immediately after rlAssertRpm" "rlJournalPrint raw | grep -o -n '<pkgdetails[^<>]*>glibc'"
  TAGS="$(rlJournalPrint raw | grep -o -n '<pkgdetails[^<>]*>glibc' | wc -l)"
  silentIfNotDebug 'rlPhaseEnd'
  silentIfNotDebug 'rlPhaseStartTest'
  assertTrue  "More <pkgdetails> tag immediately after new phase starts" "[ $( rlJournalPrint raw | grep -o -n '<pkgdetails[^<>]*>glibc' | wc -l ) -gt $TAGS ]"
  silentIfNotDebug 'rlPhaseEnd'
}

test_packageLoggingNotPresent() {
  export PACKAGE="IreallyHOPEnoPACKAGElikeTHISwillEVERexist"
  journalReset
  assertTrue "Non-installed package is marked as such" "rlJournalPrint raw | grep -o -n '<pkgnotinstalled>IreallyHOPEnoPACKAGElikeTHISwillEVERexist'"
  assertFalse "Non-installed package is not marked as installed" "rlJournalPrint raw | grep -o -n '<pkgdetails>IreallyHOPEnoPACKAGElikeTHISwillEVERexist'"

  export PACKAGE="glibc"
  journalReset
  assertTrue "Installed package is marked as such" "rlJournalPrint raw | grep -o -n '<pkgdetails[^<>]*>glibc'"
  assertFalse "Installed package is not marked as non-installed" "rlJournalPrint raw | grep -o -n '<pkgnotinstalled>glibc'"
  unset PACKAGE
}

test_packageLoggingGuess() {
  unset PACKAGE
  export TEST="/some/glibc/Regression/test"
  journalReset
  assertTrue "Package name was correctly guessed from TEST" "rlJournalPrint raw | grep -q -o -n '<pkgdetails[^<>]*>glibc'"

  unset TEST
  journalReset
  assertFalse "No <pkgdetails> tag when TEST and PACKAGE are not set" "rlJournalPrint | grep -q '<pkgdetails>'"

  export TEST="weeee some garbage"
  journalReset
  assertTrue "rlJournalStart survives garbage in TEST" "rlJournalStart"
  assertFalse "No <pkgdetails> tag when TEST is garbage" "rlJournalPrint | grep -q '<pkgdetails>'"
}

CLEAR_XUNIT_TEST_STATE() {
  XUNIT_TEST_SUBMITTED_FILES=""
  XUNIT_TEST_SUBMITTED_FILE=""
  XUNIT_TEST_VALID_XML=""
  XUNIT_TEST_XUNIT_OK=""
}

UNSET_XUNIT_TEST_STATE() {
  unset XUNIT_TEST_SUBMITTED_FILES
  unset XUNIT_TEST_SUBMITTED_FILE
  unset XUNIT_TEST_VALID_XML
  unset XUNIT_TEST_XUNIT_OK
}

testsuite_submit_xunit() {
  local SUBMITTED_FILE="$4"

  if [ -z "$XUNIT_TEST_SUBMITTED_FILE" ]
  then
    XUNIT_TEST_SUBMITTED_FILE=yes
  fi

  if ! [ -f "$SUBMITTED_FILE" ]
  then
    XUNIT_TEST_SUBMITTED_FILE=no
    return 1
  else
    XUNIT_TEST_SUBMITTED_FILES="$XUNIT_TEST_SUBMITTED_FILES:$SUBMITTED_FILE"
  fi

  if xmllint --noout $SUBMITTED_FILE
  then
    XUNIT_TEST_VALID_XML="$SUBMITTED_FILE"
  else
    return 1
  fi

  if grep -q '<testsuite name="weeee some garbage"' $SUBMITTED_FILE && \
     grep -q '<properties>' $SUBMITTED_FILE && \
     grep -q '<testcase name="Setup" assertions="1">' $SUBMITTED_FILE && \
     grep -q '<failure message="Nope ' $SUBMITTED_FILE
  then
    XUNIT_TEST_XUNIT_OK="$SUBMITTED_FILE"
  fi
}

test_rlPhaseEnd_xUnit() {
  export BEAKERLIB_COMMAND_SUBMIT_LOG=testsuite_submit_xunit
  silentIfNotDebug 'journalReset'
  silentIfNotDebug 'rlPhaseStartSetup'
  silentIfNotDebug 'rlAssert0 "Nope" 1'

  CLEAR_XUNIT_TEST_STATE
  silentIfNotDebug 'rlPhaseEnd'

  assertTrue "rlPhaseEnd submitted existing files: [$XUNIT_TEST_SUBMITTED_FILES]" "[ '$XUNIT_TEST_SUBMITTED_FILE' == 'yes' ]"
  assertTrue "At least one of submitted files was valid XML: [$XUNIT_TEST_VALID_XML]" "[ -n '$XUNIT_TEST_VALID_XML' ]"
  assertTrue "Valid XML looks like xUnit: [$XUNIT_TEST_XUNIT_OK]" "[ -n '$XUNIT_TEST_XUNIT_OK' ]"

  UNSET_XUNIT_TEST_STATE
  unset BEAKERLIB_COMMAND_SUBMIT_LOG
}

test_rlJournalEnd_xUnit() {
  export BEAKERLIB_COMMAND_SUBMIT_LOG=testsuite_submit_xunit
  silentIfNotDebug 'journalReset'
  silentIfNotDebug 'rlPhaseStartSetup'
  silentIfNotDebug 'rlAssert0 "Nope" 1'
  silentIfNotDebug 'rlPhaseEnd'

  CLEAR_XUNIT_TEST_STATE

  silentIfNotDebug 'rlJournalEnd'

  assertTrue "rlPhaseEnd submitted existing files: [$XUNIT_TEST_SUBMITTED_FILES]" "[ '$XUNIT_TEST_SUBMITTED_FILE' == 'yes' ]"
  assertTrue "At least one of submitted files was valid XML: [$XUNIT_TEST_VALID_XML]" "[ -n '$XUNIT_TEST_VALID_XML' ]"
  assertTrue "Valid XML looks like xUnit: [$XUNIT_TEST_XUNIT_OK]" "[ -n '$XUNIT_TEST_XUNIT_OK' ]"

  UNSET_XUNIT_TEST_STATE
  unset BEAKERLIB_COMMAND_SUBMIT_LOG

  local TID_BACK=$TESTID
  unset TESTID
  assertTrue 'Without TESTID set, rlJournalEnd reports xUnit directly' 'rlJournalEnd 2>&1 | grep "JOURNAL xUnit: /"'
  export TESTID=$TID_BACK
}
