Photo workflow
==============
All of the paths in this workflow are relative to `T:\PROJECTS\AKR\FMSS\PHOTOS`.
The scripts assume that they are in the folders described below and they use 
relative paths to find the necessary resources.  Therefore if everything in
`T:\PROJECTS\AKR\FMSS\PHOTOS` is moved to a different location, it should all
still work.

1) Check for records in `.\PROCESSING\PhotoCSVLoader.csv`
   * If there are none, you are done.
2) For any photo listed in `.\PROCESSING\PhotoCSVLoader.csv`
   that does not have an `ORIGINALPATH` in `.\ORIGINAL`
   copy the original full resolution un-watermarked version from the `ORIGINALPATH`
   to the correct park (`UNITCODE`) folder under `.\ORIGINAL`
3) Run the script `.\PROCESSING\Compare_Database_photos_To_ORIGINAL_Folder.py`
   and resolve any issues with missing or mis-named photo files before proceeding.
4) Review the spreadsheet for any violation of the requirements in the
   `.\PROCESSING\Readme.html`. Contact the `CREATEUSER` if necessary, or remove if
   the record if there is no `CREATEUSER`. 
5) Move the csv to .\PROCESSING\Done Processing`, and append a date stamp (_YYYY-MM-DD) to the filename.
   * IF it cannot by moved, it is in use. Either find the culprit and have them close
     out, or wait until they are done with their changes.
6) Copy `.\PROCESSING\TemplatePhotoCSVLoader - Empty.csv` to  `.\PROCESSING\PhotoCSVLoader.csv`.
7) Create a version in `akr_facility2` and load the CSV data into the `AKR_ATTACH`
   table in your version.
   * TODO - specify field mapping
   * Run the Calculations for `AKR_ATTACH`
   * Run the QC Check for `AKR_ATTACH` and resolve any issues
   * Run the script `.\PROCESSING\Compare_Database_photos_To_ORIGINAL_Folder.py` and resolve
     any issues.  If there were additional database edits, be sure to rerun the calculations
     and QC checks.
   * Request the SDE admin post your version (to include updating the FGDB export)
8) Run `.\PROCESSING\website scripts\make_webphotos.py` to create web sized photos
   in `.\WEB` from the new photos in `ORIGINALS`
9) Run `.\PROCESSING\website scripts\make_thumbnails.py` to create thumbnail photos
   in `.\THUMB` from the new photos in `ORIGINALS`
9) Run `.\PROCESSING\website scripts\update_photos_on_server.bat` to copy the new photos
   in `.\WEB` and `.\THUMB` to the server (`\\akrgis.nps.gov\inetapps\fmss\photos`).
9) Run `.\PROCESSING\website scripts\make_photos_json.py` to create an updated json list of photos
   * copy `photos.json` to `\\akrgis.nps.gov\inetapps\fmss\photos.json`

