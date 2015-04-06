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
bldg_csv = os.path.join(root,"BuildingLocations.csv")
map_csv = os.path.join(root,"BldgWithPhotos.csv")

with open(bldg_csv, 'rb') as f1, open(map_csv,'wb') as f2:
	f1.readline()  # remove the header
	loc_reader = csv.reader(f1, delimiter=',', quotechar='"')
	f2.write("Latitude,Longitude,Title,Short_Desc,Cost,Size,Status,Category,Date,Occupant,Name,ParkName\n")
	csv_writer1 = csv.writer(f2, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
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

			#date should be in ISO Format (therefore first 4 chars are year)
			date = row[12]
			try:
				date = date[:4]
			except:
				date = "unknown"
			if not date:
				date = "unknown"
				
			row_data = [lat,lon,id,desc,cost,size,status,cat,date,occupant,name,park_name]
			csv_writer1.writerow(row_data)
