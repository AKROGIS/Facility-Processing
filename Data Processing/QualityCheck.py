import constants_sde as constants

import os.path
import numpy
import arcpy
import arcpy.da

def scratch_table():
    return arcpy.CreateScratchName("temp",
                                   data_type="Dataset",
                                   workspace=arcpy.env.scratchGDB)

def find_dups(table, key):
    count_table = scratch_table()
    items = []
    arcpy.Frequency_analysis(table, count_table, key)
    where = "FREQUENCY > 1"
    with arcpy.da.SearchCursor(count_table, key, where) as cursor:
        for row in cursor:
            item = row[0]
            if item:
                items.append(item)
    arcpy.Delete_management(count_table)
    return items

def find_dup_points(point_type):
    where = "Point_Type = " + str(point_type)
    table = arcpy.MakeTableView_management(constants.point_fc, "points", where)
    dups = find_dups(table, constants.bldg_pk_name)
    arcpy.Delete_management(table)
    return dups

def find_dup_polys(poly_type):
    where = "Polygon_Type = " + str(poly_type)
    table = arcpy.MakeTableView_management(constants.poly_fc, "polys", where)
    dups = find_dups(table, constants.bldg_pk_name)
    arcpy.Delete_management(table)
    return dups

def find_missing_links(table1, table2, key1, key2 = None):
    if not key2:
        key2 = key1
    table_view = arcpy.MakeTableView_management(table1, "view")
    view_name = arcpy.Describe(table_view).basename
    join_name = arcpy.Describe(table2).basename
    items = []
    arcpy.AddJoin_management(table_view, key1, table2, key2)
    fk = join_name + "." + key2
    pk = view_name + "." + key1
    where = fk + " IS NULL"
    with arcpy.da.SearchCursor(table_view, pk, where) as cursor:
        for row in cursor:
            item = row[0]
            if item:
                items.append(item)
    arcpy.Delete_management(table_view)
    return items
    
def nps_buildings_without_fmss():
    table1 = constants.bldg_table
    table2 = constants.link_table
    key1 = constants.bldg_pk_name
    key2 = constants.bldg_pk_name
    table_view = arcpy.MakeTableView_management(table1, "view")
    view_name = arcpy.Describe(table_view).basename
    join_name = arcpy.Describe(table2).basename
    items = []
    arcpy.AddJoin_management(table_view, key1, table2, key2)
    pk = view_name + "." + key1
    where = join_name + "." + constants.fmss_fk_name + " IS NULL AND " + view_name + ".Unit_Code IS NOT NULL"
    with arcpy.da.SearchCursor(table_view, pk, where) as cursor:
        for row in cursor:
            item = row[0]
            if item:
                items.append(item)
    arcpy.Delete_management(table_view)
    return items
    
def find_bldg_without_points(point_type):
    # joining polys to buildings does not work (even in ArcMap) due to the 1-M relationship
    # Need to create a temp table (without the relationship) for the join
    temp_table = scratch_table()
    where = "Point_Type = " + str(point_type)
    view = arcpy.MakeTableView_management(constants.point_fc, "points", where)
    arcpy.CopyRows_management(view, temp_table)
    arcpy.Delete_management(view)
    missing = find_missing_links(constants.bldg_table, temp_table, constants.bldg_pk_name)
    arcpy.Delete_management(temp_table)
    return missing

def find_bldg_without_polys(poly_type):
    # joining polys to buildings does not work (even in ArcMap) due to the 1-M relationship
    # Need to create a temp table (without the relationship) for the join
    temp_table = scratch_table()
    where = "Polygon_Type = " + str(poly_type)
    view = arcpy.MakeTableView_management(constants.poly_fc, "polys", where)
    arcpy.CopyRows_management(view, temp_table)
    arcpy.Delete_management(view)
    missing = find_missing_links(constants.bldg_table, temp_table, constants.bldg_pk_name)
    arcpy.Delete_management(temp_table)
    return missing

ok_dups_by_type = None
def well_known_dups(type):
    global ok_dups_by_type
    if not ok_dups_by_type:
        ok_dups_by_type = {}
        with arcpy.da.SearchCursor(constants.allowable_dups, ["Type","ID"]) as cursor:
            for row in cursor:
                if not ok_dups_by_type.has_key(row[0]):
                    ok_dups_by_type[row[0]] = set()
                ok_dups_by_type[row[0]].add(row[1])

    if ok_dups_by_type.has_key(type):                              
        return ok_dups_by_type[type]
    return set()

