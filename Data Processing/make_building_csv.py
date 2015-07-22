#!/usr/bin/env python

"""Get the list of photos for each FMSS ID and save it as a JSON object"""

__author__ = "Regan Sarwas, GIS Team, Alaska Region, National Park Service"
__email__ = "regan_sarwas@nps.gov"
__copyright__ = "Public Domain - product of the US Government"

import sys
import os.path
import csv

# dependency pyodbc
# C:\Python27\ArcGIS10.3\Scripts\pip.exe install pyodbc

try:
    import pyodbc
except ImportError:
    pyodbc = None
    print 'pyodbc module not found, make sure it is installed with'
    print 'C:\Python27\ArcGIS10.3\Scripts\pip.exe install pyodbc'
    sys.exit()


def get_connection_or_die():
    conn_string = ("DRIVER={{SQL Server Native Client 10.0}};"
                   "SERVER={0};DATABASE={1};Trusted_Connection=Yes;")
    conn_string = conn_string.format('inpakrovmais', 'akr_facility')
    try:
        connection = pyodbc.connect(conn_string)
    except pyodbc.Error as e:
        print("Rats!!  Unable to connect to the database.")
        print("Make sure your AD account has the proper DB permissions.")
        print("Contact Regan (regan_sarwas@nps.gov) for assistance.")
        print("  Connection: " + conn_string)
        print("  Error: " + e[1])
        sys.exit()
    return connection


def get_building_data(connection):
    try:
        rows = connection.cursor().execute("""
             SELECT * FROM GIS.Existing_FMSS_Buildings_For_Website
                """).fetchall()
    except pyodbc.Error as de:
        print ("Database error ocurred", de)
        rows = None
    return rows


def write_building_csv(filename, rows):
    with open(filename, 'wb') as f:
        f.write("Latitude,Longitude,FMSS_Id,Desc,Cost,Size,Status,Year,Occupant,Name,Park_Id\n")
        csv_writer = csv.writer(f, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
        for row in rows:
            csv_writer.writerow(row)


if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    outfile = os.path.join(script_dir, 'buildings.csv')
    conn = get_connection_or_die()
    data = get_building_data(conn)
    if data:
        write_building_csv(outfile, data)


