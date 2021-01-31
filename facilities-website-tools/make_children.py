# -*- coding: utf-8 -*-

"""
Converts CSV data from the database into JSON files that the web app can load.

See `facilities.sql` for how to create the various input files.
File paths are hard coded in the script relative to the current working directory.

Written for Python 2.7; may work with Python 3.x.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import collections
import csv
from io import open
import json
import sys


# pylint: disable=redefined-builtin
def csv23_open(filename, mode="r"):
    """
    Open a file for CSV mode in a Python 2 and 3 compatible way.

    mode must be one of "r" for reading or "w" for writing.
    """

    if sys.version_info[0] < 3:
        return open(filename, mode + "b")
    return open(filename, mode, encoding="utf-8", newline="")


def csv23_fix(row):
    """Return a list of unicode strings from Python 2 or Python 3 strings."""

    if sys.version_info[0] < 3:
        return [item.decode("utf-8") for item in row]
    return row


def fix23(item):
    """Return a unicode string from a Python 2 or Python 3 string."""

    if sys.version_info[0] < 3:
        return item.decode("utf-8")
    return item


def main():
    """Create JSON files for web app"""

    with csv23_open("facilities.csv", "r") as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)  # remove header
        gis_loc_counts = collections.Counter([fix23(row[1]) for row in csv_reader])

    with csv23_open("assets.csv", "r") as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)  # remove header
        gis_asset_counts = collections.Counter([fix23(row[1]) for row in csv_reader])

    children = {}
    with csv23_open("parents.csv", "r") as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)  # remove header
        for row in [r for r in csv_reader if fix23(r[0]) in gis_loc_counts]:
            row = csv23_fix(row)
            parent = row[0]
            child = {"i": row[1], "d": row[2], "c": gis_loc_counts[row[1]]}
            if parent not in children:
                children[parent] = []
            children[parent].append(child)

    with open("children.json", "w", encoding="utf-8") as json_fh:
        json_fh.write(
            json.dumps(children, sort_keys=True, indent=2, separators=(",", ":"))
        )

    assets = {}
    with csv23_open("all_assets.csv", "r") as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)  # remove header
        for row in [r for r in csv_reader if fix23(r[0]) in gis_loc_counts]:
            row = csv23_fix(row)
            parent = row[0]
            child = {"i": row[1], "d": row[2], "c": gis_asset_counts[row[1]]}
            if parent not in assets:
                assets[parent] = []
            assets[parent].append(child)

    with open("assets.json", "w", encoding="utf-8") as json_fh:
        json_fh.write(
            json.dumps(assets, sort_keys=True, indent=2, separators=(",", ":"))
        )


if __name__ == "__main__":
    main()
