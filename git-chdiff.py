#!/usr/bin/env python
# encoding: utf-8
"""
git-chdiff

Created by Dan Weeks (dan [AT] danimal [DOT] org) on 2008-02-20.
Released to the Public Domain.
"""

import getopt
import os
import subprocess
import sys
import tempfile

help_message = '''
git-chdiff <opts> [file1, file2, ...]

display diffs of git files using the chdiff utility 

  -h, --help        display this message
  -r, --revision    the revision of the file to use 
                       defaults to 'HEAD~1', the previous commit
  -w, --wait        cause chdiff to wait between files
  -v, --verbose     print more messages during operation
  --clean           clean any temp files that might have been left around
'''

tempFileSuffix = '.temp'
tempFilePrefix = 'git-chdiff'
tempDirectory = '/var/tmp'

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

def cleanTempFiles(verbose=False):
    """
    because we don't always wait for chdiff we can't always clean up
    the temp files we make.  This will wipe out all git-chdiff temp
    files owned by us.
    """
    import pwd
    import getpass
    try:
        if verbose:
            print 'scanning for git-chdiff temp files to clean'
        myUid = pwd.getpwnam(getpass.getuser())[2]
        fileList = os.listdir(tempDirectory)
        for fileName in fileList:
            nFile = os.path.join(tempDirectory, fileName)
            # skip directories
            if not os.path.isfile(nFile):
                continue
            # skip anything not named right
            if not fileName.startswith(tempFilePrefix):
                continue
            # skip if it's not our file
            if os.stat(nFile)[4] != myUid:
                continue
            # if we're here we own the file and it's named correctly
            # remove it
            if verbose:
                print 'removing temp file: %s' % nFile
            os.unlink(nFile)
        return 0
    except Exception, e:
        if verbose:
            print >>sys.stderr, 'Clean failed:', e
        return 1

def main(argv=None):
    """
    the basic work location
    """
    
    # set up the defaults
    doClean = False
    revision = 'HEAD~0' # get the previous commit
    wait = False
    verbose = False
    
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], 'hr:wv', ['clean',
                                                          'help', 
                                                          'revision=',
                                                          'wait',
                                                          'verbose'])
        except getopt.error, msg:
            raise Usage(msg)
        
        # option processing
        for option, value in opts:
            if option in ('--clean'):
                doClean = True
                del(argv[argv.index(option)])
            if option in ('-h', '--help'):
                raise Usage(help_message)
            if option in ('-r', '--revision'):
                revision = value
                del(argv[argv.index(option)])
                del(argv[argv.index(value)])
            if option in ('-w', '--wait'):
                wait = True
                del(argv[argv.index(option)])
            if option in ('-v', '--verbose'):
                verbose = True
                del(argv[argv.index(option)])
    except Usage, err:
        print >> sys.stderr, sys.argv[0].split('/')[-1] + ': ' + str(err.msg)
        print >> sys.stderr, help_message
        return 2
    
    if doClean:
        return cleanTempFiles(verbose)
    fileNames = argv[1:]
    for fileName in fileNames:
        nFile = os.path.normpath(fileName)
        gitFile = nFile
        if verbose:
            print '-> working on %s' % nFile
        if not os.path.isfile(nFile):
            #if verbose:
            print '%s is not a file' % nFile
            continue
        # make sure the file is in the git repository
        try:
            p = subprocess.Popen('git status %s' % nFile, 
                                 env=os.environ,
                                 shell=True,
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.STDOUT)
            p.wait()
            lines = p.stdout.readlines()
            if p.returncode > 0:
                # the file is probably not in the git repo
                # or is not changed, let's find out
                if lines[0].startswith('error:'):
                    print '%s not in git repository.....skipping' % nFile
                    continue
                elif lines[0].startswith('# '):
                    # we're probably not changed
                    if verbose:
                        print '    %s unchanged.....skipping' % nFile
                    continue
            # our file is there, look for the full path to it
            for line in lines:
                line = line.rstrip()
                if line.endswith(nFile):
                    # split on the three spaces between 
                    #'modified:' and the file name
                    gitFile = line.split('   ')[-1]
                    if verbose:
                        print '    git path: %s' % gitFile
                    break
        except OSError, e:
            print >>sys.stderr, 'Execution failed:', e
        # shadow the requested version of the file to a temp file
        # so we have something to diff against
        tFile = None
        try:
            p = subprocess.Popen('git show %s:%s' % (revision,gitFile), 
                                 env=os.environ,
                                 shell=True,
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.STDOUT)
            p.wait()
            # git show, it appears, doesn't return a 1 when the
            # revision/tag isn't valid so we have to scan the output
            lines = p.stdout.readlines()
            if lines[0].startswith('fatal:') or lines[0].startswith('error:'):
                print 'problem getting revision %s of file %s' % (revision,
                                                                  nFile)
                print '    %s' % lines[0]
                continue
            else:
                # save the file out
                tFile = tempfile.mkstemp(tempFileSuffix, 
                                         tempFilePrefix, 
                                         tempDirectory)
                if verbose:
                    print '    temp file: %s' % tFile[1]
                os.fdopen(tFile[0], 'w').write(''.join(lines))
        except OSError, e:
            print >>sys.stderr, 'Execution failed:', e
        # now that we have the temp file we can diff it with the
        # current file in the repo
        try:
            waitFlag = ''
            if wait:
                waitFlag = '--wait'
            p = subprocess.Popen('chdiff %s %s %s' % (waitFlag,
                                                      tFile[1],
                                                      nFile),
                                 env=os.environ,
                                 shell=True,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT)
            p.wait()
            # ugh, this is sloppy, but we only know to clean up
            # if a chdiff wait is specified, so tidy up now
            if wait:
                os.unlink(tFile[1])
        except OSError, e:
            print >>sys.stderr, 'Execution failed:', e

if __name__ == '__main__':
    sys.exit(main())
