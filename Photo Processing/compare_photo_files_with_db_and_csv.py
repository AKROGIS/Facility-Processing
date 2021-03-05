# -*- coding: utf-8 -*-
"""
Compares the list of photos in database + CSV file with the filesystem.

Review/Edit the Config parameters before executing.

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


class Config(object):
    """Namespace for configuration parameters. Edit as needed."""

    # pylint: disable=useless-object-inheritance,too-few-public-methods

    # Root folder - the common prefix for the `csv_path` and `photo_folder`
    # optional if you choose to provide a absolute path for both paths.
    root_folder = r"T:\PROJECTS\AKR\FMSS\PHOTOS"

    # Photo folder - the absolute path prefix for location of photo folders
    # and photo files.  Photos can be in the photo_folder or in sub folders
    # to any depth.
    photo_folder = os.path.join(root_folder, "ORIGINAL")

    # The path to the CSV file with photo names and folders.
    csv_path = os.path.join(root_folder, "PhotoCSVLoader.csv")

    # Unit index - the column index in `csv_path` for the first sub folder
    # in `root_folder`. Can be None if not used in CSV
    unit_index = 0

    # Folder index - the column index in `csv_path` for the sub folder path
    # below `root_folder/csv[unit_index]`. Can be None if not used in CSV
    folder_index = 1

    # Name index - the column index in `csv_path` for the photo name
    # in `root_folder/csv[unit_index]/csv[folder_index]`.
    name_index = 2

    # Photo query - A database query to produce a single column of relative
    # photo paths.
    photo_query = """
        SELECT REPLACE(ATCHLINK, 'https://akrgis.nps.gov/fmss/photos/web/', '')
          FROM gis.AKR_ATTACH_evw
         WHERE ATCHTYPE = 'Photo'
           AND ATCHLINK LIKE 'https://akrgis.nps.gov/fmss/photos/web/%'
    """

    # Database - the the name of the database in which to run the query
    database = "akr_facility2"

    # Server - the name of the server which has the database
    server = "inpakrovmais"


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
    """Return a set of standardized relative paths from the database connection."""
    try:
        rows = connection.cursor().execute(Config.photo_query).fetchall()
    except pyodbc.Error as ex:
        print("Database error ocurred", ex)
        rows = []

    paths = [standardize(path) for path in rows]
    return set(paths)


def photos_below(folder):
    """Return a set of standardized relative paths to photos below folder."""
    folder += os.pathsep
    paths = set()
    for root, _, files in os.walk(folder):
        relative_path = root.replace(folder, "")
        print(relative_path, end=" ")
        for filename in files:
            if is_image(filename):
                path = os.path.join(relative_path, filename)
                path = standardize(path)
                paths.add(path)
    return paths


def files_in_csv(csv_path):
    """Return a set of standardized relative paths to photos in the file at csv_path."""
    paths = set()
    with csv23.open(csv_path, "r") as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)  # skip the header
        for row in csv_reader:
            row = csv23.fix(row)
            path = row[Config.name_index]
            if Config.folder_index is not None:
                folder = row[Config.folder_index]
                path = os.path.join(folder, path)
            if Config.unit_index is not None:
                folder = row[Config.unit_index]
                path = os.path.join(folder, path)
            path = standardize(path)
            paths.add(path)
    return paths


def standardize(path):
    """Returns a standardized path."""
    return path.replace("\\", "/").lower()


def is_image(name):
    """Return True if the file at name is a image file."""
    ext = os.path.splitext(name)[1].lower()
    return ext in [".jpg", ".jpeg", ".png", ".gif"]


def compare(conn, csv_path, photo_dir):
    """Read the database plus CSV file and compare with filesystem."""

    print("Reading database")
    db_photo_set = get_database_photos(conn)
    print("Found {0} unique files in the Database.".format(len(db_photo_set)))

    print("\nReading {0}".format(csv_path))
    csv_photo_set = files_in_csv(csv_path)
    csv_file = os.path.basename(csv_path)
    print("Found {0} unique files in the {1}.".format(len(csv_photo_set), csv_file))

    print("\nReading Folders in " + photo_dir)
    fs_photo_set = photos_below(photo_dir)
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


def main():
    """Get the paths and connections and then compare."""
    conn = get_connection_or_die(Config.server, Config.database)
    compare(conn, Config.csv_path, Config.photo_folder)


if __name__ == "__main__":
    main()
