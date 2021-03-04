# -*- coding: utf-8 -*-
"""
Writes the list of photos found in the filesystem to a database table.

The database table will have the following columns:

Folder, Filename, Lat, Lon, Bytes, Gpsdate, Exifdate, Filedate

Filename - the filename of the photo (any file with a `.jpg` extension)
Folder - the sub folder under `Config.photo_dir` containing the photo
Exifdate - the date the photo was taken as encoded in the EXIF data
Lat - the latitude of the photo location as encoded in the EXIF data
Lon - the longitude of the photo location as encoded in the EXIF data
Gpsdate - the date (in UTC) the photo was taken as encoded in the EXIF data
Bytes - the size (in bytes) of the photo file
Filedate - the file systems last modified date for the photo file

CAUTION:
Currently only Filename and Folder are populated.  See `make_photo_list.py`
for a tool that creates a CSV file with the other attributes.

Written for Python 2.7; may work with Python 3.x.

Third party requirements:
* pyodbc - https://pypi.python.org/pypi/pyodbc
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import os
import sys

import pyodbc


class Config(object):
    """Namespace for configuration parameters. Edit as needed."""

    # pylint: disable=useless-object-inheritance,too-few-public-methods

    # Photo_dir - the absolute path to the folder to search for photo files.
    # Assumes all photos are in sub folders of photo_dir only one level deep.
    # and that there are no photos in photo_dir.
    photo_dir = r"T:\PROJECTS\AKR\FMSS\PHOTOS\ORIGINAL"

    # Table - the name of the table to create for the photo records
    table = "Photos_In_Filesystem"

    # Database - the the name of the database in which to create the table
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


def make_table(connection):
    """Execute SQL in connection to create a new photos table if it does not exist."""
    sql = """
        IF NOT (EXISTS (SELECT *
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_NAME = '{0}'))
        BEGIN
          CREATE TABLE {0}
          (Folder nvarchar(max), Filename nvarchar(max), Lat float, Lon float, Bytes int,
          Gpsdate datetime2, Exifdate datetime2, Filedate datetime2)
        END
    """
    sql = sql.format(Config.table)
    return execute_sql(connection, sql)


def clear_table(connection):
    """Execute SQL in connection to clear the photos table."""
    sql = "DELETE FROM {0}"
    sql = sql.format(Config.table)
    return execute_sql(connection, sql)


def execute_sql(connection, sql):
    """Execute sql in the database connection."""
    wcursor = connection.cursor()
    wcursor.execute(sql)
    try:
        wcursor.commit()
    except pyodbc.Error as ex:
        return "Database error:\n{0}\n{1}\n{2}".format(sql, connection, ex)
    return None


def write_photos(connection, photos):
    """Execute SQL in connection to add the list of photos to the photos table."""
    wcursor = connection.cursor()
    if photos and len(photos[0]) == 2:
        for photo in photos:
            if len(photo) == 2:
                # (folder,file) tuple
                sql = "INSERT [Photos_In_Filesystem] (Folder, Filename) values ('{0}','{1}')"
                sql = sql.format(*photo)
            else:
                # dictionary of values for each photo
                sql = """
    INSERT [Photos_In_Filesystem]
    (Folder, Filename, Lat, Lon, Bytes, Gpsdate, Exifdate, Filedate) values
    ('{folder}','{file}', {lat}, {lon}, {bytes}, '{gpsdate}', '{exifdate}', '{filedate}')
                """
                sql = sql.format(**photo)
            # print(sql)
            wcursor.execute(sql)
    try:
        wcursor.commit()
    except pyodbc.Error as ex:
        msg = "Database error inserting into 'Photos_In_Filesystem'\n{0}\n{1}"
        return msg.format(connection, ex)
    return None


def files_for_folders(root):
    """
    Get the files in the folders below root
    :param root: The full path of the folder to search
    :return: A dictionary of the folders in root with a list of files for each folder.
    All paths are relative to root.
    """
    files = {}
    for folder in [f for f in os.listdir(root) if os.path.isdir(os.path.join(root, f))]:
        print(folder, end="")
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


def is_image(name):
    """Return True if the file at name is a image file."""
    ext = os.path.splitext(name)[1].lower()
    return ext in [".jpg", ".jpeg", ".png", ".gif"]


def is_jpeg(name):
    """Return True if the file at name is a photo file."""
    ext = os.path.splitext(name)[1].lower()
    return ext in [".jpg", ".jpeg"]


def main():
    """Read photos in file system and write them to the database."""
    conn = get_connection_or_die(Config.server, Config.database)
    make_table(conn)
    clear_table(conn)
    folder = Config.photo_dir
    photo_list = [t for t in folder_file_tuples(folder) if is_jpeg(t[1])]
    write_photos(conn, photo_list)


if __name__ == "__main__":
    main()
