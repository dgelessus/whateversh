#!/usr/bin/env python
########################################################################.......

from __future__ import division, print_function, unicode_literals

import glob
import os
import string
import sys

# Parser constants
MODE_NONE = 0x0 # Blank mode, used at start and expected at end
MODE_1QUOT = 0x1 # Used during single-quoted 'string'
MODE_2QUOT = 0x2 # Used during double-quoted "string"
MODE_ESCAPE = 0x4 # Used during backslash \escapes
MODE_ENVVAR = 0x8 # Used during single-word $envvars 
MODE_BRACENV = 0x10 # Used during multi-word ${braced envvars}

ESC_NONE = 0 # Don't escape
ESC_SEMI = 1 # Escape like in double quotes
ESC_ALL = 2 # Always escape

# Shell constants
ENVVAR_CHARS = string.ascii_letters + string.digits + "_"
PROMPT = "{path} $ " # Shell prompt format string

def has_flag(bits, flag):
    """Return whether flag is 1 in bits.
    """
    return bits & flag == flag

def collapseuser(path):
    """Reverse of os.path.expanduser: return path relative to ~, if
    such representation is meaningful. If path is not ~ or a
    subdirectory, the absolute path will be returned.
    """
    path = os.path.abspath(unicode(path))
    home = os.path.expanduser("~")
    if os.path.exists(os.path.expanduser("~/Pythonista.app")):
        althome = os.path.dirname(os.path.realpath(os.path.expanduser("~/Pythonista.app")))
    else:
        althome = home
    
    if path.startswith(home):
        collapsed = os.path.relpath(path, home)
    elif path.startswith(althome):
        collapsed = os.path.relpath(path, althome)
    else:
        collapsed = path
    
    ##print(path, home, althome, collapsed)
    
    return "~" if collapsed == "." else os.path.join("~", collapsed)

def process_escapes(cmd):
    """Process cmd and determine the "escape level" of every
    character. Returns a 2-tuple (newcmd, escapes), where newcmd
    is the input command with any escape characters removed, and
    escapes is a list of integers representing different escape
    levels. The meanings of these integers are defined in the
    ESC_* constants.
    """
    
    # Init locals
    cmd = unicode(cmd).strip()
    newcmd = ""
    escapes = []
    mode = MODE_NONE
    
    # Process cmd
    for char in cmd:
        if has_flag(mode, MODE_ESCAPE):
            # Escape this character. The exception of \ inside 1quoted
            # string is already handled with the previous char, because
            # in that case the MODE_ESCAPE flag would not be set.
            newcmd += char
            escapes.append(ESC_ALL)
            mode ^= MODE_ESCAPE
        elif char == "'" and not has_flag(mode, MODE_2QUOT):
            # Start or end 1quoted string, unless in 2quoted string
            mode ^= MODE_1QUOT
        elif char == '"' and not has_flag(mode, MODE_1QUOT):
            # Start or end 2quoted string, unless in 1quoted string
            mode ^= MODE_2QUOT
        elif char == "\\":
            # Escape the following character, unless in 1quoted string
            # If in 2quoted string, add a \ before characters that are
            # unnecessarily escaped.
            if has_flag(mode, MODE_1QUOT):
                newcmd += "\\"
                escapes.append(ESC_ALL)
            elif has_flag(mode, MODE_2QUOT) and char not in r'\$"':
                newcmd += "\\"
                escapes.append(ESC_ALL)
                mode ^= MODE_ESCAPE
            else:
                mode ^= MODE_ESCAPE
        else:
            newcmd += char
            
            if has_flag(mode, MODE_1QUOT):
                # Inside 1quoted string, full escape
                escapes.append(ESC_ALL)
            elif has_flag(mode, MODE_2QUOT):
                # Inside 2quoted string, semi-escape
                escapes.append(ESC_SEMI)
            else:
                # Outside quoted string, no escape
                escapes.append(ESC_NONE)
    
    # Post-parse sanity checks
    if mode != MODE_NONE:
        if has_flag(mode, MODE_1QUOT):
            raise ValueError("Unclosed single-quoted string in command")
        elif has_flag(mode, MODE_2QUOT):
            raise ValueError("Unclosed double-quoted string in command")
        elif has_flag(mode, MODE_ESCAPE):
            raise ValueError("Unfinished backslash escape at end of command")
        else:
            raise ValueError("Parser flags are not zero: " + hex(mode))
    
    return newcmd, escapes

