#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
import os
import stat
import sys
from configurePOM import archs, detectArch
import subprocess

java_apps = {
    "BLNinfer": {"class": "probcog.srl.directed.inference.BLNinfer"},
    "BLN2MLN": {"class": "probcog.BLN2MLN"},
    "BLNprintCPT": {"class": "probcog.BLNprintCPT"},
    "BLOGDB2MLNDB": {"class": "probcog.BLOGDB2MLNDB"},
    "BNprintCPT": {"class": "probcog.BNprintCPT"},
    "BNinfer": {"class": "probcog.bayesnets.inference.BNinfer"},
    "ABL2MLN": {"class": "probcog.ABL2MLN"},
    "BN2CSV": {"class": "probcog.bayesnets.conversion.BN2CSV"},
    "BNsaveAs": {"class": "probcog.bayesnets.conversion.BNsaveAs"},
    "BNlistCPTs": {"class": "probcog.BNlistCPTs"},
    "BNrandomEvidence": {"class": "probcog.BNrandomEvidence"},
    "MLN2WCSP": {"class": "probcog.MLN2WCSP"},
    "MLNinfer": {"class": "probcog.MLNinfer"},
    "bnj": {"class": "probcog.BNJ"},
    "genDB": {"class": "probcog.genDB"},
    "groundABL": {"class": "probcog.groundABL"},
    "learnABL": {"class": "probcog.srl.directed.learning.BLNLearner"},
    "learnABLSoft": {"class": "dev.learnABLSoft"},
    "jython": {"class": 'org.python.util.jython'},
    "syprolog": {"class": "probcog.PrologShell"},
    "yprolog": {"class": "yprolog.Go"},
    "blogdb2ergevid": {"class": "blogdb2ergevid"},
    "bndb2inst": {"class": "probcog.bayesnets.conversion.BNDB2Inst"},
}
java_apps["netEd"] = java_apps["bnj"]
java_apps["pcjython"] = java_apps["jython"]

python_apps = [
    {"name": "mlnquery", "script": "$SRLDB_HOME/python/mlnQueryTool.py"},
    {"name": "mlnlearn", "script": "$SRLDB_HOME/python/mlnLearningTool.py"},
    {"name": "amlnlearn", "script": "$SRLDB_HOME/python/amlnLearn.py"},
    {"name": "blnquery", "script": "$SRLDB_HOME/python/blnQueryTool.py"},
    {"name": "bnquery", "script": "$SRLDB_HOME/python/bnQueryTool.py"},
    {"name": "blnlearn", "script": "$SRLDB_HOME/python/blnLearningTool.py"},
    {"name": "fixCR", "script": "$SRLDB_HOME/python/fixCR.py"},
    {"name": "MLN", "script": "$SRLDB_HOME/python/MLN.py"},
    {"name": "trajvis", "script": "$SRLDB_HOME/python/trajvis.py"},
    {"name": "evalSeqLabels", "script": "$SRLDB_HOME/python/evalSeqLabels.py"},
    {"name": "pmml2graphml", "script": "$SRLDB_HOME/python/pmml2graphml.py"},
]

pythonInterpreter = "python"

def adapt(name, arch):
    return name.replace("<ARCH>", arch).replace("$SRLDB_HOME", os.path.abspath(".")).replace("/", os.path.sep)

