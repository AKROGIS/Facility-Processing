# -*- coding: utf-8 -*-
"""
Add the photos from a CSV file to a versioned table in a SDE database.

A very specific format for the CSV file is expected.
Review/Edit the Config parameters before executing.

For editing of SQL Server SDE data without ArcGIS see
http://desktop.arcgis.com/en/arcmap/latest/manage-data/using-sql-with-gdbs/edit-versioned-data-using-sql-sqlserver.htm

Note that database errors are expected.
This is a strange interaction between pyodbc and SDE.
Everything works as expected despite the errors.  Example follows:

Database error:
  EXEC sde.create_version 'sde.DEFAULT',
       'photo_update_20181211', 1, 2, 'For auto upload of new photos';
  ('25000', u'[25000] [Microsoft][ODBC Driver 13 for SQL Server][SQL Server]Transaction
   count after EXECUTE indicates a mismatching number of BEGIN and COMMIT statements.
   Previous count = 1, current count = 0. (266) (SQLExecDirectW)')
Database error:
  EXEC dbo.Calc_Attachments 'DBO.photo_update_20181211';
  ('25000', u'[25000] [Microsoft][ODBC Driver 13 for SQL Server][SQL Server]Transaction
   count after EXECUTE indicates a mismatching number of BEGIN and COMMIT statements.
   Previous count = 1, current count = 0. (266) (SQLExecDirectW); [25000]
   [Microsoft][ODBC Driver 13 for SQL Server][SQL Server]Transaction count
   after EXECUTE indicates a mismatching number of BEGIN and COMMIT statements.
   Previous count = 1, current count = 0. (266)')

Written for Python 2.7; may work with Python 3.x.

Third party requirements:
* pyodbc - https://pypi.python.org/pypi/pyodbc
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import csv
import datetime
import sys

import pyodbc

import csv23


class Config(object):
    """Namespace for configuration parameters. Edit as needed."""

    # pylint: disable=useless-object-inheritance,too-few-public-methods

    # CSV Path - The path to the CSV file with photo names and folders.
    csv_path = r"T:\PROJECTS\AKR\FMSS\PHOTOS\PhotoCSVLoader.csv"

    # Unit index - the column index in `csv_path` for the park unitcode.
    # It is also part of the URL path to the file
    unit_index = 0

    # Folder index - the column index in `csv_path` for the optional
    # sub folder path below `csv[unit_index]`
    folder_index = 1

    # Name index - the column index in `csv_path` for the photo name
    # in `root_folder/csv[unit_index]/csv[folder_index]`.
    name_index = 2

    # Create user index - the column index in `csv_path` for the name
    # of the user in who created the photo record.
    # Value defaults to `default_create_user`
    create_user_index = 10

    # Create date index - the column index in `csv_path` for the date
    # that the photo record was created. Value defaults to today.
    create_date_index = 11

    # Default create user - The default database value if no create user is
    # provided.
    default_create_user = "AKRO_GIS"

    # Root URL - the start of the permanent address if the photo.
    # `csv[unit_index]/csv[folder_index]/csv[name_index]` is appended.
    root_url = "https://akrgis.nps.gov/fmss/photos/web/"

    # Insert query - A database query to produce a single photo record.
    # The {number}s coorespond to columns in `csv_path`, where {0} is
    # the generated URL to the photo, and the other columns start with 1.
    # Code assumes all columns are be either strings or NULL
    insert_query = """
        INSERT gis.AKR_ATTACH_evw
        (ATCHLINK, UNITCODE, ATCHALTNAME, ATCHDATE, FACLOCID, FACASSETID, FEATUREID,
        GEOMETRYID, ATCHNAME, ATCHSOURCE, CREATEUSER, CREATEDATE, NOTES)
        VALUES ('{0}', {1}, {3}, {4}, {5}, {6}, {7}, {8}, {9}, {10}, {11}, {12}, {13});
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


def read_csv(csv_path):
    """Read the list of photos from csv_path."""
    rows = []
    with csv23.open(csv_path, "r") as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)  # skip the header
        for row in csv_reader:
            row = csv23.fix(row)
            rows.append(row)
    return rows