def split_cmd(cmd, escapes=None):
    """Split cmd at unescaped spaces. escapes should be a list
    of escape levels (integers). If escapes is omitted or None,
    the entire command is considered unescaped.
    """
    
    # Init locals
    if escapes is None:
        escapes = [ESC_NONE] * len(cmd)
    
    cmdparts = []
    escparts = []
    curcmd = ""
    curesc = []
    
    # Process cmd and escapes
    for char, esc in zip(cmd, escapes):
        if char == " " and esc == ESC_NONE:
            # Unescaped space, split here
            if curcmd != "":
                cmdparts.append(curcmd)
                escparts.append(curesc)
            curcmd = ""
            curesc = []
        else:
            # Other character, append unchanged
            curcmd += char
            curesc.append(esc)
    
    # Append last command/escapes (if any) to return lists
    if curcmd != "":
        cmdparts.append(curcmd)
        escparts.append(curesc)
    
    return cmdparts, escparts

def parse_cmd(cmd, expanduser=True, expandvars=True, doglob=True):
    """Parse cmd as a shell input, split it into individual parts,
    and optionally expand environment variables and do globbing.
    """
    
    # Step 1 and 2 have been moved to separate functions.
    # Need to do the same for steps 3-5.
    parts, partesc = split_cmd(*process_escapes(cmd))
    
    # Step 3: Expand user home (~)
    usrparts = []
    usresc = []
    
    for part, escapes in zip(parts, partesc):
        if not expanduser:
            usrparts = parts
            usresc = partesc
            break
        
        if part.startswith("~") and (len(part) < 2 or part[1] in os.sep+os.pathsep):
            home = os.path.expanduser("~")
            usrparts.append(home + part[1:])
            usresc.append(escapes[0:1]*len(home) + escapes[1:])
        else:
            usrparts.append(part)
            usresc.append(escapes)
    
    # Step 4: Expand environment variables
    current = ""
    curesc = []
    varname = ""
    varesc = ESC_NONE
    mode = MODE_NONE
    xpndparts = []
    xpndesc = []
    
    for part, escapes in zip(usrparts, usresc):
        if not expandvars:
            xpndparts = parts
            xpndesc = partesc
            break
        
        for char, esc in zip(part, escapes):
            if char == "$" and not has_flag(mode, MODE_BRACENV) and esc != ESC_ALL:
                # Start of envvar that is not fully escaped
                if has_flag(mode, MODE_ENVVAR):
                    # Start of envvar during other envvar, expand the first one
                    mode ^= MODE_ENVVAR
                    val = os.environ.get(varname, "")
                    current += val
                    curesc += [varesc] * len(val)
                    varname = ""
                    varesc = ESC_NONE
                    
                mode ^= MODE_ENVVAR
                varesc = esc
            elif (char == "{" and varname == "" and has_flag(mode, MODE_ENVVAR)
                  and not has_flag(mode, MODE_BRACENV)):
                # { immediately after $, start of braced envvar
                mode ^= MODE_BRACENV
            elif char == "}" and has_flag(mode, MODE_BRACENV):
                # End of braced envvar
                mode ^= MODE_ENVVAR ^ MODE_BRACENV
                val = os.environ.get(varname, "")
                current += val
                curesc += [varesc] * len(val)
                varname = ""
                varesc = ESC_NONE
            elif (char not in ENVVAR_CHARS and has_flag(mode, MODE_ENVVAR)
                  and not has_flag(mode, MODE_BRACENV)):
                # Implicit end of non-braced envvar, because char is not
                # a normal varname char
                mode ^= MODE_ENVVAR
                val = os.environ.get(varname, "")
                current += val
                curesc += [varesc] * len(val)
                varname = ""
                varesc = ESC_NONE
                
                current += char
                curesc.append(esc)
            elif has_flag(mode, MODE_ENVVAR):
                # Some char during envvar
                if esc != varesc:
                    # Implicit end of envvar because escape mode changed
                    # NAND is used to ensure that the flags are set to 0,
                    # not just toggled
                    mode &= ~(MODE_ENVVAR ^ MODE_BRACENV)
                    val = os.environ.get(varname, "")
                    current += val
                    curesc += [varesc] * len(val)
                    varname = ""
                    varesc = ESC_NONE
                    
                    current += char
                    curesc.append(esc)
                else:
                    # Append to varname
                    varname += char
            else:
                # Some char outside envvar, append unchanged
                current += char
                curesc.append(esc)
        
        # End of inner for loop
        
        if has_flag(mode, MODE_ENVVAR):
            if varname == "":
                # Empty varname (i. e. $ at end of part)
                current += "$"
                curesc.append(varesc)
                if has_flag(mode, MODE_BRACENV):
                    current += "{"
                    curesc.append(varesc)
            else:
                # Implicit end of envvar because end of part (i. e. space)
                val = os.environ.get(varname, "")
                current += val
                curesc += [varesc] * len(val)
                varname = ""
                varesc = ESC_NONE
        
        xpndparts.append(current)
        xpndesc.append(curesc)
        mode = MODE_NONE
        current = ""
        curesc = []
        varname = ""
        varesc = ESC_NONE
    
    # End of outer for loop
    
    # Step 5: Globbing
    globparts = []
    for part, escapes in zip(xpndparts, xpndesc):
        if not doglob:
            globparts = xpndparts
            break
        # Check whether the part should be globbed
        hasglob = False
        for char, esc in zip(part, escapes):
            if char in "*?[" and esc == ESC_NONE:
                hasglob = True
                break
        
        if hasglob:
            # Prepare part for globbing by prefixing escaped
            # glob chars with backslashes
            globstr = ""
            for char, esc in zip(part, escapes):
                if char in "*?[]" and esc != ESC_NONE:
                    globstr += "\\" + char
                else:
                    globstr += char
            globparts += glob.glob(globstr)
        else:
            globparts.append(part)
    
    return globparts

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
        joined = os.path.join(path, filename)
        if os.path.exists(joined) and os.path.isfile(joined):
            return joined
    
    return None

