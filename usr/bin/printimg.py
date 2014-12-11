#!/usr/bin/env python
########################################################################.......

"""Show image in console.
"""

from __future__ import division, print_function, unicode_literals

import argparse
import console
import sys

def main(args):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("image", action="store", help="image to show")
    ns = p.parse_args(args)
    
    console.show_image(ns.image)
    
    sys.exit(0)

if __name__ == "__main__":
    main(sys.argv[1:])