ok_link_issues_by_type = None
def well_known_link_issues(type):
    global ok_link_issues_by_type
    if not ok_link_issues_by_type:
        ok_link_issues_by_type = {}
        with arcpy.da.SearchCursor(constants.accepted_link_issues, ["Type","ID"]) as cursor:
            for row in cursor:
                if not ok_link_issues_by_type.has_key(row[0]):
                    ok_link_issues_by_type[row[0]] = set()
                ok_link_issues_by_type[row[0]].add(row[1])

    if ok_link_issues_by_type.has_key(type):                              
        return ok_link_issues_by_type[type]
    return set()
   
def find_dup_bldgs():
    return find_dups(constants.bldg_table,constants.bldg_pk_name)

def find_dup_bldg_links():
    return find_dups(constants.link_table,constants.bldg_pk_name)

def find_dup_fmss_id():
    dups = find_dups(constants.link_table,constants.fmss_fk_name)
    ok_dups = well_known_dups('FMSS_ID')
    dups = [dup for dup in dups if dup not in ok_dups]
    return dups

def find_dup_lcs_id():
    dups = find_dups(constants.link_table,constants.lcs_fk_name)
    ok_dups = well_known_dups('LCS_ID')
    dups = [dup for dup in dups if dup not in ok_dups]
    return dups

def find_dup_park_id():
    dups = find_dups(constants.link_table,constants.park_pk_name)
    ok_dups = well_known_dups('Park_ID')
    dups = [dup for dup in dups if dup not in ok_dups]
    return dups

def find_dup_point_geom_id():
    return find_dups(constants.point_fc,constants.geometry_id)

def find_dup_poly_geom_id():
    return find_dups(constants.poly_fc,constants.geometry_id)

def find_dup_centers():
    dups = find_dup_points(constants.point_types['Center'])
    ok_dups = well_known_dups('Center')
    dups = [dup for dup in dups if dup not in ok_dups]
    return dups

def find_dup_entrances():
    dups = find_dup_points(constants.point_types['Entrance'])
    ok_dups = well_known_dups('Entrance')
    dups = [dup for dup in dups if dup not in ok_dups]
    return dups

def find_dup_perimeters():
    dups = find_dup_polys(constants.poly_types['Perimeter'])
    ok_dups = well_known_dups('Perimeter')
    dups = [dup for dup in dups if dup not in ok_dups]
    return dups

def bldgs_without_center():
    return find_bldg_without_points(constants.point_types['Center'])

#def bldgs_without_entrance():
#    return find_bldg_without_points(constants.point_types['Entrance'])

#def bldgs_without_perim():
#    return find_bldg_without_polys(constants.poly_types['Perimeter'])

#def bldgs_without_link():
#    return find_missing_links(constants.bldg_table, constants.link_table, constants.bldg_pk_name)

def links_without_bldg():
    return find_missing_links(constants.link_table, constants.bldg_table, constants.bldg_pk_name)

def links_without_fmss():
    links = find_missing_links(constants.link_table, constants.fmss_table, constants.fmss_fk_name, constants.fmss_pk_name)
    ok_links = well_known_link_issues('FMSS_ID')
    links = [link for link in links if link not in ok_links]
    return links

def links_without_lcs():
    links = find_missing_links(constants.link_table, constants.lcs_table, constants.lcs_pk_name)
    ok_links = well_known_link_issues('LCS_ID')
    links = [link for link in links if link not in ok_links]
    return links

def myStr(s):
    if s:
        return str(s)
    else:
        return ''
    
def bldgs_without_fmss():
    links = nps_buildings_without_fmss()
    ok_links = well_known_link_issues('Building_ID')
    items = [link for link in links if link not in ok_links]
    if items:
        #link bldg id to bldg table to get common name and park, join to point FC to get extant
        #I know this is a very silly and inefficent way to do this, but converting a python list to
        #a table that can be joined to arcGIS data proved to difficult
        table1 = constants.bldg_table
        table2 = constants.point_fc
        details = []
        for i in items:
            where1 = "Building_ID = '"+i+"'"
            where2 = where1 + ' AND Point_Type = 0'
            with arcpy.da.SearchCursor(table1, ['Unit_Code','Common_Name'], where1) as cursor1, \
                 arcpy.da.SearchCursor(table2, ['Is_Extant'], where2) as cursor2:
                is_extant = ''
                #there should always be one and only one row, but this is safest
                for row in cursor2:
                    is_extant = row[0]
                detail = ['',is_extant,'',i]
                #there should always be one and only one row, but this is safest
                for row in cursor1:   
                    strings = [myStr(x) for x in row]
                    detail = [strings[0],is_extant,strings[1],i]
                details.append(detail)
        details.sort()
        items = details
    return items

