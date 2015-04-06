#!/usr/bin/env python

"""Creates a CSV file with building location, attributes and thumbnail URL
   Highly dependent on the format (columns and contents) of the location data
   as well as the output file expected by the web software"""

__author__ = "Regan Sarwas, GIS Team, Alaska Region, National Park Service"
__email__ = "regan_sarwas@nps.gov"
__copyright__ = "Public Domain - product of the US Government"

import os.path
import locale
import csv

#root = "/Users/regan_sarwas/Desktop/photos/"
#root = r"T:\PROJECTS\AKR\Buildings\PhotosFromAllYears-Geotagged\2014Reprocess"
root = os.path.dirname(os.path.abspath(__file__))
photo_csv = os.path.join(root,"MasterPhotoListCopy.csv")
bldg_csv = os.path.join(root,"BuildingLocations.csv")
map_csv = os.path.join(root,"BldgWithPhotos.csv")
map2_csv = os.path.join(root,"BldgWithoutPhotos.csv")

thumbnail_url = "http://akrgis.nps.gov/apps/bldgs/photos/thumbs"

#The locale 'en_US' works on the Mac, but for Windows it must be just 'US'.
#locale.setlocale(locale.LC_ALL, 'en_US')
locale.setlocale(locale.LC_ALL, 'US')

ids_with_photo = set([])
with open(photo_csv, 'rb') as fh:
	fh.readline()  # remove the header
	photo_reader = csv.reader(fh, delimiter=',', quotechar='"')
	for row in photo_reader:
		# Unit,Filename,Asset_Code,LocationRecord,ASSETID,PhotoDate,originalphotopath,AssociatedRecord,notes,,,
		# 0   ,1       ,2         ,3             ,4      ,5        ,6                ,7               ,8
		id = row[3]
		ids_with_photo.add(id)

			
with open(bldg_csv, 'rb') as f1, open(map_csv,'wb') as f2, open(map2_csv,'wb') as f3:
	f1.readline()  # remove the header
	loc_reader = csv.reader(f1, delimiter=',', quotechar='"')
	f2.write("Number,Latitude,Longitude,Title,Short_Desc,Image_Url,Cost,Size,Status,Category,Date,Occupant,Name,ParkName\n")
	csv_writer1 = csv.writer(f2, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
	f3.write("Number,Latitude,Longitude,Title,Short_Desc,Image_Url,Cost,Size,Status,Category,Date,Occupant,Name,ParkName\n")
	csv_writer2 = csv.writer(f3, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
	count = 0
	for row in loc_reader:
		# Lat,Long,Unit,FMSS_Id,Park_Id,Name,Description,Type,Status,Occupant,Value,Size,Date
		# 0  ,1   ,2   ,3      ,4      ,5   ,6          ,7   ,8     ,9       ,10   ,11  ,12  
		id = row[3]
		if id:
			lat = row[0]
			lon = row[1]
			unit = row[2]
			park_name = row[4]
			name = row[5]
			desc = row[6]
			cat = row[7]
			status = row[8]
			
			occupant = row[9]
			if not occupant:
				occupant = "unknown"
				
			cost = row[10]
			try:
				cost = "$" + locale.format("%d", int(locale.atof(cost)), grouping=True)
			except:
				cost = "unknown"
			if cost == "$0":
				cost = "unknown"

			size = row[11]
			try:
				size = locale.format("%d", int(locale.atof(size)), grouping=True) + " Sq Ft"
			except:
				size = "unknown"
			if size == "0 Sq Ft":
				size = "unknown"

			date = row[12].strip()
			try:
				#date = date[-4:]
				date = date[:4]
			except:
				date = "unknown"
			if not date:
				date = "unknown"
				
			url = "{0}/{1}/{2}.jpg".format(thumbnail_url,unit,id)
			count = count + 1
			row_data = [count,lat,lon,id,desc,url,cost,size,status,cat,date,occupant,name,park_name]
			if id in ids_with_photo:
				csv_writer1.writerow(row_data)
			else:
				csv_writer2.writerow(row_data)
				#print("There are no photos for bldg {0}".format(id))