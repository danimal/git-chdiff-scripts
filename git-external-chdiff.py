#!/usr/bin/env python
# encoding: utf-8
"""
git-external-chdiff

Created by Dan Weeks (dan [AT] danimal [DOT] org) on 2008-02-27.
Released to the Public Domain.
"""


import sys
import subprocess
import os

help_message = '''
git-external-chdiff [old-file] [new-file]

display diffs of git files using the chdiff utility
as a proxy for GIT_EXTERNAL_DIFF via git
'''

def main(argv=None):
    """
    the basic work location
    """
    
    # set up the defaults
    wait = True
    verbose = False
    
    # pull the file names from the args passed in via git
    oldFile = sys.argv[2]
    newFile = sys.argv[5]
    try:
        waitFlag = ''
        if wait:
            waitFlag = '--wait'
        if verbose:
            print 'git-external-chdiff: comparing %s %s' % (oldFile, newFile)
        p = subprocess.Popen('chdiff %s %s %s' % (waitFlag,
                                                  oldFile,
                                                  newFile),
                             env=os.environ,
                             shell=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        p.wait()
        # ugh, this is sloppy, but we only know to clean up
        # if a chdiff wait is specified, so tidy up now
    except OSError, e:
        print >>sys.stderr, 'Execution failed:', e

if __name__ == '__main__':
    sys.exit(main())