def getDependencyClasspath():
    p = subprocess.Popen("mvn dependency:build-classpath", shell=True, 
          stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    (child_stdin, child_stdout) = (p.stdin, p.stdout)
    lines = child_stdout.readlines()
    classpath = None
    for i, line in enumerate(lines):
        if "Dependencies classpath" in line:
            classpath = lines[i+1].strip()
    if classpath is None:
        print "ERROR: Could not determine classpath via maven. Check for problems in maven's output below:\n\n"
        print "".join(lines)
        sys.exit(1)
    return classpath
    
if __name__ == '__main__':
    print "\nProbCog Apps Generator\n\n"
    print "  usage: make_apps [--arch=%s] [additional JVM args]\n" % "|".join(archs)
    print
    print "  Note: Some useful JVM args include"
    print "    -Xmx8000m   set maximum Java heap space to 8000 MB"
    print "    -ea         enable assertions"
    print

    args = sys.argv[1:]
    
    # check if probcog binaries exist
    if not os.path.exists("bin") and not os.path.exists("lib/srldb.jar"):
        print "ERROR: No ProbCog binaries found. If you are using the source version of ProbCog, please compile it first using 'ant compile' or an Eclipse build"
        sys.exit(1)

    # determine architecture
    arch = None
    if len(args) > 0 and args[0].startswith("--arch="):
        arch = args[0][len("--arch="):].strip()
        args = args[1:]
    else:
        arch = detectArch()
    if arch is None:
        print "Could not automatically determine your system's architecture. Please supply the --arch argument"
        sys.exit(1)
    if arch not in archs:
        print "Unknown architecture '%s'" % arch
        sys.exit(1)
        
    jvm_userargs = " ".join(args)

    if not os.path.exists("apps"):
        os.mkdir("apps")

    print "\nDetermining dependency classpath..."
    dep_classpath = getDependencyClasspath()
    print "\nCreating application files for %s..." % arch
    classpath = os.path.pathsep.join([adapt("$SRLDB_HOME/target/classes", arch), dep_classpath])
    isWindows = "win" in arch
    isMacOSX = "macosx" in arch
    preamble = "@echo off\r\n" if isWindows else "#!/bin/sh\n"
    allargs = '%*' if isWindows else '"$@"'
    pathsep = os.path.pathsep
    for appname, app in java_apps.iteritems():
        filename = os.path.join("apps", "%s%s" % (appname, {True:".bat", False:""}[isWindows]))
        print "  %s" % filename
        with file(filename, "w") as f:
            f.write(preamble)
            addargs = "-XstartOnFirstThread" if arch in ("macosx", "macosx64") else ""
            f.write('java %s -cp "%s" %s %s %s\n' % (addargs, classpath, jvm_userargs, adapt(app["class"], arch), allargs))
            f.close()
        if not isWindows: os.chmod(filename, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
    for app in python_apps:
        filename = os.path.join("apps", "%s%s" % (app["name"], {True:".bat", False:""}[isWindows]))
        print "  %s" % filename
        f = file(filename, "w")
        f.write(preamble)
        f.write("%s -O \"%s\" %s\n" % (pythonInterpreter, adapt(app["script"], arch), allargs))
        f.close()
        if not isWindows: os.chmod(filename, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
    print

    # write shell script for environment setup
    appsDir = adapt("$SRLDB_HOME/apps", arch)
    pythonDir = adapt("$SRLDB_HOME/python", arch)
    jythonDir = adapt("$SRLDB_HOME/jython", arch)
    if not "win" in arch:
        f = file("env.sh", "w")
        f.write("export PATH=$PATH:%s\n" % appsDir)
        f.write("export PYTHONPATH=$PYTHONPATH:%s\n" % pythonDir)
        f.write("export JYTHONPATH=$JYTHONPATH:%s:%s\n" % (jythonDir, pythonDir))
        f.write("export PROBCOG_HOME=%s\n" % adapt("$SRLDB_HOME", arch))
        f.close()
        print 'Now, to set up your environment type:'
        print '    source env.sh'
        print
        print 'To permantly configure your environment, add this line to your shell\'s initialization script (e.g. ~/.bashrc):'
        print '    source %s' % adapt("$SRLDB_HOME/env.sh", arch)
        print
    else:
        f = file("env.bat", "w")
        f.write("SET PATH=%%PATH%%;%s\r\n" % appsDir)
        f.write("SET PYTHONPATH=%%PYTHONPATH%%;%s\r\n" % pythonDir)
        f.write("SET JYTHONPATH=%%JYTHONPATH%%;%s;%s\r\n" % (jythonDir, pythonDir))
        f.write("SET PROBCOG_HOME=%s\n" % adapt("$SRLDB_HOME", arch))
        f.close()
        print 'To temporarily set up your environment for the current session, type:'
        print '    env.bat'
        print
        print 'To permanently configure your environment, use Windows Control Panel to set the following environment variables:'
        print '  To the PATH variable add the directory "%s"' % appsDir
        print '  To the PYTHONPATH variable add the directory "%s"' % pythonDir
        print '  To the JYTHONPATH variable add the directories "%s" and "%s"' % (jythonDir, pythonDir)
        print 'Should any of these variables not exist, simply create them.'
