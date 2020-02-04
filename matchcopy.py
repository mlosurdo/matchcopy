#!/usr/bin/env python3
import argparse
import os
import sys
import shutil
import re

from csv import DictReader
from fnmatch import fnmatch
from datetime import datetime


# Lazy handling of different input methods between Python 2 vs Python 3
try:
    input = raw_input
except NameError:
    pass


def check_inputs(args):
    # Check source path
    if os.path.exists(args.src):
        # Make absolute path
        args.src = os.path.abspath(args.src)
        print('Confirm source dir path is correct: {}'.format(args.src))
        if input('+ y/n: ') == 'y':
            pass
        else:
            print('! Exiting script: Rerun with correct source dir path.')
            sys.exit()
    else:
        print('! Exiting script: Source dir path {} does not exist.'.format(
            args.src))
        sys.exit()

    # Check destination path
    if os.path.exists(args.dst):
        # Make absolute path
        args.dst = os.path.abspath(args.dst)
        print('Confirm destination dir path is correct: {}'.format(args.dst))
        if input('+ y/n: ') == 'y':
            pass
        else:
            print('! Exiting script: Rerun with correct destination dir path.')
            sys.exit()
    else:
        print(
            '! Exiting script: Destination dir path {} does not exist.'.format(
                args.dst))
        sys.exit()

    # Check input file path if provided
    if args.inputFile:
        if os.path.exists(args.inputFile):
            # Make absolute path
            args.inputFile = os.path.abspath(args.inputFile)
            print('Confirm inputFile path is correct: {}'.format(
                args.inputFile)
            )
            if input('+ y/n: ') == 'y':
                pass
            else:
                print('! Exiting script: Rerun with correct inputFile path.')
                sys.exit()
        else:
            print('! Exiting script: InputFile path {} does not exist.'.format(
                args.inputFile))
            sys.exit()

    # Check for some patternj
    if not (args.inputFile or args.patterns):
        print('! Exiting script: Must provide either -p or -i.')
        sys.exit()

    # Confirm mode
    if args.mode in ['m', 'move']:
        print('WARNING: mode value set to "move". Confirm this is correct.')
        if input('+ y/n: ') == 'y':
            pass
        else:
            print('! Exiting script: Rerun with correct mode value.')
            sys.exit()

    return


def find_pattern_matches(src, pattern, exts):
    matches = []

    # Walk through src directory and search for/return pattern matches
    for root, _, files in os.walk(src):
        for fname in files:
            parsed_name = os.path.splitext(fname.strip())[0]
            parsed_ext = os.path.splitext(fname.strip())[1]
            if fnmatch(parsed_name, pattern):
                if exts:
                    if parsed_ext in exts:
                        matches.append(os.path.join(root, fname.strip()))
                else:
                    matches.append(os.path.join(root, fname.strip()))
    return matches


def find_all_pattern_matches(args):
    matches = []

    # Use .csv input file data if provided
    if args.inputFile:
        with open(args.inputFile) as csvfile:
            reader = DictReader(csvfile)
            rows = [row for row in reader]

        # Loop through .csv file and search for listed patterns
        for row in rows:
            pattern = row['pattern']
            if row.get('extensions', None):
                exts = row['extensions']
                exts = [ext.strip() for ext in exts.split(',')]
            else:
                exts = args.exts

            matches += find_pattern_matches(args.src, pattern, exts)

    # Use patterns provided at command line if .csv file not provided
    else:
        for pattern in args.patterns:
            matches += find_pattern_matches(args.src, pattern, args.exts)
    return list(set(matches))


def copy_file(path, src, dst, mode):
    part = re.sub(src, '', path)[1:]
    newpath = os.path.join(dst, part)
    newdir = os.path.dirname(newpath)

    # Make necessary directories
    if not os.path.exists(newdir):
        os.makedirs(newdir)

    # Copy or Move based on mode passed
    if mode in ['copy', 'c']:
        shutil.copy2(path, newpath)
    elif mode in ['move', 'm']:
        shutil.move(path, newpath)
    else:
        print('! Exiting script: mode value "{}" not recognized.'.format(mode))
        sys.exit()

    # Return old and new for receipts
    return (os.path.abspath(path), os.path.abspath(newpath))


def main(args):
    # Validate input
    check_inputs(args)

    # Search src for pattern(s) passed to script
    matches = find_all_pattern_matches(args)

    if input('+ Show all matches? y/n: ') == 'y':
        for i, match in enumerate(matches, start=1):
            print('{}. {}'.format(i, match))

    if input('+ Continue? y/n: ') == 'y':
        pass
    else:
        print('! Exiting script.')
        return

    # Copy/move matching files from src to dst
    receipts = []
    for path in matches:
        record = copy_file(path, args.src, args.dst, args.mode)
        receipts.append(record)

    # Write receipts
    ts = datetime.now().strftime('%Y-%m-%d_%I%M%p')
    receipts_fname = 'receipts_{}.txt'.format(ts)
    with open(receipts_fname, 'w+') as f:
        num = len(receipts)
        f.write('Total number of files copied/moved: {}\n\n'.format(num))
        for record in receipts:
            f.write('Old: {}\n'.format(record[0]))
            f.write('New: {}\n\n'.format(record[1]))
    print('Script complete.')
    print('Receipts located at: {}'.format(os.path.abspath(receipts_fname)))
    return


if __name__ == '__main__':
    # Initialize parser
    parser = argparse.ArgumentParser(
        description="Use this script to... "
    )

    # Add parameters: positional
    parser.add_argument(
        'src',
        help='Path to "source" root directory to search.'
    )

    parser.add_argument(
        'dst',
        help='Path to "destination" root directory to move matching files.'
    )

    # Add parameters: optional
    parser.add_argument(
        '-p',
        '--patterns',
        nargs='+',
        help='Single filename pattern to search/move.',
        default=None
    )

    parser.add_argument(
        '-i',
        '--inputFile',
        help='Path to .csv file containing filename patterns to search/move.',
        default=None
    )

    parser.add_argument(
        '-e',
        '--exts',
        nargs='+',
        help='List of extensions to copy/move, separated by spaces.',
        default=None
    )

    parser.add_argument(
        '-m',
        '--mode',
        help='Defines what to do with file when found, "copy" vs "move".',
        choices=['copy', 'c', 'move', 'm'],
        default='copy'
    )

    # Get arguments passed at command line
    args = parser.parse_args()

    # Run main
    main(args)
