This folder was created by Joel Cusick.  Regan Sarwas assisted with the documentation.
It is also used for documenting photos (in `PhotoCSVLoader.csv`) that need
to be added to the `akr_facility2` geodatabase.
The folder `Done Processing` contains processed and date stamped versions of
`PhotoCSVLoader.csv`
This folder can also be used for the temporary processing (renaming) of photos
prior to storing them into a sub folder of `..\ORIGINAL`.

The PDS Data Manager should reference `Workflow.md` for instructions
on processing new photos.

Master copies of these documents are at:
https://github.com/AKROGIS/Facility-Processing/tree/master/Photo%20Processing

Photo List
==========
* Edit `PhotoCSVLoader.csv` to document photos that should be added to the
  facility photos.  These photos can document any feature in the `akr_facility2`
  geodatabase.

* This file can be edited in MS Excel, but must be saved as a CSV file.
  **WARNING:** Excel can irreparably damage dates in a CSV file and may not respect
  ISO formatting (required for database transfer). I strongly recommend that you do some
  testing on a copy and the open the CSV file in a text editor to check your settings.
  A good tip is to format the date columns with a custom format of `yyyy-mm-ddThh:mm:ss`
  Also try not to used commas in the notes or filenames.

* Requirements of the fields in `PhotoCSVLoader.csv`

  * UNITCODE => AKR_ATTACH.UNITCODE and part of AKR_ATTACH.ATCHLINK

    Required.  This must be one of the well known AKR UNITCODE domain values
    Any invalid values will be rejected during QC.  This will also be the sub folder
    in `..\ORIGINAL` where the original image will be archived.

  * FOLDER => part of AKR_ATTACH.ATCHLINK

    Optional.  The folder or path under the `..\ORIGINAL\{UNITCODE}`, and in
    which the file called FILENAME will be found. Separate path elements with
    a slash (/), not a backslash (\\).

  * FILENAME => AKR_ATTACH.ATCHALTNAME and part of AKR_ATTACH.ATCHLINK

    Required.  The filename of the photo, including the extension (i.e. .jpg)
    The file name must not include the directory path.  The only restriction on the
    file name is that is unique among all photos in a UNITCODE.  If it is not unique,
    a numberical suffix will be added to make it unique.
    Typically photo files have been renamed with a FMSS location ID (when available),
    and the timestamp.

  * TIMESTAMP => AKR_ATTACH.ATCHDATE (AKR extension)

    Required. The date/time that the photo was taken.  It must be
    an [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601) formatted date/time
    (i.e. YYYY-MM-DDThh:mm:ss).  It will be used to sort the photos.

  * FACLOCID => AKR_ATTACH.FACLOCID

    Optional. A foreign key to the FACLOCID of any spatial record in `akr_facility2`
    This will link this photo to a feature (facility) and location in the geodatabase.
    Multiple foreign keys can be provided, but is usually only done to link the photo
    to several different features.

  * FACASSETID => AKR_ATTACH.FACASSETID

    Optional. A foreign key to the FACASSETID of any spatial record in `akr_facility2`
    This will link this photo to a feature (facility) and location in the geodatabase.
    Multiple foreign keys can be provided, but is usually only done to link the photo
    to several different features.

  * FEATUREID => AKR_ATTACH.FEATUREID

    Optional. A foreign key to the FEATUREID of any spatial record in `akr_facility2`
    This will link this photo to a feature (facility) and location in the geodatabase.
    Multiple foreign keys can be provided, but is usually only done to link the photo
    to several different features.

  * GEOMETRYID => AKR_ATTACH.GEOMETRYID

    Optional. A foreign key to the GEOMETRYID of any spatial record in `akr_facility2`
    This will link this photo to a feature (facility) and location in the geodatabase.
    Multiple foreign keys can be provided, but is usually only done to link the photo
    to several different features.

  * DESCRIPTION => AKR_ATTACH.ATCHNAME

    Optional. A name or description for the content of this photo.
    If empty it will default to `Photo of Building`.

  * ORIGINALPATH => AKR_ATTACH.ATCHSOURCE (AKR extension)

    Optional. The network location of the original source photo.
    If this is not provided, it is assumed the original photo is in
    `T:\PROJECTS\AKR\FMSS\PHOTOS\ORIGINAL`. Furthermore all photos will be copied from
    the `Original_Photo_Path` to `T:\PROJECTS\AKR\FMSS\PHOTOS\ORIGINAL`, unless it has
    already been copied.

  * CREATEUSER => AKR_ATTACH.CREATEUSER

    Optional. This is the full name (or login name) of the user who added
    this photo to the CSV.  It is useful for resolving any issues that occur during processing.
    If not provided 'AKRO_GIS' will be used, and the photo will be ignored if there are
    processing issues.

  * CREATEDATE => AKR_ATTACH.CREATEDATE

    Optional. This is the date/time the user added the photo to the CSV file.  If not provided,
    It will be the date/time the CSV record is added to the `AKR_ATTACH` table in `akr_facility2`
    It must be an [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601) formatted date/time
    (i.e. YYYY-MM-DDThh:mm:ss)

  * NOTES => AKR_ATTACH.NOTES

    Optional. Any comments about this photo.

Scripts:
========

Compare_Database_photos_To_ORIGINAL_Folder.py
---------------------------------------------
This script can be run at any time, but especially before and after editing
`PhotoCSVLoader.csv`.  The script will compare the files in the folder
`..\ORIGINAL` with the table `AKR_ATTACH` in the  `akr_facility2` geodatabase
and the contents of `PhotoCSVLoader.csv`.  Any photo file in the `..\ORIGINAL`
should be in either the geodatabase, or the csv file.  Editors of the CSV
file are responsible for ensuring that their changes do not introduce errors.

extras
------
Aditional scripts that are no longer required (part of the standard workflow)
but could be useful in some situations.  See the `Readme.md` file in that
folder for details on the scripts therein.

scripts
-------
Additional scripts for processing photos.  See the `Readme.md` file in that
folder for details.  These scripts will typically be run by the PDS
Data Manager when updating the `akr_facility2` geodatabase and website.
