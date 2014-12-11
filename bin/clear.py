#!/usr/bin/env python
########################################################################.......

"""Clear the console output.
"""

from __future__ import division, print_function, unicode_literals

import argparse
import sys

def main(args):
    p = argparse.ArgumentParser(description=__doc__)
    ns = p.parse_args(args)
    
    status = 0
    
    try:
        import console
        console.clear()
    except ImportError as err:
        print("clear: not supported on this platform ({!s})".format(err), file=sys.stderr)
        status = 1
    except Exception as err:
        print("clear: {}: {!s}".format(type(err).__name__, err), file=sys.stderr)
        status = 1
    
    sys.exit(status)

if __name__ == "__main__":
    main(sys.argv[1:])
