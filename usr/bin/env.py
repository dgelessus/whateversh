#!/usr/bin/env python
########################################################################.......

"""Run a command in a modified environment.
"""

from __future__ import division, print_function, unicode_literals

import argparse
import os
import sys

def find_in_path(filename):
    """Search all entries in $PYPATH, $PATH and sys.path for filename
    and return the first occurence, or None if the file couldn't be found.
    """
    paths = (["."] # Force cwd to be searched regardless of envvars
           + os.environ.get("PYPATH", "").split(os.pathsep)
           + os.environ.get("PATH", "").split(os.pathsep)
           + sys.path)
    
    for path in paths:
        path = unicode(path)
        try:
            files = os.listdir(path)
        except OSError:
            continue
        
        if filename in files:
            joined = os.path.join(path, filename)
            if os.path.isfile(joined):
                return joined
    
    return None

def main(args):
    # Need to split args between env and command runtime args because
    # otherwise argparse will process the command's flags as well.
    env_args = args
    cmd_args = []
    for i, arg in enumerate(args):
        if not arg.startswith("-"):
            env_args = args[:i]
            cmd_args = args[i:]
            break
    
    p = argparse.ArgumentParser(description=__doc__)
    # These arguments are never actually parsed by argparse and are
    # only registered so they appear in the help.
    p.add_argument("cmd", action="store", nargs="?", default="printenv", type=unicode,
                   help="command to be executed")
    p.add_argument("args", action="store", nargs="*", default=[], 
                   type=unicode, help="arguments to be passed to command")
    ns = p.parse_args(env_args)
    
    status = 0
    
    try:
        cmd = cmd_args[0] if len(cmd_args) > 0 else "printenv"
        filename = find_in_path(cmd) or find_in_path(cmd + ".py")
        if filename:
            old_argv = sys.argv
            try:
                sys.argv = [filename] + cmd_args[1:]
                ##print(sys.argv)
                with open(filename, "rU") as f:
                    scriptcode = compile(f.read(), os.path.abspath(filename),
                                            "exec", dont_inherit=True)
                    exec(scriptcode, {"__name__": "__main__"})
            except SystemExit as ex:
                status = ex.code
            except BaseException as err:
                print("env: {}: {!s}".format(type(err).__name__, err), file=sys.stderr)
            finally:
                sys.argv = old_argv
        else:
            print("env: {}: command not found".format(cmd), file=sys.stderr)
    finally:
        pass
    
    sys.exit(status)

if __name__ == "__main__":
    main(sys.argv[1:])
