#!/usr/bin/env python

"""Get the list of photos for each FMSS ID and save it as a JSON object"""

__author__ = "Regan Sarwas, GIS Team, Alaska Region, National Park Service"
__email__ = "regan_sarwas@nps.gov"
__copyright__ = "Public Domain - product of the US Government"

import sys
import os.path
import csv

# dependency pyodbc
# pip install pyodbc

try:
    import pyodbc
except ImportError:
    pyodbc = None
    pydir = os.path.dirname(sys.executable)
    print 'pyodbc module not found, make sure it is installed with'
    print pydir + r'\Scripts\pip.exe install pyodbc'
    print 'Don''t have pip?'
    print 'Download <https://bootstrap.pypa.io/get-pip.py> to ' + pydir + r'\Scripts\get-pip.py'
    print 'Then run'
    print sys.executable + ' ' + pydir + r'\Scripts\get-pip.py'
    sys.exit()


def get_connection_or_die():
    conn_string = ("DRIVER={{SQL Server Native Client 11.0}};"
                   "SERVER={0};DATABASE={1};Trusted_Connection=Yes;")
    conn_string = conn_string.format('inpakrovmais', 'akr_facility2')
    try:
        connection = pyodbc.connect(conn_string)
        return connection
    except pyodbc.Error:
        # Try to alternative connection string for 2008
        conn_string2 = conn_string.replace('SQL Server Native Client 11.0', 'SQL Server Native Client 10.0')
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
        rows = connection.cursor().execute("""
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
	  WHERE P.ISEXTANT = 'True' AND (P.FACLOCID IS NOT NULL OR (P.ISOUTPARK <> 'Yes' AND P.FACMAINTAIN IN ('NPS','FEDERAL')))
                """).fetchall()
    except pyodbc.Error as de:
        print ("Database error ocurred", de)
        rows = None
    return rows


def write_building_csv(filename, rows):
    with open(filename, 'wb') as f:
        f.write("Latitude,Longitude,FMSS_Id,Desc,Cost,Size,Status,Year,Occupant,Name,Park_Id,Photo_Id\n")
        csv_writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
        for row in rows:
            csv_writer.writerow([unicode(x).encode('utf8') for x in row])


if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    outfile = os.path.join(script_dir, 'buildings.csv')
    conn = get_connection_or_die()
    data = get_building_data(conn)
    if data:
        write_building_csv(outfile, data)
