#!/usr/bin/env python
########################################################################.......

"""Python version of a symlink. Run the script at TARGET.
"""

from __future__ import division, print_function, unicode_literals

import os
import sys

TARGET = os.path.expanduser("~/Documents/")

def main(args):
    with open(TARGET, "rU") as f:
        scriptcode = compile(f.read(), os.path.abspath(TARGET),
                             "exec", dont_inherit=True)
        exec(scriptcode, {"__name__": "__main__"})

if __name__ == "__main__":
    main(sys.argv[1:])
