#!/usr/bin/env python

"""Compares the list of building locations with the list of photos"""

__author__ = "Regan Sarwas, GIS Team, Alaska Region, National Park Service"
__email__ = "regan_sarwas@nps.gov"
__copyright__ = "Public Domain - product of the US Government"

import os.path

default_photo_file = "MasterPhotoListCopy.csv"
default_location_file = "BuildingLocations.csv"
default_no_photo_file = "Locations_in_gis_no_photo.csv"
default_no_bldg_file = "Locations_in_photos_no_gis.csv"

def photo_problems(photo_csv, location_csv):
	photos = set([])
	photo_details = {}
	with open(photo_csv) as fh:
		fh.readline()  # Remove header
		for line in fh:
			items = line.split(',')
			# Unit,Filename,Asset_Code,LocationRecord,ASSETID,PhotoDate,originalphotopath,AssociatedRecord,notes,,,
			# 0   ,1       ,2         ,3             ,4      ,5        ,6                ,7               ,8
			id = items[3]
			unit = items[0]
			photos.add(id)
			if not photo_details.has_key(id):
				photo_details[id] = []
			photo_details[id].append([unit, id, items[1], items[5]])
	#print("There are photos for {0} buildings".format(len(photos)))		

	bldgs = set([])
	bldg_details = {}
	with open(location_csv) as fh:
		fh.readline()  # Remove header
		for line in fh:
			items = line.split(',')
			# Lat,Long,Unit,FMSS_Id,Park_Id,Name,Description,Type,Status,Occupant,Value,Size,Date
			# 0  ,1   ,2   ,3      ,4      ,5   ,6          ,7   ,8     ,9       ,10   ,11  ,12
			unit = items[2]
			id = items[3]
			bldgs.add(id)
			bldg_details[id] = [unit, id, items[6], items[8]]
	#print("There are locations for {0} buildings".format(len(bldgs)))

	missing_photos = bldgs-photos
	missing_entrance = photos-bldgs

	bldg_issues = [bldg_details[id] for id in missing_photos]
	#rows = [str(bldg_unit[id])+','+str(id) for id in missing_photos]
	bldg_issues.sort()

	photo_groups = [photo_details[id] for id in missing_entrance]
	#there is a group of photos for each id
	photo_issues = [issue for group in photo_groups for issue in group]
	#rows = [str(photo_folder[id])+','+str(id) for id in missing_entrance]
	photo_issues.sort()

	return bldg_issues, photo_issues


def main():
	#root = "/Users/regan_sarwas/Desktop/photos/"
	#root = r"T:\PROJECTS\AKR\Buildings\PhotosFromAllYears-Geotagged\2014Reprocess"
	root = os.path.dirname(os.path.abspath(__file__))
	photo_file = os.path.join(root,default_photo_file)
	location_file = os.path.join(root,default_location_file)
	bldg_issues,photo_issues = photo_problems(photo_file, location_file)
	if bldg_issues:
		print("There are {0} Location Record Numbers in the Spatial data with no photos:".format(len(bldg_issues)))
		print("Unit_Code,FMSS_ID,Name,Status")
		print("Text,Text")  #required or else ArcGIS will interpret the ID column as a number (the joins do not work)
		for issue in bldg_issues:
			print(','.join([str(i) for i in issue]))
	else:
		print("All buildings with a location have a photo")
	if photo_issues:
		print("There are {0} Location Record Numbers in the Photo list with no spatial record:".format(len(photo_issues)))
		print("Unit_Code,FMSS_ID,FileName,PhotoDate")
		print("Text,Text")  #required or else ArcGIS will interpret the ID column as a number (the joins do not work)
		for issue in photo_issues:
			print(','.join([str(i) for i in issue]))
	else:
		print("All buildings with a photo have a location")


def main2():
	#root = "/Users/regan_sarwas/Desktop/photos/"
	#root = r"T:\PROJECTS\AKR\Buildings\PhotosFromAllYears-Geotagged\2014Reprocess"
	root = os.path.dirname(os.path.abspath(__file__))
	photo_file = os.path.join(root,default_photo_file)
	location_file = os.path.join(root,default_location_file)
	no_photo_file = os.path.join(root,default_no_photo_file)
	no_location_file = os.path.join(root,default_no_bldg_file)
	bldg_issues,photo_issues = photo_problems(photo_file, location_file)
	
	if bldg_issues:
		import csv
		item_names = ['Park','FMSS_ID','Name','Status']
		with open(no_photo_file,'wb') as csvfile:
			csv.writer(csvfile).writerows([item_names]+bldg_issues)
	else:
		open(no_photo_file,'wb').close()
	if photo_issues:
		import csv
		item_names = ['Park','FMSS_ID','FileName','PhotoDate']
		with open(no_location_file,'wb') as csvfile:
			csv.writer(csvfile).writerows([item_names]+photo_issues)
	else:
		open(no_location_file,'wb').close()


if __name__ == '__main__':
	main2()
	
