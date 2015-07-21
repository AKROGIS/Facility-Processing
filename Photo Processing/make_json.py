#!/usr/bin/env python

"""Get the list of photos for each FMSS ID and save it as a JSON object"""

__author__ = "Regan Sarwas, GIS Team, Alaska Region, National Park Service"
__email__ = "regan_sarwas@nps.gov"
__copyright__ = "Public Domain - product of the US Government"

import sys
import os.path
import json

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


def get_photo_data(connection):
    photos = {}
    try:
        rows = connection.cursor().execute("""
             SELECT P.Location_Id AS id, P.Unit + '/' + P.[Filename] AS photo
               FROM gis.Photos_evw as P
          LEFT JOIN gis.FMSSEXPORT as F
                 ON P.Asset_Code = F.Asset_Code AND P.Location_Id = F.Location -- AND P.Asset_Id AND F.Asset_ID
              WHERE P.Location_Id IS NOT NULL
           ORDER BY P.Location_Id, P.PhotoDate DESC
                """).fetchall()
    except pyodbc.Error as de:
        print ("Database error ocurred", de)
        rows = None
    if rows:
        for row in rows:
            if row.id in photos:
                photos[row.id].append(row.photo)
            else:
                photos[row.id] = [row.photo]
    return photos


if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    outfile = os.path.join(script_dir, 'photos.json')
    conn = get_connection_or_die()
    data = get_photo_data(conn)
    with open(outfile, 'w') as fh:
        fh.write(json.dumps(data, indent=2, separators=(',', ': ')))
