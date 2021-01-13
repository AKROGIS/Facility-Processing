# Photo workflow

All of the paths in this workflow are relative to the parent folder of this
readme file, currently `T:\PROJECTS\AKR\FMSS\PHOTOS`.
The scripts assume that they are in the folders described below and they use
relative paths to find the necessary resources.  Therefore if everything in
`T:\PROJECTS\AKR\FMSS\PHOTOS` is moved to a different location, it should all
still work.

**NOTE:**
*This process is **NOT** for geo-tagged photos (such as from a mobile device).
Those photos will go into the `akr_facility2.AKR_ATTACH_PT` feature class
using a TBD process.*
          
## Photo Providers

* This process is for photos that will be linked to a geographic feature in the
  `akr_facility2` database. These photos can be linked to the items by
  `FACLOCID`, `FACASSETID`, `FEATUREID`, or `GEOMETRYID`.
* Each new photo must be documented in `.\PROCESSING\PhotoCSVLoader.csv`.  See
  `.\PROCESSING\Readme.html` for details on the column values.
* The original full resolution un-watermarked version of the photos should be
  copied to the correct park folder under `.\ORIGINAL`.  The file name is not
  important, but it must be a unique name in the park folder. **WARNING** Be
  very careful that you do not overwrite an existing photo.  Not only will you
  destroy a photo that may be irreplaceable, but you will also create an
  inconsistency that may be hard to resolve.
* Run the script `.\PROCESSING\Compare_Database_photos_To_ORIGINAL_Folder.py`
  and resolve any issues with missing or mis-named photo files before
  proceeding.

## PDS Data Manager

1. Check for records in `.\PROCESSING\PhotoCSVLoader.csv`
   * If there are none, you are done.
2. For any photo listed in `.\PROCESSING\PhotoCSVLoader.csv` that has an
   `ORIGINALPATH` but is not in `.\ORIGINAL` copy the original full resolution
   un-watermarked version from the `ORIGINALPATH` to the correct folder under
   `.\ORIGINAL` (i.e. `UNITCODE/FOLDER`).
3. Run the script `.\PROCESSING\Compare_Database_photos_To_ORIGINAL_Folder.py`
   and resolve any issues with missing or mis-named photo files before
   proceeding.
4. Review the spreadsheet for any violation of the requirements in the
   `.\PROCESSING\Readme.html`. Contact the `CREATEUSER` if necessary, or remove
   the record if there is no `CREATEUSER`.
5. Move the csv to `.\PROCESSING\scripts` to ensure that it is not edited by
   another user while processing.
   * If it cannot by moved, it is in use. Either find the culprit and have them
     close out, or wait until they are done with their changes.  If they have
     made changes, start over.
6. Run the script `.\PROCESSING\scripts\add_photo_list_to_database.py`.  This
   will add the photos listed in the CSV file to a new version in the facilities
   SDE.
7. Run the [Enterprise-QC](https://github.com/AKROGIS/Enterprise-QC) checks
   on the new version (see the view `QC_ISSUES_AKR_ATTACH`).  Correct any
   issues and post the version to `DEFAULT` and then delete the new version.   
8. Move the csv to `.\PROCESSING\Done Processing`, and append a date stamp
   (YYYY-MM-DD) to the filename.
9. Copy `.\PROCESSING\TemplatePhotoCSVLoader - Empty.csv` to
   `.\PROCESSING\PhotoCSVLoader.csv`.
9. Run `.\PROCESSING\Compare_Database_photos_To_ORIGINAL_Folder.py` to verify
   that the database matches the file system.
9. Run `.\PROCESSING\scripts\make_webphotos.py` to create web sized photos
   in `.\WEB` from the new photos in `.\ORIGINALS`.
9. Run `.\PROCESSING\scripts\make_thumbnails.py` to create thumbnail photos
   in `.\THUMB` from the new photos in `.\ORIGINALS`.
9. Run `.\PROCESSING\scripts\make_photos_json.py` to create an updated json
   list of photos.
9. Run `.\PROCESSING\scripts\make_buildings_csv.py` to create an updated json
   list of buildings.
9. Run `.\PROCESSING\scripts\update_photos_on_server.bat` to copy the new CSV
   files and the photos in `.\WEB` and `.\THUMB` to the server
   (`\\akrgis.nps.gov\inetapps\fmss\photos`).
