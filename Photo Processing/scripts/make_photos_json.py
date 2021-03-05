# -*- coding: utf-8 -*-
"""
Create a JSON file with a list of relative photo URLS for each feature ID in a database.

Review/Edit the Config parameters before executing.

Written for Python 2.7; may work with Python 3.x.

Third party requirements:
* pyodbc - https://pypi.python.org/pypi/pyodbc
"""

from __future__ import absolute_import, division, print_function, unicode_literals

from io import open
import json
import sys

import pyodbc


class Config(object):
    """Namespace for configuration parameters. Edit as needed."""

    # pylint: disable=useless-object-inheritance,too-few-public-methods

    # JSON path - the path to the JSON file to create.
    # This should be the same as the path in `update_photos_on_server.bat`
    json_path = r"T:\PROJECTS\AKR\FMSS\PHOTOS\PROCESSING\scripts\photos.json"

    # Photo query - A database query to produce a (id, URL) record for
    # each photo.
    # FIXME - This query only returns one ID for each photo
    #   some photos have multiple IDs (some buildings and building assets
    #   have FMSS ID(s) and a FEATUREID)
    photo_query = """
        SELECT COALESCE(FACLOCID,
                        COALESCE(FEATUREID,
                                 COALESCE(FACASSETID, GEOMETRYID))) AS id,
               REPLACE(ATCHLINK, 'https://akrgis.nps.gov/fmss/photos/web/', '') AS photo
          FROM gis.AKR_ATTACH_evw
         WHERE ATCHALTNAME IS NOT NULL AND (FACLOCID IS NOT NULL
            OR FACASSETID IS NOT NULL OR FEATUREID IS NOT NULL
            OR GEOMETRYID IS NOT NULL)
      ORDER BY id, ATCHDATE DESC
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


def get_photo_data(connection):
    """Get a association list (id, url) of photos from connection."""
    photos = {}
    try:
        rows = connection.cursor().execute(Config.photo_query).fetchall()
    except pyodbc.Error as ex:
        print("Database error ocurred", ex)
        rows = None
    if rows:
        for row in rows:
            if row.id in photos:
                photos[row.id].append(row.photo)
            else:
                photos[row.id] = [row.photo]
    return photos


def main():
    """Get data from the database and save as a JSON file."""
    conn = get_connection_or_die(Config.server, Config.database)
    data = get_photo_data(conn)
    with open(Config.json_path, "w", encoding="utf-8") as out_file:
        out_file.write(json.dumps(data, indent=2, separators=(",", ": ")))


if __name__ == "__main__":
    main()
