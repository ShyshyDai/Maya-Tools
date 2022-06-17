# cli is short for command line interface

# a library for passing command line arguments
import argparse

# a python module for interpreting Regular Express
import re

import os

# an expansion for os, including delete, move, copy, compress or depress for files
import shutil


def main():
    parser = argparse.ArgumentParser(description="This is a batch renamer",
                                     usage="To replace all files with dell with goodbye instead: python cliRenamer.py hello goodbye")
    parser.add_argument('inString', help="The word to replace")
    parser.add_argument('outString', help="The word to replace it with")

    # optional arguments usually start with a dash and they have a short form and a long form
    # 'store_true' means if this arg is provided, while no value for it, then default to true
    parser.add_argument('-d', '--duplicate',
                        help="Whether to duplicate or replace in spot",
                        action='store_true')

    parser.add_argument('-r', '--regex',
                        help="Whether the patterns are regex or not",
                        action='store_true')
    parser.add_argument('-o', '--output', help="The output location. Default to here")

    args = parser.parse_args()
    print args

    rename(args.inString, args.outString, duplicate=args.duplicate, outDirectory=args.output, regex=args.regex)


def rename(inString, outString, duplicate=True, inDirectory=None, outDirectory=None, regex=False):

    if not inDirectory:

        # getcwd means get current working directory
        inDirectory = os.getcwd()
    if not outDirectory:
        outDirectory = inDirectory

    print outDirectory

    outDirectory = os.path.abspath(outDirectory)

    if not os.path.exists(outDirectory):
        raise IOError("%s does not exist!" % outDirectory)

    if not os.path.exists(inDirectory):
        raise IOError("%s does not exist!" % inDirectory)

    for f in os.listdir(inDirectory):
        # startswith('.') means it is a hidden file and should not be touched.
        if f.startswith('.'):
            continue

        # use regex replace or not
        # so we can use "[tT]orus" or "^sphere" to make the condition more specific
        if regex:
            name = re.sub(inString, outString, f)
        else:
            name = f.replace(inString, outString)

        # if nothing happened, then continue
        if name == f:
            continue

        src = os.path.join(inDirectory, f)
        dest = os.path.join(outDirectory, name)

        if duplicate:
            shutil.copy2(src, dest)
        else:
            os.rename(src, dest)


# the namespace is only equal to __main__ when running the scripts directly
if __name__ == '__main__':
    main()