def fmss_without_link():
    items = find_missing_links(constants.fmss_table, constants.link_table, constants.fmss_pk_name, constants.fmss_fk_name)
    if items:
        #link location to fmss export to get park, status, description,Location, type
        #I know this is a very silly and inefficent way to do this, but converting a python list to
        #a table that can be joined to ArcGIS data proved to difficult
        table1 = constants.fmss_table
        details = []
        for i in items:
            where1 = "Location = '"+i+"'"
            with arcpy.da.SearchCursor(table1, ['Park','Status','Description','BLDGTYPE',], where1) as cursor:
                detail = ['','','',i,'']
                #there should always be one and only one row, but this is safest
                for row in cursor:   
                    strings = [myStr(x) for x in row]
                    detail = strings[:3] + [i] + strings[-1:]
                    details.append(detail)
        details.sort()
        items = details
    return items

def polys_without_bldg():
    return find_missing_links(constants.poly_fc, constants.bldg_table, constants.bldg_pk_name)

def points_without_bldg():
    return find_missing_links(constants.point_fc, constants.bldg_table, constants.bldg_pk_name)

def bldgs_with_GPS_problems():
    bldgs = find_bldg_without_polys(constants.poly_types['Perimeter'])
    entrances = find_bldg_without_points(constants.point_types['Entrance'])
    if bldgs or entrances:
        pass #do something
        return ['  ** Problems!, see {}'.format(constants.gps_export)]
    else:
        return []

def print_heading(title):
    separator = '='*len(title)
    print separator
    print title
    print separator
    
def print_issues(issues,item_names):
    print ','.join(item_names)
    for issue in issues:
        if isinstance(issue,list):
            print ','.join(issue)
        else:
            print issue

operations = [
    ("Duplicate Building Ids in the Buildings Table", find_dup_bldgs, "Building_ID", None),
    ("Duplicate Building Ids in Building Points with the Center Subtype", find_dup_centers, "Building_ID", None),
    #("Duplicate Building Ids in Building Points with the Entrance Subtype", find_dup_entrances, "Building_ID", None),
    #("Duplicate Building Ids in Building Polygons with the Perimeter Subtype", find_dup_perimeters, "Building_ID", None),
    #("Duplicate Building Ids in the Building Links Table", find_dup_bldg_links, "Building_ID", None),
    #("Duplicate Geometry Ids in the Point Feature Class", find_dup_point_geom_id, "Geometry_ID", None),
    #("Duplicate Geometry Ids in the Polygon Feature Class", find_dup_poly_geom_id, "Geometry_ID", None),
    #("Duplicate FMSS Ids in the Building Links Table", find_dup_fmss_id, "FMSS_ID", None),
    #("Duplicate LCS Ids in the Building Links Table", find_dup_lcs_id, "LCS_ID", None),
    #("Duplicate Park Ids in the Building Links Table", find_dup_park_id, "Park_ID", None),
    
    #("Buildings without a Center (in point feature class)", bldgs_without_center, "Building_ID", None),
    ##("Buildings without an Entrance (in point feature class)", bldgs_without_entrance, "Building_ID", None),
    ##("Buildings without a Perimeter (in polygon feature class)", bldgs_without_perim, "Building_ID", None),
    ##("Buildings without a Record in the Links Table", bldgs_without_link, "Building_ID", None),
    #("Building Links with an Building ID not in the Buildings Table", links_without_bldg, "Building_ID", None),
    #("Building Links with an FMSS ID not in the FMSS Table", links_without_fmss, "Building_ID", None),
    #("Building Links with an LCS ID not in the LCS Table", links_without_lcs, "Building_ID", None),
    ("Buildings with UnitCode and No FMSS_ID in Links Table", bldgs_without_fmss, ['Park','Status','Description','ID','Type'], constants.no_fmss_export),
    ("FMSS Records without a Record in the Link Table", fmss_without_link, ['Park','Status','Description','ID','Type'], constants.no_gis_export),
    #("Building Polygons without a Building Record", polys_without_bldg, "Building_ID", None),
    #("Building Points without a Building Record", points_without_bldg, "Building_ID", None),
    #("Buildings with GPS Issues", bldgs_with_GPS_problems, ['Park','Status','Description','ID','Type'], constants.gps_export)
    #("Buildings with Photo Issues", ??, ['Park','Status','Description','ID','Type'], None)
    #("Photo without buildings", ??, ['Park','Status','Description','ID','Type'], None)
    ]

def main():
    for title,func,item_names,file in operations:
        print_heading(title)
        if isinstance(item_names,str):
            item_names = item_names.split(',')
        issues = func()
        if issues:
            if file:
                import csv
                with open(file,'wb') as csvfile:
                    csv.writer(csvfile).writerows([item_names]+issues)
                print '  ** Problems!, see {}'.format(file)
            else:
                print_issues(issues,item_names)
        else:
            print '  Nothing found! All is well!!'
            if file:
                open(file,'wb').close()


if __name__ == '__main__':
    main()
