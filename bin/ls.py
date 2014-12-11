#!/usr/bin/env python
########################################################################.......

"""List the contents of the current directory.
"""

from __future__ import division, print_function, unicode_literals

import argparse
import os
import stat
import sys

WIDTH = 80

def has_flag(bits, flag):
    return bits & flag == flag

def main(args):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("-a", "--all", action="store_true",
                   help="list all files, including hidden ones")
    p.add_argument("-A", "--almost-all", action="store_true",
                   help="like -a, but don't include . and ..")
    p.add_argument("-B", "--ignore-backups", action="store_true",
                   help="don't include backups (files ending in ~)")
    p.add_argument("-F", "--file-type", action="store_true",
                   help="show type indicators /@|= behind directories, symlinks, FIFOs and sockets")
    p.add_argument("dir", action="store", nargs="*", default=[os.getcwdu()], 
                   type=unicode, help="directory to be listed, defaults to current directory")
    ns = p.parse_args(args)
    
    status = 0
    
    try:
        items = os.listdir(ns.dir[0])
    except Exception as err:
        print("ls: {}: {!s}".format(type(err).__name__, err), file=sys.stderr)
        status = 1
        sys.exit(status)
    
    if ns.all:
        items = [".", ".."] + items
    elif not ns.almost_all:
        items = [i for i in items if not i.startswith(".")]
    
    if ns.ignore_backups:
        items = [i for i in items if not i.endswith("~")]
    
    if not items:
        sys.exit(status)
    
    longest = max(map(len, items)) + 2
    cols = WIDTH // longest
    text = ""
    for i, item in enumerate(items):
        text += item
        if ns.file_type:
            try:
                statinfo = os.stat(item)
            except OSError:
                text += "?"
            else:
                if stat.S_ISDIR(statinfo.st_mode):
                    text += "/"
                elif stat.S_ISLNK(statinfo.st_mode):
                    text += "@"
                elif stat.S_ISFIFO(statinfo.st_mode):
                    text += "|"
                elif stat.S_ISSOCK(statinfo.st_mode):
                    text += "="
                else:
                    text += " "
        
        text += " " * (longest - len(item) - (1 if ns.file_type else 0))
        if (i+1) % cols == 0:
            text += "\n"
    
    print(text)
    
    sys.exit(status)

if __name__ == "__main__":
    main(sys.argv[1:])
