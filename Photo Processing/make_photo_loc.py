#!/usr/bin/env python

"""Creates a CSV file of photo files without a building location
   Highly dependent on the format of the location data
   as well as the output file expected by the web software"""

__author__ = "Regan Sarwas, GIS Team, Alaska Region, National Park Service"
__email__ = "regan_sarwas@nps.gov"
__copyright__ = "Public Domain - product of the US Government"

import os.path
import csv

#root = "/Users/regan_sarwas/Desktop/photos/"
#root = r"T:\PROJECTS\AKR\Buildings\PhotosFromAllYears-Geotagged\2014Reprocess"
root = os.path.dirname(os.path.abspath(__file__))
photo_csv = os.path.join(root,"PhotoListWithId.csv")
bldg_csv = os.path.join(root,"BuildingLocations.csv")
map_csv = os.path.join(root,"PhotosNoBldg.csv")

thumbnail_url = "http://akrgis.nps.gov/buildings/photos/thumbs"

ids_with_bldg_location = set([])
with open(bldg_csv, 'rb') as fh:
	fh.readline()  # remove the header
	bldg_reader = csv.reader(fh, delimiter=',', quotechar='"')
	for row in bldg_reader:
		# Lat,Long,Unit,FMSS_Id,Park_Id,Name,Description,Type,Status,Occupant,Value,Size,Date
		# 0  ,1   ,2   ,3      ,4      ,5   ,6          ,7   ,8     ,9       ,10   ,11  ,12
		id = row[3]
		ids_with_bldg_location.add(id)

			
with open(photo_csv, 'rb') as f1, open(map_csv,'wb') as f2:
	f1.readline()  # remove the header
	photo_reader = csv.reader(f1, delimiter=',', quotechar='"')
	f2.write("Number,Latitude,Longitude,Title,Short_Desc,Image_Url\n")
	csv_writer = csv.writer(f2, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
	ids_done = set([])
	count = 1
	for row in photo_reader:
		# Id,Date,Unit,File,Latitude,Longitude,Url
		# 0 ,1   ,2   ,3   ,4       ,5        ,6
		id = row[0]
		if id and id not in ids_with_bldg_location and id not in ids_done:
			unit = row[2]
			date = row[1]
			file = row[3]
			desc = "{0}/{1}".format(unit,file)
			lat = row[4]
			lon = row[5]
			url = row[6]
			if lat and lon:
				row_data = [count,lat,lon,id,desc,url]
				csv_writer.writerow(row_data)
				ids_done.add(id)
				count = count + 1
			else:
				print("{0:>10}  {1}  {2}".format(id,date[:10],desc))