"""This script creates a csv file combining the GIS and FMSS data to drive the
  buidings website

This script has a lot of knowledge about the schema of the Buildings data, and
  will fail if schema changes.  Some of the schema is maintained in
  the adjacent constants.py"""

import constants

import os
import os.path
import csv

import arcpy

# must start with the point_fc because of the 1-M relationship
# get only the existing non-sensitive centers
where = "Point_Type = 0"
# where = "Point_Type = 0 AND Is_Extant = 'Y' AND Is_Sensitive = 'N'"
points = arcpy.MakeTableView_management(constants.point_fc, "view", where)

unit_rename = {
    'AKSO': 'AKRO',
    'AKLO': 'FAIR',
    'NOAT': 'WEAR',
    'KOVA': 'WEAR',
    'CAKR': 'WEAR',
}


def fixunit(unit):
    if unit in unit_rename:
        return unit_rename[unit]
    else:
        return unit


try:
    # join link table and fmss data
    view = arcpy.Describe(points).basename
    bldg = arcpy.Describe(constants.bldg_table).basename
    link = arcpy.Describe(constants.link_table).basename
    fmss = arcpy.Describe(constants.fmss_table).basename
    key1 = constants.bldg_pk_name
    key2 = key1
    arcpy.AddJoin_management(points, key1, constants.bldg_table, key2)
    key1 = view + "." + constants.bldg_pk_name
    key2 = constants.bldg_pk_name
    arcpy.AddJoin_management(points, key1, constants.link_table, key2)
    key1 = link + "." + constants.fmss_fk_name
    key2 = constants.fmss_pk_name
    arcpy.AddJoin_management(points, key1, constants.fmss_table, key2)

    field_names_in = ["SHAPE@Y", "SHAPE@X", bldg + ".Unit_Code", key1,
                      link + ".Park_ID",
                      bldg + ".Common_Name", fmss + ".Description",
                      fmss + ".BLDGTYPE", fmss + ".Status",
                      fmss + ".Occupant", fmss + ".CRV", fmss + ".Qty",
                      fmss + ".Acquisition_Date"]
    field_names_out = ["Lat", "Long", "Unit", "FMSS_Id", "Park_Id", "Name",
                       "Description",
                       "Type", "Status", "Occupant", "Value", "Size", "Date"]

    # write output to csv in current working directory
    out_file = os.path.join(os.getcwd(), constants.location_export)
    if arcpy.Exists(out_file):
        arcpy.Delete_management(out_file)
    with open(out_file, 'wb') as f:
        writer = csv.writer(f)
        writer.writerow(field_names_out)
        with arcpy.da.SearchCursor(points, field_names_in) as cursor:
            for row in cursor:
                if row[2]:  # only write out buildings in a unit
                    # row is a tuple, not a list
                    new_row = row[:2] + (fixunit(row[2]),) + row[3:]
                    writer.writerow(new_row)

finally:
    # cleanup
    arcpy.Delete_management(points)
