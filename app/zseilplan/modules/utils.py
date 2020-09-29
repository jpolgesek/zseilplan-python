#!/usr/bin/env python3
import sys


def log(text, end="\n", overwrite = False):
    if overwrite:
        sys.stdout.write('\r')
    sys.stdout.write(text)
    sys.stdout.write(end)
    sys.stdout.flush()

    return True

def step(text, state = "    "):
    if state == "    ":
        log("[{}] {}".format(state, text), end="")
    else:
        log("[{}] {}".format(state, text), overwrite=True)
    
    return True

def substep(text = ""):
    print("       - {}".format(text))

def debug(text = "", level=2):
    #TODO: check level
    #log(text)
    return True


def check_python_version(minimal = (3,6), preferred = (3,7)):
    version = sys.version_info

    if version < minimal:
        print(f"This program requires Python version {minimal}, but you are running {version}. Exiting.")
        sys.exit(1)
    
    if version < preferred:
        print(f"This program prefers Python version {preferred}, but will run on version {version}.")
        print(f"Warning! utils.hash might work incorrectly.")
