#!/usr/bin/env python

"""Compares a list of photo files with the list of photos"""

__author__ = "Regan Sarwas, GIS Team, Alaska Region, National Park Service"
__email__ = "regan_sarwas@nps.gov"
__copyright__ = "Public Domain - product of the US Government"

import os.path

#root = "/Users/regan_sarwas/Desktop/photos/"
#root = r"T:\PROJECTS\AKR\Buildings\PhotosFromAllYears-Geotagged\2014Reprocess"
root = os.path.dirname(os.path.abspath(__file__))
file_csv = os.path.join(root,"PhotoList.csv")
photo_csv = os.path.join(root,"MasterPhotoListCopy.csv")

files = set([])
with open(file_csv) as fh:
	fh.readline()  # Remove header
	for line in fh:
		items = line.split(',')
		# folder,photo,id,namedate,exifdate,lat,lon,gpsdate,size,filedate
		# 0     ,1    ,2 ,3       ,4       ,5  ,6  ,7      ,8   ,9
		folder = items[0]
		file = items[1]
		id = folder + "/" + file
		files.add(id)
print("There are {0} photos files".format(len(files)))		

csv = set([])
with open(photo_csv) as fh:
	fh.readline()  # Remove header
	for line in fh:
		items = line.split(',')
		# Unit,Filename,Asset_Code,LocationRecord,ASSETID,PhotoDate,originalphotopath,AssociatedRecord,notes,,,
		# 0   ,1       ,2         ,3             ,4      ,5        ,6                ,7               ,8
		unit = items[0]
		file = items[1]
		id = unit + "/" + file
		csv.add(id)
print("There are {0} photo records in the CSV file".format(len(csv)))		

missing_csv = files-csv
missing_file = csv-files

if len(missing_csv):
	print("There are {0} photo files with no CSV record:".format(len(missing_csv)))
	files = list(missing_csv)
	files.sort()
	for file in files:
		print("\t"+file)
else:
	print("All photo files have a CSV record")		

if len(missing_file):
	print("There are {0} records in the CSV with no file:".format(len(missing_file)))
	rows = list(missing_file)
	rows.sort()
	for row in rows:
		print("\t"+row)
else:
	print("All CSV records have a photo file")		
