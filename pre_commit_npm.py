"""
pre-commit helper to call npm in a subdirectory.

The first command-line argument is the --prefix.
Following arguments are executed.

It seems like there ought to be an easier way...

https://github.com/pre-commit/pre-commit/issues/989
"""

import shutil
import subprocess
import sys


def main():
    prefix = sys.argv[1]
    args = [adjust(prefix, arg) for arg in sys.argv[2:]]
    args = [shutil.which("npm"), "--prefix", prefix] + args
    result = subprocess.run(args)  # pylint: disable=subprocess-run-check
    sys.exit(result.returncode)


def adjust(prefix: str, arg: str) -> str:
    prefix += "/"
    if arg.startswith(prefix):
        return arg[len(prefix) :]
    return arg
