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


# dependency pyodbc
# pip install pyodbc

try:
    import pyodbc
except ImportError:
    module_missing("pyodbc")


def module_missing(name):
    """Prints details about missing 3rd party module (name) and exits."""

    print("Module {0} not found, make sure it is installed.".format(name))
    exec_dir = os.path.split(sys.executable)[0]
    pip = os.path.join(exec_dir, "Scripts", "pip")
    print("Install with: {0} install {1}".format(pip, name))
    print("Reference: https://pypi.python.org/pypi/{0}".format(name))
    sys.exit()


def get_connection_or_die():
    conn_string = (
        "DRIVER={{SQL Server Native Client 11.0}};"
        "SERVER={0};DATABASE={1};Trusted_Connection=Yes;"
    )
    conn_string = conn_string.format("inpakrovmais", "akr_facility2")
    try:
        connection = pyodbc.connect(conn_string)
        return connection
    except pyodbc.Error:
        # Try to alternative connection string for 2008
        conn_string2 = conn_string.replace(
            "SQL Server Native Client 11.0", "SQL Server Native Client 10.0"
        )
    try:
        connection = pyodbc.connect(conn_string)
        return connection
    except pyodbc.Error as e:
        # Additional alternatives are 'SQL Native Client' (2005) and 'SQL Server' (2000)
        print("Rats!!  Unable to connect to the database.")
        print("Make sure you have the SQL Server Client installed and")
        print("your AD account has the proper DB permissions.")
        print("Contact regan_sarwas@nps.gov for assistance.")
        print("  Connection: " + conn_string)
        print("         and: " + conn_string2)
        print("  Error: " + e[1])
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
    conn = get_connection_or_die()
    data = get_building_data(conn)
    if data:
        write_building_csv(outfile, data)
