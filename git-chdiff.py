#!/usr/bin/env python
# encoding: utf-8
"""
git-chdiff

Created by Dan Weeks on 2008-02-20.
Copyright (c) 2008 Dan Weeks. All rights reserved.
"""

import getopt
import os
import sys


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
    
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "hr:w", ["help", 
                                                          "revision=",
                                                          "wait"])
        except getopt.error, msg:
            raise Usage(msg)
        
        # option processing
        for option, value in opts:
            if option in ("-h", "--help"):
                raise Usage(help_message)
            if option in ('-r', '--revision'):
                revision = value
                del(argv[argv.index(option)])
                del(argv[argv.index(value)])
            if option in ('-w', '--wait'):
                wait = True
                del(argv[argv.index(option)])
    except Usage, err:
        print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
        print >> sys.stderr, help_message
        return 2
    
    fileNames = argv[1:]
    for fileName in fileNames:
        print os.path.normpath(fileName)

if __name__ == "__main__":
    sys.exit(main())
