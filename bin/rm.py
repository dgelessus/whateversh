#!/usr/bin/env python
########################################################################.......

"""Delete the specified files.
"""

from __future__ import division, print_function, unicode_literals

import argparse
import errno
import os
import shutil
import sys

def main(args):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("-d", "--dir", action="store_true",
                   help="delete directories if they are empty")
    p.add_argument("-r", "-R", "--recursive", action="store_true",
                   help="recursively delete contents of directories")
    # The following three are dummy parameters, the situations they handle
    # cannot occur on iOS
    p.add_argument("--one-file-system", action="store_true",
                   help="ignore files on a file system other than that of file")
    p.add_argument("--no-preserve-root", action="store_true", dest="preserve-root",
                   help="do not treat / specially")
    p.add_argument("--preserve-root", action="store_false",
                   help="do not attempt to remove / (default behavior)")
    p.add_argument("file", action="store", nargs="+",
                   default=[os.path.expanduser("~")], type=unicode,
                   help="files to be removed")
    ns = p.parse_args(args)
    
    status = 0
    
    for f in ns.file:
        try:
            if ns.recursive:
                shutil.rmtree(f)
            elif ns.dir:
                os.rmdir(f)
            else:
                os.remove(f)
        except Exception as err:
            print("rm: {}: {!s}".format(type(err).__name__, err), file=sys.stderr)
            status = 1
    
    sys.exit(status)

if __name__ == "__main__":
    main(sys.argv[1:])
