# -*- coding: utf-8 -*-
"""
Writes the list of photos found in the filesystem to a database table.

File paths are hard coded in the script relative to the scipt's location.
The database connection string and schema are also hardcoded in the script.

Written for Python 2.7; may work with Python 3.x.

Third party requirements:
* pyodbc - https://pypi.python.org/pypi/pyodbc
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import os
import sys

import pyodbc


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
    sql = (
        "IF NOT (EXISTS (SELECT * "
        "FROM INFORMATION_SCHEMA.TABLES "
        "WHERE TABLE_NAME = 'Photos_In_Filesystem'))"
        "BEGIN"
        "  CREATE TABLE [Photos_In_Filesystem] "
        "  (Folder nvarchar(max), Filename nvarchar(max), Lat float, Lon float, Bytes int, "
        "  Gpsdate datetime2, Exifdate datetime2, Filedate datetime2)"
        "END"
    )
    return execute_sql(connection, sql)


def clear_table(connection):
    sql = "DELETE FROM [Photos_In_Filesystem] "
    return execute_sql(connection, sql)


def execute_sql(connection, sql):
    wcursor = connection.cursor()
    wcursor.execute(sql)
    try:
        wcursor.commit()
    except pyodbc.Error as de:
        return "Database error:\n{0}\n{1}\n{1}".format(sql, connection, de)
    return None


def write_photos(connection, photos):
    wcursor = connection.cursor()
    if photos and len(photos[0]) == 2:
        for photo in photos:
            if len(photo) == 2:
                # (folder,file) tuple
                sql = "INSERT [Photos_In_Filesystem] (Folder, Filename) values ('{0}','{1}')"
                sql = sql.format(*photo)
            else:
                # dictionary of values for each photo
                sql = (
                    "INSERT [Photos_In_Filesystem] "
                    "(Folder, Filename, Lat, Lon, Bytes, Gpsdate, Exifdate, Filedate) values "
                    "('{folder}','{file}', {lat}, {lon}, {bytes}, '{gpsdate}', '{exifdate}', '{filedate}')"
                )
                sql = sql.format(**photo)
            # print(sql)
            wcursor.execute(sql)
    try:
        wcursor.commit()
    except pyodbc.Error as de:
        msg = "Database error inserting into 'Photos_In_Filesystem'\n{0}\n{1}"
        return msg.format(connection, de)
    return None


def files_for_folders(root):
    """
    Get the files in the folders below root
    :param root: The full path of the folder to search
    :return: A dictionary of the folders in root with a list of files for each folder.  All paths are relative to root.
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
    ext = os.path.splitext(name)[1].lower()
    return ext in [".jpg", ".jpeg", ".png", ".gif"]


def is_jpeg(name):
    ext = os.path.splitext(name)[1].lower()
    return ext in [".jpg", ".jpeg"]


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Assumes script is in the Processing folder which is sub to the photos base folder.
    base_dir = os.path.dirname(script_dir)
    photo_dir = os.path.join(base_dir, "ORIGINAL")
    conn = get_connection_or_die("inpakrovmais", "akr_facility2")
    make_table(conn)
    clear_table(conn)
    photo_list = [t for t in folder_file_tuples(photo_dir) if is_jpeg(t[1])]
    write_photos(conn, photo_list)
