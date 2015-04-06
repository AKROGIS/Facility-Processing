Master documents:
	MasterPhotoList.xlsx
	All_Buildings_V6.gdb
	All_Buildings_V6.mxd
	{UnitCode}/*.jpg

If the building spatial data has changed:
  Run CreateWebData.py (in ../../2015/Regan's Updates)
		- Creates BuildingLocations.csv
	Update the building footprint web mapping service
	
If the list of photos has changed
	Export MasterPhotoList.xlsx to MasterPhotoListCopy.csv
		- Creates  MasterPhotoListCopy.csv

If the photo files have changed
	Run make_photo_list.py
		- Creates PhotoList.csv
	Run check_photofiles.py
	Fix issues.
	Go back to the beginning

	
Run check_bldgs.py
	Check on issues (fixing is optional, but only matches will appear in website)
	If you fixed issues, go back to the beginning

Run make_photo_list_with_id.py
	- Creates PhotoListWithId
Run make_bldg_loc.py
	- Creates BldgWithPhotos.csv
Run make_photo_loc.py
	- Creates PhotosNoBldg.csv
Run make_photos.py and make_thumbnails.py
	- Creates thumbnail and web-res (watermarked) photos
Run make_json.py
  - Creates photos.js
Move the following files and folders to the website
	BldgWithPhotos.csv
	PhotosNoBldg.csv
  photos.js
	thumb folder (only necessary to copy new files)
	web folders (only necessary to copy new files)


SPECIAL NOTES:
The computer running the python scripts must have python installed (comes with ArcGIS)
You must also have the following python modules loaded:
	exifread - https://pypi.python.org/pypi/ExifRead
	pillow 2.x - https://pypi.python.org/pypi/Pillow