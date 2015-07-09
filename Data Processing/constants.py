"""This file is intended to capture the database location and schema
in a single location for all the python scripts"""

import os.path

data_root = r"C:\tmp\Buildings"
gdb = os.path.join(data_root, "AKR_2015_01_08_15_13_56_00.gdb")

bldg_table = os.path.join(gdb, "Building")
link_table = os.path.join(gdb, "Building_Link")
point_fc = os.path.join(gdb, "Building_Point")
poly_fc = os.path.join(gdb, "Building_Polygon")
allowable_dups = os.path.join(gdb, "Well_Known_Duplicates")
accepted_link_issues = os.path.join(gdb, "Accepted_Link_Issues")

fmss_table = os.path.join(gdb, "FMSSExport62")
lcs_table = os.path.join(gdb, "LCSExport")

bldg_pk_name = "Building_ID"
fmss_fk_name = "FMSS_ID"
fmss_pk_name = "Location"
lcs_fk_name = "LCS_ID"
lcs_pk_name = lcs_fk_name
park_pk_name = "Park_ID"
geometry_id = "Geometry_ID"

point_types = {'Center': 0, 'Boundary': 1, 'Entrance': 2, 'Photo': 3,
               'Other': 4, 'Obscured': 5, 'Elevation': 6}
poly_types = {'Perimeter': 0, 'Envelope': 1, 'Buffer': 2, 'Obscured': 3}

gps_export = os.path.join(data_root, "GPS Issues.csv")
no_gis_export = os.path.join(data_root, "FMSS_no_GIS.csv")
no_fmss_export = os.path.join(data_root, "GIS_no_FMSS.csv")
bad_fmss_export = os.path.join(data_root, "bad_FMSS.csv")

location_export = os.path.join(data_root, "BuildingLocations.csv")

photo_root = r"T:\PROJECTS\AKR\Buildings\PhotosFromAllYears-Geotagged\2014Reprocess"
photo_csv = os.path.join(photo_root, "MasterPhotoListCopy.csv")
