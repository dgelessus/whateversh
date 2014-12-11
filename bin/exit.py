#!/usr/bin/env python
########################################################################.......

"""Exit the interactive shell.
"""

from __future__ import division, print_function, unicode_literals

import argparse
import sys

def main(args):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("status", action="store", nargs="?", default=0,
                   type=int, help="status code")
    ns = p.parse_args(args)
    sys.exit((ns.status, "ShellExit"))

if __name__ == "__main__":
    main(sys.argv[1:])