def fix_globals():
    global _importcompletion
    global _outputcapture
    
    import importcompletion as _importcompletion
    import _outputcapture

def main(args):
    if not os.environ.get("PYPATH", ""):
        os.environ["PYPATH"] = os.pathsep.join([
            os.path.expanduser("~/Documents/whateversh_usr/bin"),
            os.path.expanduser("~/Documents/whateversh_bin"),
        ])
    
    status = 0
    running = True
    
    while running:
        try:
            cwd = os.getcwdu()
        except OSError as err:
            print("sh: Failed to get current working directory, returning to home.", file=sys.stderr)
            print("sh: {}: {!s}".format(type(err).__name__, err), file=sys.stderr)
            os.chdir(os.path.expanduser("~"))
            cwd = os.getcwdu()
        
        inp = raw_input(PROMPT.format(path=collapseuser(cwd)))
        parsed = parse_cmd(inp)
        if not parsed:
            # No input, do nothing
            pass
        else:
            # Some other command
            filename = find_in_path(parsed[0]) or find_in_path(parsed[0] + ".py")
            if filename:
                old_argv = sys.argv
                try:
                    sys.argv = [filename] + parsed[1:]
                    ##print(sys.argv)
                    with open(filename, "rU") as f:
                        scriptcode = compile(f.read(), os.path.abspath(filename),
                                             "exec", dont_inherit=True)
                        exec(scriptcode, {"__name__": "__main__"})
                except SystemExit as ex:
                    ##print(ex.code)
                    if isinstance(ex.code, tuple) and len(ex.code) > 1 and ex.code[1] == "ShellExit":
                        status = ex.code[0]
                        running = False
                except BaseException as err:
                    print("sh: {}: {!s}".format(type(err).__name__, err), file=sys.stderr)
                finally:
                    sys.argv = old_argv
            else:
                print("sh: {}: command not found".format(parsed[0]), file=sys.stderr)
    
    fix_globals()
    sys.exit(status)

if __name__ == "__main__":
    main(sys.argv[1:])
