#!/usr/bin/env python
########################################################################.......

"""Open file in Quick Look.
"""

from __future__ import division, print_function, unicode_literals

import argparse
import console
import sys

def main(args):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("file", action="store", help="file to open")
    ns = p.parse_args(args)
    
    console.quicklook(ns.file)
    
    sys.exit(0)

if __name__ == "__main__":
    main(sys.argv[1:])
