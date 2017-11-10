#!/usr/bin/env python3
# Copyright (c) 2017 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import os
import sys
import subprocess

travis_commit_range = os.getenv('TRAVIS_COMMIT_RANGE')
if not travis_commit_range:
    print("Travis commit range is empty, exiting...")
    sys.exit(0)

try:
    result = subprocess.check_output(['git', 'diff', '--name-only', travis_commit_range])
except Exception as e:
    print(e.output)
    raise e
files_added = result.decode('utf-8').split()

for file_added in files_added:

    # Skip files which are not assert files
    if not file_added.endswith(".assert") or "/" not in file_added:
        continue

    digests = {}
    assert_filepath = os.path.abspath(file_added)

    with open(assert_filepath, 'r') as assert_file: 
        for line in assert_file.readlines():
            line = line.strip()

            # We only really care about lines containing "bitcoin"
            if line.startswith("-") or "bitcoin" not in line:
                continue
            
            digest, file = line.split()
            digests[file] = digest
    
    release_version = file_added.split("/", 1)[0]
    print("Checking", release_version)

    for subdir, dirs, files in os.walk(os.path.abspath(release_version)):
        for file in files:
            # Only check .assert files
            if not file.endswith(".assert"):
                continue

            filepath = os.path.abspath(os.path.join(subdir, file))
            # Don't bother checking the same file we've pulled
            if assert_filepath == filepath:
                continue

            with open(filepath, 'r') as assert_file:
                for line in assert_file.readlines():
                    line = line.strip()

                    if line.startswith("-") or "bitcoin" not in line:
                        continue

                    try:
                        digest, file_name = line.split()
                    except:
                        continue
                    
                    if file_name in digests and digests[file_name] != digest:
                        print("Mismatch between", assert_filepath, "and", filepath, "for", file_name, ":", digests[file_name], "!=", digest)
                        sys.exit(1)

sys.exit(0)
