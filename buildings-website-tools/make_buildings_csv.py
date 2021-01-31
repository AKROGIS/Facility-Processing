# -*- coding: utf-8 -*-
"""
Get the building records from the database and export as a CSV file.

File paths are hard coded in the script relative to the scipt's location.
The database connection string and schema are also hardcoded in the script.

Written for Python 2.7; will NOT work with Python 3.x.

Third party requirements:
* pyodbc - https://pypi.python.org/pypi/pyodbc
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import csv
from io import open
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


def get_building_data(connection):
    try:
        rows = (
            connection.cursor()
            .execute(
                """
 	 SELECT P.Shape.STY AS Latitude,  P.Shape.STX AS Longitude, P.FACLOCID as FMSS_Id,
	        COALESCE(F.[Description], P.MAPLABEL) AS [Desc],
	        COALESCE(FORMAT(CAST(F.CRV AS float), 'C', 'en-us'), 'unknown') AS Cost,
--			COALESCE(FORMAT(F.Qty, '0,0 Sq Ft', 'en-us'), 'unknown') AS Size, F.[Status] AS [Status],
			'unknown' AS Size, P.BLDGSTATUS AS [Status],
			COALESCE(CAST(F.YearBlt AS nvarchar), 'unknown') AS [Year], P.FACOCCUPANT AS Occupant,
			P.BLDGNAME AS [Name], P.PARKBLDGID AS Park_Id,
            COALESCE(FACLOCID, COALESCE(FEATUREID, COALESCE(FACASSETID, GEOMETRYID))) AS Photo_Id
       FROM gis.AKR_BLDG_CENTER_PT_evw as P
  LEFT JOIN dbo.FMSSEXPORT as F
         ON P.FACLOCID = F.Location
	  WHERE P.ISEXTANT = 'True' AND (P.FACLOCID IS NOT NULL
         OR (P.ISOUTPARK <> 'Yes' AND P.FACMAINTAIN IN ('NPS','FEDERAL')))
                """
            )
            .fetchall()
        )
    except pyodbc.Error as de:
        print("Database error ocurred", de)
        rows = None
    return rows


# pylint: disable=redefined-builtin
def csv23_open(filename, mode="r"):
    """
    Open a file for CSV mode in a Python 2 and 3 compatible way.

    mode must be one of "r" for reading or "w" for writing.
    """

    if sys.version_info[0] < 3:
        return open(filename, mode + "b")
    return open(filename, mode, encoding="utf-8", newline="")


def cvs23_write(writer, row):
    """
    Write a row to a csv writer.

    writer is a csv.writer, and row is a list of unicode or number objects.
    """

    if sys.version_info[0] < 3:
        # Ignore the pylint error that unicode is undefined in Python 3
        # pylint: disable=undefined-variable

        writer.writerow(
            [
                item.encode("utf-8") if isinstance(item, unicode) else item
                for item in row
            ]
        )
    else:
        writer.writerow(row)


def write_building_csv(csv_path, rows):
    header = [
        "Latitude",
        "Longitude",
        "FMSS_Id",
        "Desc",
        "Cost",
        "Size",
        "Status",
        "Year",
        "Occupant",
        "Name",
        "Park_Id",
        "Photo_Id",
    ]
    with csv23_open(csv_path, "w") as csv_file:
        csv_writer = csv.writer(csv_file)
        cvs23_write(csv_writer, header)
        for row in rows:
            cvs23_write(csv_writer, row)


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    outfile = os.path.join(script_dir, "buildings.csv")
    conn = get_connection_or_die("inpakrovmais", "akr_facility2")
    data = get_building_data(conn)
    if data:
        write_building_csv(outfile, data)
