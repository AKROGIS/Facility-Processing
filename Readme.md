# Facility Processing Tools

This is a collection of tools to process the data needed to support
the [Facility Website](https://github.com/AKROGIS/Facilities-Website),
and the now obsolete
[Buildings Website](https://github.com/AKROGIS/Buildings-Website).
It also includes tools to add photos to the facilities database and the web
server.

## Contents

Only the `facilities-website-tools` and `Photo Processing` folders are
currently being used. The others are historical as of 2021.

### `bldgV1_QC`

Obsolete quality control SQL scripts for building data in the old national data
standard.

### `buildings-website-tools`

SQL Scripts to to create the building and photo lists for the website.  These
have been replaced by the Python script (for `buildings.csv`), and the Photo
Processing folder for `photos.json`.

### `facilities-website-tools`

* `Facilities.lyr` - The symbology for the facilities layers in the web mapping
service used in the website.
* `facilities.sql` - A SQL script that needs to be run as a single command. It
will create four results windows which need to be saved as `facilities.csv`,
`assets.csv`, `parents.csv`, and `all_assets.csv` respectively.
* `make_children.py` - A Python script to read `parents.csv` and
  `all_assets.csv` and created `children.json` and `assets.json`.
* `MultiplePhotoIds.sql` - The way that photos can be associated with various
  facilities in different feature classes is very flexible, but that makes it
  very complicated to combine all the possible combinations into a single list
  that can be easily used in a website.  This query helped test the various
  combinations that were eventually used in `facilities.sql`.

See the [Facilities Website](https://github.com/AKROGIS/Facilities-Website)
for details on how the products of these scripts are deployed to make the
website work.

### `FMSS`

Primarily a Python script that was deployed as a scheduled task to make a
nightly request of the FMSS web service to collect data from FMSS for inclusion
in the facilities database and then the website.  Unfortunately, the web
service does not have all the attributes that we need, so we have abandoned
this effort for a manual method as described in the
[FMSS Export Instructions](https://github.com/AKROGIS/Enterprise-QC/blob/master/FMSSExport/FMSS%20Export%20Instructions.md)
in the [Enterprise QC](https://github.com/AKROGIS/Enterprise-QC) repo.

### `misc-tools`

ArcGIS snippets to select only those buildings without an FMSS relationship
(`NOFMSS.exp`) and to do a field calc to create a GUID (`addGUID.cal`).
Not really needed for the website, but here they are anyway :smile:.

### `Photo Processing`

Tools for processing photo files into a list of photos to be inserted into the
database, and copied to the web server. It also has tools for
creating the `photos.json` file that is deployed to the website and powers the
photo part of the facilities website.  See the
[Readme](./Photo%20Processing/readme.md)
and [workflow](./Photo%20Processing/workflow.md)
documents in the folder for more details.

This folder is also deployed to the GIS Team drive with the facility related
photos.


## Build

There is nothing to build to use these tools.

## Deploy

These tools do not need to be deployed.  Just clone this repository
to a local file system.

## Use

### Python

Before executing a python script, open it in a text editor and check any
path or file names in the script that should be edited to reflect the 
file system where the script and data are deployed.  The script can then
be run in a CMD/Powershell window, with the
[IDLE](https://en.wikipedia.org/wiki/IDLE) application,
with the
[Python extension to VS Code](https://code.visualstudio.com/docs/languages/python), 
or any other Python execution environment.

### SQL Scripts

1) Open the script file in SQL Server Management Studio
([SSMS](https://docs.microsoft.com/en-us/sql/ssms/download-sql-server-management-studio-ssms?view=sql-server-ver15)),
or [Azure Data Studio](https://docs.microsoft.com/en-us/sql/azure-data-studio/download-azure-data-studio?view=sql-server-ver15).
2) Connect to the appropriate server and database.
3) Select the statement you want to run and click `Run` in the toolbar.
   When applicable, see the comments in the file, you can run all the SQL
   commands in the file sequentially by clicking `Run` when nothing is selected.
