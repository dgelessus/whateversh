#!/usr/bin/env python
########################################################################.......

"""Print all arguments to stdout, separated by spaces.
"""

from __future__ import division, print_function, unicode_literals

import sys

def main(args):
    # Not using argparse here, because echo will echo anything that is not a
    # valid and usable flag.
    end = "\n"
    escapes = False # NYI
    remove = []
    for i, arg in enumerate(args):
        if arg.startswith("-"):
            if set(arg[1:]) < set("neE"):
                for char in arg[1:]:
                    if char == "n":
                        end = ""
                    elif char == "e":
                        escapes = True
                    elif char == "E":
                        escapes = False
                remove.append(i)
            else:
                continue
    
    for i in reversed(remove):
        del args[i]
    
    print(*args, end=end)
    
    sys.exit(0)

if __name__ == "__main__":
    main(sys.argv[1:])
