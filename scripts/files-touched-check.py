#!/usr/bin/env python3
# Copyright (c) 2018 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import os
import sys
import subprocess

travis_commit_range = os.getenv('TRAVIS_COMMIT_RANGE')
if not travis_commit_range:
    print("Travis commit range is empty, exiting...")
    sys.exit(1)

try:
    result = subprocess.check_output(['git', 'diff', '--no-commit-id', '--name-status', '-r', travis_commit_range])
except Exception as e:
    print(e.output)
    raise e

files_added = result.decode('utf-8').splitlines()
print(files_added)
subdir_name = ""
    
for file_added in files_added:
    file_added = file_added.split(maxsplit=1)

    # Exclude certain files from some checks
    if file_added[1].startswith("scripts/") or file_added[1] in ['README.md', '.travis.yml', '.gitattributes']:
        print("Warning: modified non-gitian file", file_added[1])
        continue

    # Check that files are only added, not modified or deleted
    if file_added[0] != 'A':
        print("Error: modified or removed existing file:", file_added[1])
        sys.exit(1)

    # Check that files added are only added to a single subdirectory name
    if file_added[1].count('/') > 1:
        current_subdir = file_added[1].split('/')[1]
        if not subdir_name:
            subdir_name = current_subdir
        if subdir_name != current_subdir:
            print("Error: files added to multiple subdirectories. Already seen", subdir_name, "got", file_added[1])
            sys.exit(1)
    else:
        print("Warning: filename does not match expected form:", file_added[1])

sys.exit(0)
