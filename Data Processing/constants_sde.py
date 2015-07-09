"""This file is intended to capture the database location and schema
in a single location for all the python scripts"""

import os

try:
    data_root = os.path.dirname(os.path.realpath(__file__))
except NameError:
    data_root = r"C:\tmp\Buildings"

gdb = os.path.join(data_root, "facilities_as_domainuser.sde")

bldg_table = os.path.join(gdb, "akr_facility.GIS.Building")
link_table = os.path.join(gdb, "akr_facility.GIS.Building_Link")
point_fc = os.path.join(gdb, "akr_facility.GIS.Building_Point")
poly_fc = os.path.join(gdb, "akr_facility.GIS.Building_Polygon")
allowable_dups = os.path.join(gdb, "akr_facility.GIS.Building_QC_Well_Known_Duplicates")
accepted_link_issues = os.path.join(gdb, "akr_facility.GIS.Building_QC_Accepted_Link_Issues")

fmss_table = os.path.join(gdb, "akr_facility.GIS.FMSSExport")
lcs_table = os.path.join(gdb, "akr_facility.GIS.LCSExport")

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
