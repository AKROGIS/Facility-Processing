Regan Sarwas created.
Scripts for updating photo changes on our FMSS website

Scripts:
========
 Master copies of these scripts are at:
 https://github.com/regan-sarwas/Building-QC
 The scripts require the following support files
   apply_orientation.py
   ARLRDBD.TTF
 
 make_thumbnails.py
 ------------------
 This will sync the THUMB folder with the ORIGINAL folder
 BUG: This script can leave orphaned thumbnails if the original file is renamed or deleted
      It is safe to ignore the orphans.
      To remove all orphans, purge the THUMB folder before running this script.
 
 make_webphotos.py
 -----------------
 This will sync the WEB folder with the ORIGINAL folder.
 BUG: Some changes in the database should update watermarking. This script is not smart enough
      to find these changes and update the watermarking.
      WORKAROUND: delete the web version of photos that should get updated watermarking before
      running this script.  You could clear the entire web folder, and a completely new set of
      web resolution photos will be created in about 10 minutes.
 
 make_photos_json.py
 -------------------
 This will create a json file that list each photo by an FMSS Location Record Number.
 This is used by the buildings web site

 make_buildings_csv.py
 ---------------------
 This will create a csv file listing all the FMSS buildings for use in the buildings web site.
 
 update_photos_on_server.bat
 ---------------------------
 This is a robocopy script that sync the Photo Server with the files in WEB and THUMB
 it also copies photos.json to \\akrgis.nps.gov\inetApps\fmss\photos.json
 and buildings.csv to \\akrgis.nps.gov\inetApps\buildings\data\buildings.csv


Output
 ---------------------------
Scripts in this folder create 2 files

Buildings.csv
Photos.json

download https://bootstrap.pypa.io/get-pip.py to c:\Python27\ArcGIS10.3\Scripts\get-pip.py
C:\Python27\ArcGIS10.3\python.exe C:\Python27\ArcGIS10.3\Scripts\get-pip.py
use os.path.dirname(sys.executable)

fix basepath to go up two levels to base photo dir.
Try multiple SQL Server Clients
