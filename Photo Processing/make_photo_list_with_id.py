#!/usr/bin/env python

"""Creates a list of photo with id, dates, and location by merging two related files"""

__author__ = "Regan Sarwas, GIS Team, Alaska Region, National Park Service"
__email__ = "regan_sarwas@nps.gov"
__copyright__ = "Public Domain - product of the US Government"

import os.path

#root = "/Users/regan_sarwas/Desktop/photos/"
#root = r"T:\PROJECTS\AKR\Buildings\PhotosFromAllYears-Geotagged\2014Reprocess"
root = os.path.dirname(os.path.abspath(__file__))
file_csv = os.path.join(root, "PhotoList.csv")
photo_csv = os.path.join(root, "MasterPhotoListCopy.csv")
list_csv = os.path.join(root, "PhotoListWithId.csv")

thumbnail_url = "http://akrgis.nps.gov/apps/bldgs/photos/thumbs"

files = {}
with open(file_csv) as fh:
    fh.readline()  # Remove header
    for line in fh:
        items = line.split(',')
        # folder,photo,id,namedate,exifdate,lat,lon,gpsdate,size,filedate
        # 0     ,1    ,2 ,3       ,4       ,5  ,6  ,7      ,8   ,9
        folder = items[0]
        file = items[1]
        tag = folder + "/" + file
        files[tag] = items

csv = {}
with open(photo_csv) as fh, open(list_csv, 'w') as fo:
    fh.readline()  # Remove header
    fo.write("Id,Date,Unit,File,Latitude,Longitude,Url\n")
    for line in fh:
        items = line.split(',')
        # Unit,Filename,Asset_Code,LocationRecord,ASSETID,PhotoDate,originalphotopath,AssociatedRecord,notes,,,
        # 0   ,1       ,2         ,3             ,4      ,5        ,6                ,7               ,8
        unit = items[0]
        filename = items[1]
        key = unit + "/" + filename
        try:
            fileitems = files[key]
        except KeyError:
            continue
        tag = items[3]
        if fileitems[4]:  # exifdate
            date = fileitems[4]
        elif fileitems[7]:  # gpsdate
            date = fileitems[7] + 'Z'
        else:
            date = items[5]  # filename date - may not be well formatted, or even a date
        #FIXME - check if we have a valid date, if not set to None, so we can use the filedate
        if not date and fileitems[9]:  # filedate
            date = fileitems[9].rstrip()
        lat = fileitems[5]
        lon = fileitems[6]
        url = "{0}/{1}/{2}.jpg".format(thumbnail_url, unit, tag)
        fo.write("{0},{1},{2},{3},{4},{5},{6}\n".format(tag, date, unit, filename, lat, lon, url))