def fix_photos(photos):
    """Fix the list of photos to match database formats."""
    today = datetime.date.today().isoformat()
    for photo in photos:
        if not photo[Config.create_user_index]:
            photo[Config.create_user_index] = Config.default_create_user
        if not photo[Config.create_date_index]:
            photo[Config.create_date_index] = today
    return photos


def make_new_version(conn):
    """Create a new named SDE version in conn.

    SDE will automatically make sure the name is unique (with 1 as the 3rd param)
    need to query the versions to get the owner name as well as the final name.
    """
    today = datetime.date.today()
    name = "photo_update_{0}{1:02d}{2:02d}".format(today.year, today.month, today.day)
    # 3rd param: 1 for uniquify, 2 to use name as given (may error).
    # 4th param: 0 for private, 1 for public, or 2 for protected.
    sql = """
        EXEC sde.create_version
             'sde.DEFAULT', '{0}', 1, 2, 'For auto upload of new photos';
    """
    sql = sql.format(name)
    execute_sql(conn, sql)
    # Note that the uniquify has been throwing an error but still succeeded.
    # Since the name may have been altered, find the new name
    row = None
    sql = """
          SELECT TOP 1 owner, name
            FROM sde.SDE_versions
           WHERE name LIKE '{0}%'
        ORDER BY creation_time desc
    """
    sql = sql.format(name)
    try:
        row = conn.cursor().execute(sql).fetchone()
    except pyodbc.Error as ex:
        err = "Database error:\n{0}\n{1}".format(sql, ex)
        print(err)
    if row and len(row) == 2:
        return "{0}.{1}".format(*row)
    print("Unexpected database response to query for version name")
    print(row)
    return None


def write_photos(connection, version, photos):
    """Execute SQL in connection to add photos to the SDE version."""
    sql = None
    try:
        with connection.cursor() as wcursor:
            sql = "EXEC sde.set_current_version '{0}';".format(version)
            wcursor.execute(sql)
            sql = "EXEC sde.edit_version '{0}', 1;".format(version)  # Start editing
            wcursor.execute(sql)
            # UNITCODE,FOLDER,FILENAME,TIMESTAMP,FACLOCID,FACASSETID,FEATUREID,
            # GEOMETRYID,DESCRIPTION,ORIGINALPATH,CREATEUSER,CREATEDATE,NOTES
            for photo in photos:
                unit_folder = photo[Config.unit_index]
                sub_folder = photo[Config.folder_index]
                name = photo[Config.name_index]
                if sub_folder:
                    link = "{0}/{1}/{2}/{3}".format(
                        Config.root_url, unit_folder, sub_folder, name
                    )
                else:
                    link = "{0}/{1}/{2}".format(Config.root_url, unit_folder, name)
                photo_db = ["'{0}'".format(i) if i else "NULL" for i in photo]
                sql = Config.insert_query.format(link, *photo_db)
                wcursor.execute(sql)
            # Do automated calcs
            sql = "EXEC dbo.Calc_Attachments '{0}';".format(version)
            wcursor.execute(sql)
            sql = "EXEC sde.edit_version '{0}', 2;".format(version)  # Stop editing
            wcursor.execute(sql)
    except pyodbc.Error as ex:
        err = "Database error:\n{0}\n{1}".format(sql, ex)
        print(err)
        return err
    return None


def execute_sql(connection, sql):
    """Execute sql in the database connection."""
    try:
        with connection.cursor() as wcursor:
            wcursor.execute(sql)
    except pyodbc.Error as ex:
        err = "Database error:\n{0}\n{1}".format(sql, ex)
        print(err)
        return err
    return None


def main():
    """Add Photos in CSV to the database."""

    new_photos = read_csv(Config.csv_path)
    if not new_photos:
        print("There are no photos to add")
        sys.exit()
    conn = get_connection_or_die(Config.server, Config.database)
    version = make_new_version(conn)
    photos = fix_photos(new_photos)
    write_photos(conn, version, photos)


if __name__ == "__main__":
    main()
