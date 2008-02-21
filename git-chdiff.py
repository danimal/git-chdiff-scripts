#!/usr/bin/env python
# encoding: utf-8
"""
git-chdiff

Created by Dan Weeks on 2008-02-20.
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
'''


class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg


def main(argv=None):
    """
    the basic work location
    """
    
    # set up the defaults
    revision = 'HEAD~1'
    wait = False
    verbose = True #XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], 'hr:wv', ['help', 
                                                          'revision=',
                                                          'wait',
                                                          'verbose'])
        except getopt.error, msg:
            raise Usage(msg)
        
        # option processing
        for option, value in opts:
            if option in ('-h', '--help'):
                raise Usage(help_message)
            if option in ('-r', '--revision'):
                revision = value
                del(argv[argv.index(option)])
                del(argv[argv.index(value)])
            if option in ('-w', '--wait'):
                wait = True
                del(argv[argv.index(option)])
            if option in ('-v', '--version'):
                verbose = True
                del(argv[argv.index(option)])
    except Usage, err:
        print >> sys.stderr, sys.argv[0].split('/')[-1] + ': ' + str(err.msg)
        print >> sys.stderr, help_message
        return 2
    
    fileNames = argv[1:]
    for fileName in fileNames:
        nFile = os.path.normpath(fileName)
        if verbose:
            print '-> working on %s' % nFile
        # make sure the file is in the git repository
        try:
            p = subprocess.Popen('git status %s' % nFile, 
                                 env=os.environ,
                                 shell=True,
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
            p.wait()
            if p.returncode > 0:
                # the file is probably not in the git repo
                print '%s not in git repository.....skipping' % nFile
                continue
        except OSError, e:
            print >>sys.stderr, 'Execution failed:', e
        # shadow the requested version of the file to a temp file
        # so we have something to diff against
        try:
            p = subprocess.Popen('git show %s:%s' % (revision,nFile), 
                                 env=os.environ,
                                 shell=True,
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
            p.wait()
            # git show, it appears, doesn't return a 1 when the
            # revision/tag isn't valid so we have to scan the output
            lines = p.stdout.readlines()
            if lines[0].startswith('fatal:'):
                print 'problem getting revision of file %s' % nFile
                print line
            else:
                # save the file out
                tFile = tempfile.mkstemp('.temp', 'git-chdiff', '/var/tmp')
                if verbose:
                    print '\ttemp file: %s' % tFile[1]
                os.fdopen(tFile[0], 'w').write(''.join(lines))
        except OSError, e:
            print >>sys.stderr, 'Execution failed:', e

if __name__ == '__main__':
    sys.exit(main())
