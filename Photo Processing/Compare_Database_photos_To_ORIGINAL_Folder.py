# -*- coding: utf-8 -*-
"""
Compares the list of photos in database + CSV file with the filesystem.

File paths are hard coded in the script relative to the scipt's location.
The database connection string and schema are also hardcoded in the script.

Written for Python 2.7 and 3.6.

Third party requirements:
* pyodbc - https://pypi.python.org/pypi/pyodbc
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import csv
import os
import sys

import pyodbc

import csv23


def get_connection_or_die(server, database):
    """
    Get a Trusted pyodbc connection to the SQL Server database on server.

    Try several connection strings.
    See https://github.com/mkleehammer/pyodbc/wiki/Connecting-to-SQL-Server-from-Windows

    Exit with an error message if there is no successful connection.
    """
    drivers = [
        "{ODBC Driver 17 for SQL Server}",  # supports SQL Server 2008 through 2017
        "{ODBC Driver 13.1 for SQL Server}",  # supports SQL Server 2008 through 2016
        "{ODBC Driver 13 for SQL Server}",  # supports SQL Server 2005 through 2016
        "{ODBC Driver 11 for SQL Server}",  # supports SQL Server 2005 through 2014
        "{SQL Server Native Client 11.0}",  # DEPRECATED: released with SQL Server 2012
        # '{SQL Server Native Client 10.0}',    # DEPRECATED: released with SQL Server 2008
    ]
    conn_template = "DRIVER={0};SERVER={1};DATABASE={2};Trusted_Connection=Yes;"
    for driver in drivers:
        conn_string = conn_template.format(driver, server, database)
        try:
            connection = pyodbc.connect(conn_string)
            return connection
        except pyodbc.Error:
            pass
    print("Rats!! Unable to connect to the database.")
    print("Make sure you have an ODBC driver installed for SQL Server")
    print("and your AD account has the proper DB permissions.")
    print("Contact akro_gis_helpdesk@nps.gov for assistance.")
    sys.exit()


def get_database_photos(connection):
    try:
        rows = (
            connection.cursor()
            .execute(
                """
            SELECT REPLACE(ATCHLINK, 'https://akrgis.nps.gov/fmss/photos/web/', '')
              FROM gis.AKR_ATTACH_evw
             WHERE ATCHTYPE = 'Photo'
               AND ATCHLINK LIKE 'https://akrgis.nps.gov/fmss/photos/web/%'
        """
            )
            .fetchall()
        )
    except pyodbc.Error as de:
        print("Database error ocurred", de)
        rows = None
    return rows


def files_for_folders(root):
    """
    Get the files in the folders below root
    :param root: The full path of the folder to search
    :return: A dictionary of the folders in root with a list of files for each folder.  All paths are relative to root.
    """
    files = {}
    for folder in [f for f in os.listdir(root) if os.path.isdir(os.path.join(root, f))]:
        print(folder, end=" ")
        path = os.path.join(root, folder)
        files[folder] = [
            f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))
        ]
    return files


def folder_file_tuples(root):
    """
    Get the (folder,file) info below root
    :param root: The full path of the folder to search
    :return: A list of (folder,file) pairs for each file in each folder below root.
    folder and file are names, not paths.
    """
    pairs = []
    folders = files_for_folders(root)
    for folder in folders:
        for name in folders[folder]:
            pairs.append((folder, name))
    return pairs


def photos_below(dir):
    dir = dir + "\\"
    results = []
    for root, dirs, files in os.walk(dir):
        relative_path = root.replace(dir, "")
        print(relative_path, end=" ")
        for filename in files:
            if is_image(filename):
                results.append(os.path.join(relative_path, filename))
    return results


def files_in_csv(csv_path):

    files = set()
    with csv23.open(csv_path, "r") as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)  # skip the header
        for row in csv_reader:
            row = csv23.fix(row)
            unit = row[0]
            folder = row[1]
            name = row[2]
            if folder:
                path = "{0}/{1}/{2}".format(unit, folder, name)
            else:
                path = "{0}/{1}".format(unit, name)
            files.add(path.lower())
    return files


def is_image(name):
    ext = os.path.splitext(name)[1].lower()
    return ext in [".jpg", ".jpeg", ".png", ".gif"]


def is_jpeg(name):
    ext = os.path.splitext(name)[1].lower()
    return ext in [".jpg", ".jpeg"]


if __name__ == "__main__":
    print("Reading database")
    conn = get_connection_or_die("inpakrovmais", "akr_facility2")
    # duplicate paths in the database are OK;
    #  two different features could be in the same photo
    # so we want to unique-ify the list of photo links
    db_photo_set = set([row[0].lower() for row in get_database_photos(conn)])
    print("Found {0} unique files in the Database.".format(len(db_photo_set)))

    csv_file = "PhotoCSVLoader.csv"
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Assumes script ia adjacent to the CSV list of new photos
    csv_path = os.path.join(script_dir, csv_file)
    print("\nReading {0}".format(csv_path))
    csv_photo_set = files_in_csv(csv_path)
    print("Found {0} unique files in the {1}.".format(len(csv_photo_set), csv_file))

    # Assumes script is in the Processing folder which is in the photos base folder.
    #   some/path/PHOTOS/PROCESSING/this_script.py
    #   some/path/PHOTOS/ORIGINAL/{park}/photos_files.jpg
    base_dir = os.path.dirname(script_dir)
    photo_dir = os.path.join(base_dir, "ORIGINAL")
    print("\nReading Folders in " + photo_dir)
    # photo_tuples = [t for t in folder_file_tuples(photo_dir) if is_jpeg(t[1])]
    # fs_photo_set = set([(t[0]+'/'+t[1]).lower() for t in photo_tuples])
    fs_photo_set = set([p.lower().replace("\\", "/") for p in photos_below(photo_dir)])
    print("\nFound {0} unique files in the Filesystem.".format(len(fs_photo_set)))
    print("")

    fs_not_db = fs_photo_set - db_photo_set - csv_photo_set
    db_not_fs = db_photo_set - fs_photo_set
    csv_not_fs = csv_photo_set - fs_photo_set
    if fs_not_db:
        print(
            "ERROR: The following {0} files are in the Filesystem but not the Database/CSV".format(
                len(fs_not_db)
            )
        )
        for i in sorted(list(fs_not_db)):
            print("  {0}".format(i))
    if db_not_fs:
        print(
            "ERROR: The following {0} files are in the Database but not the Filesystem".format(
                len(db_not_fs)
            )
        )
        for i in sorted(list(db_not_fs)):
            print("  {0}".format(i))
    if csv_not_fs:
        print(
            "ERROR: The following {0} files are in the CSV but not the Filesystem".format(
                len(csv_not_fs)
            )
        )
        for i in sorted(list(csv_not_fs)):
            print("  {0}".format(i))
    if not fs_not_db and not db_not_fs and not csv_not_fs:
        print("Woot, Woot, No issues found.")
