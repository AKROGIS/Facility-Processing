# -*- coding: utf-8 -*-
"""
Looks for all files in a CSV file that are not in the filesystem.

File paths are hard coded in the script and relative to the current working directory.

Written for Python 2.7; may work with Python 3.x.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import csv
import os.path

import csv23


class Config(object):
    """Namespace for configuration parameters. Edit as needed."""

    # pylint: disable=useless-object-inheritance,too-few-public-methods

    # If False, the script will get the two objects to compare from the command line.
    csv_path = r"T:\PROJECTS\AKR\FMSS\PHOTOS\PROCESSING\PhotoCSVLoader.csv"

    # Path root - the absolute path prexix for the data in the CSV
    # can be NULL and then the path in the CSV is either absolute or relative.
    path_root = r'T:\PROJECTS\AKR\FMSS\PHOTOS\ORIGINAL'

    # Folder index - the column index in the CSV file that has the folder path
    folder_index = 6

    # Name index - the column index in the CSV file that has the file name
    name_index = 1


def check_paths(csv_path):
    """Check that the paths in csv_path exist in the filesystem."""
    line = 0
    missing_paths = []
    with csv23.open(csv_path, "r") as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            row = csv23.fix(row)
            line += 1
            if line == 1:
                # skipping the header
                continue
            name = row[Config.name_index]
            folder = row[Config.folder_index]
            if not name or not folder:
                print("Bad record at line {0}".format(line))
                continue
            if path_root is None:
                path = os.path.join(folder, name)
            else:
                path = os.path.join(Config.path_root, folder, name)
            if not os.path.exists(path):
                missing_paths.append((path, line))
    for path, line in sorted(missing_paths):
        print("Path `{0}` not found at line {1}".format(path, line))


check_paths(Config.csv_path)
