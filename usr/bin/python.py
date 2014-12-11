#!/usr/bin/env python
########################################################################.......

"""Run a Python script or the interactive interpreter.
"""

from __future__ import division, print_function, unicode_literals

import argparse
import code
import os
import sys

def main(args):
    # Need to split args between python command and script runtime args
    # because otherwise argparse will process the script's flags as well.
    python_args = args
    script_args = []
    for i, arg in enumerate(args):
        if not arg.startswith("-"):
            python_args = args[:i]
            script_args = args[i:]
            break
    
    p = argparse.ArgumentParser(description=__doc__)
    # file and args are not actually used and are added only to generate
    # a meaningful help message.
    p.add_argument("file", action="store", nargs="?", default="", type=unicode,
                   help="script to be executed")
    p.add_argument("args", action="store", nargs="*", default=[], type=unicode,
                   help="script runtime arguments")
    ns = p.parse_args(python_args)
    
    status = 0
    
    if script_args:
        old_argv = sys.argv
        try:
            sys.argv = script_args
            pyfile = script_args[0]
            with open(pyfile, "rU") as f:
                scriptcode = compile(f.read(), os.path.abspath(pyfile),
                                        "exec", dont_inherit=True)
                exec(scriptcode, {"__name__": "__main__"})
        except SystemExit as ex:
            status = ex.code
        except BaseException as err:
            print("python: {}: {!s}".format(type(err).__name__, err), file=sys.stderr)
        finally:
            sys.argv = old_argv
    else:
        ii = code.InteractiveConsole()
        try:
            ii.interact()
        except SystemExit as ex:
            status = ex.code
    
    sys.exit(status)

if __name__ == "__main__":
    main(sys.argv[1:])
