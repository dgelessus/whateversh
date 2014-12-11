#!/usr/bin/env python
########################################################################.......

"""Print the contents of the given files.
"""

from __future__ import division, print_function, unicode_literals

import argparse
import sys

def main(args):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("file", action="store", nargs="+", type=unicode,
                   help="one or more files to be printed")
    ns = p.parse_args(args)
    
    status = 0
    
    for filename in ns.file:
        try:
            with open(filename, "rb") as f:
                buf = b"foo"
                while buf:
                    buf = f.read(1024).replace(b"\x00", b"")
                    print(buf.decode("ascii", errors="replace"), end="")
        except Exception as err:
            print("cat: {}: {!s}".format(type(err).__name__, err), file=sys.stderr)
            status = 1
    
    sys.exit(status)

if __name__ == "__main__":
    main(sys.argv[1:])
