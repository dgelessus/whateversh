#!/usr/bin/env python
########################################################################.......

"""Print the current working directory.
"""

from __future__ import division, print_function, unicode_literals

import argparse
import os
import sys

def main(args):
    p = argparse.ArgumentParser(description=__doc__)
    ns = p.parse_args(args)
    
    status = 0
    
    try:
        print(os.getcwdu())
    except Exception as err:
        print("pwd: {}: {!s}".format(type(err).__name__, err), file=sys.stderr)
        status = 1
    
    sys.exit(status)

if __name__ == "__main__":
    main(sys.argv[1:])
