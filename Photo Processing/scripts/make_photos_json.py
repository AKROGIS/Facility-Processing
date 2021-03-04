# -*- coding: utf-8 -*-
"""
Create a photos.json file which lists each photo in the database with a URL and foreign key.

File paths are hard coded in the script relative to the scipt's location.
The database connection string and schema are also hardcoded in the script.

Written for Python 2.7; may work with Python 3.x.

Third party requirements:
* pyodbc - https://pypi.python.org/pypi/pyodbc
"""

from __future__ import absolute_import, division, print_function, unicode_literals

from io import open
import json
import os.path
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


def get_photo_data(connection):
    """Get a association list (id, url) of photos from connection."""
    photos = {}
    try:
        # FIXME - This only returns one ID for each photo
        #   some photos have multiple IDs (some buildings and building assets
        #   have FMSS ID(s) and a FEATUREID)
        rows = (
            connection.cursor()
            .execute(
                """
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
            )
            .fetchall()
        )
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
    script_dir = os.path.dirname(os.path.abspath(__file__))
    outfile = os.path.join(script_dir, "photos.json")
    conn = get_connection_or_die("inpakrovmais", "akr_facility2")
    data = get_photo_data(conn)
    with open(outfile, "w", encoding="utf-8") as out_file:
        out_file.write(json.dumps(data, indent=2, separators=(",", ": ")))


if __name__ == "__main__":
    main()
