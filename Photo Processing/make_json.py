#!/usr/bin/env python

"""Get the list of photos for each FMSS ID and save it as a JSON object"""

__author__ = "Regan Sarwas, GIS Team, Alaska Region, National Park Service"
__email__ = "regan_sarwas@nps.gov"
__copyright__ = "Public Domain - product of the US Government"

import os.path
import json

#root = "/Users/regan_sarwas/Desktop/photos/"
#root = r"T:\PROJECTS\AKR\Buildings\PhotosFromAllYears-Geotagged\2014Reprocess"
root = os.path.dirname(os.path.abspath(__file__))
photo_csv = os.path.join(root,"MasterPhotoListCopy.csv")
photo_js = os.path.join(root,"photos.js")

photos = {}
with open(photo_csv) as fh:
	fh.readline()  # Remove header
	for line in fh:
		items = line.split(',')
		# Unit,Filename,Asset_Code,LocationRecord,ASSETID,PhotoDate,originalphotopath,AssociatedRecord,notes,,,
		# 0   ,1       ,2         ,3             ,4      ,5        ,6                ,7               ,8
		id = items[3]
		photodate = items[5]
		src = items[1]
		unit = items[0]
		#timestamp = src.split('_')[1].split('.')[0].replace(' ','_')
		#item = timestamp
		item = unit + '/' + src
		if photos.has_key(id):
			photos[id].append(item)
		else:
			photos[id] = [item]
print("There are {0} buildings with photos".format(len(photos)))		
#print(photos)			
with open(photo_js,'w') as fh:
	fh.write("var photos = \n")
	fh.write(json.dumps(photos,indent=2, separators=(',', ': ')))
