# Scripts

This folder contains scripts for updating photo changes on our FMSS website.

This folder was created by and is maintained by Regan Sarwas.
Master copies of these documents and scripts are at:
https://github.com/AKROGIS/Facility-Processing/blob/master/Photo%20Processing/scripts

The documented scripts require the following support files in this folder
  * `apply_orientation.py`
  * `ARLRDBD.TTF`

## Contents

### `add_photo_list_to_database.py`

This script will push a CSV file listing the new photo files into a new
version on the SDE database `akr_facility2`. This script is sensitive to
the structure of the input CSV, the database schema, and other naming
conventions in the destination database.  This script requires the `pyodbc`
Python module (use `pip` to install it, see script for details).  This script
will fail unless you have edit permissions in the facilities database.
 
### `make_photos_json.py`

This will create a json file that lists each photo by it photo foreign key
(`FACLOCID`, or similar). This file is copied to the root of the photos
library on the website and is used by the buildings and facilities web sites.

### `make_thumbnails.py`

This will sync the `THUMB` folder with the `ORIGINAL` folder. This script
requires the `pillow` (aka `PIL`) Python module (use `pip` to install `pillow`,
see script for details).

**BUG:** This script can leave orphaned thumbnails if the original file is
renamed or deleted. It is safe to ignore the orphans.
To remove all orphans, purge the `THUMB` folder before running this script.

### `make_webphotos.py`

This will sync the `WEB` folder with the `ORIGINAL` folder. This script
requires the `pillow` (aka `PIL`) Python module (use `pip` to install `pillow`,
see script for details).

**BUG:** Some changes in the database should update watermarking. This script
is not smart enough to find these changes and update the watermarking.

**WORKAROUND:** delete the web version of photos that should get updated
watermarking before running this script.  You could clear the entire web folder,
and a completely new set of web resolution photos will be created in about 10
minutes.

### `update_photos_on_server.bat`

This is a robocopy script that will update the web server with the files in
`WEB` and `THUMB` it also copies `photos.json` to 
`\\akrgis.nps.gov\inetApps\fmss\photos.json` and `buildings.csv` to 
`\\akrgis.nps.gov\inetApps\buildings\data\buildings.csv`.
The user will need write access to the web server (`akrgis.nps.gov`).

## Output

Scripts in this folder will update the files in `WEB` and `THUMB` and create
`Photos.json`.
