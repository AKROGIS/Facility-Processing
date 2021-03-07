# -*- coding: utf-8 -*-
"""
Creates a CSV list of photos (and select EXIF metadata) for all photos below a folder.

The CSV file will have the following columns:

folder,photo,id,namedate,exifdate,lat,lon,gpsdate,size,filedate

photo - the filename of the photo (any file with a `.jpg` extension)
folder - the sub folder under `Config.photo_root` containing the photo
id - the FMSS id encoded in the filename assuming `id-date-*.jpg`
namedate - the photo date encoded in the filename
exifdate - the date the photo was taken as encoded in the EXIF data
lat - the latitude of the photo location as encoded in the EXIF data
lon - the longitude of the photo location as encoded in the EXIF data
gpsdate - the date (in UTC) the photo was taken as encoded in the EXIF data
size - the size (in bytes) of the photo file
filedate - the file systems last modified date for the photo file

Written for Python 2.7; may work with Python 3.x.

A version of this script without the specific requirements of the
FMSS photo processing is at
https://github.com/AKROGIS/Misc_Scripts/blob/master/attributes_of_photo_files.py


Third party requirements:
* exifread - https://pypi.python.org/pypi/ExifRead
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import csv
import datetime
from io import open
import os

import exifread

import csv23


class Config(object):
    """Namespace for configuration parameters. Edit as needed."""

    # pylint: disable=useless-object-inheritance,too-few-public-methods

    # The path to the CSV file to create.
    csv_path = r"C:\tmp\PhotoList.csv"

    # Photo root - the absolute path prexix for the data in the CSV
    # can be NULL and then the path in the CSV is either absolute or relative.
    photo_root = r"T:\PROJECTS\AKR\FMSS\PHOTOS\ORIGINAL"

    # A list of sub folder names to skip (based on the GeoJot process)
    skip_dirs = [
        "thumbs",
        "webphotos",
        "thumb",
        "web-photo",
        "web-photos",
        "All_Buildings_V6.gdb",
    ]


def get_name_parts(name):
    """Splits the name into a code and a date.

    name is a file name without extension.
    """
    name_date = ""
    new_name = name.lower().replace("_", "-")
    if -1 < new_name.find("-tag"):
        new_name = new_name.replace("-tag", "")
    if -1 < new_name.find("-thm"):
        new_name = new_name.replace("-thm", "")
    try:
        code, name_date = new_name.split("-", 1)
    except ValueError:
        code = new_name
    return code, name_date


def get_latitude(tags):
    """Return the latitude found in the EXIF tags."""

    lat = ""
    try:
        dms = tags["GPS GPSLatitude"].values
        deg = float(dms[0].num) / dms[0].den
        minute = float(dms[1].num) / dms[1].den
        sec = float(dms[2].num) / dms[2].den
        if tags["GPS GPSLatitudeRef"].values == "N":
            sign = 1
        else:
            sign = -1
        lat = sign * (deg + (minute + sec / 60) / 60)
        if lat == 0:
            lat = ""
    except (KeyError, ZeroDivisionError):
        pass
    return lat


def get_longitude(tags):
    """Return the latitude found in the EXIF tags."""

    lon = ""
    try:
        dms = tags["GPS GPSLongitude"].values
        deg = float(dms[0].num) / dms[0].den
        minute = float(dms[1].num) / dms[1].den
        sec = float(dms[2].num) / dms[2].den
        if tags["GPS GPSLongitudeRef"].values == "E":
            sign = 1
        else:
            sign = -1
        lon = sign * (deg + (minute + sec / 60) / 60)
        if lon == 0:
            lon = ""
    except (KeyError, ZeroDivisionError):
        pass
    return lon


def get_exif_date(tags):
    """Return the camera date as found in the EXIF tags."""

    exif_date = ""
    try:
        time = tags["EXIF DateTimeOriginal"].values
        # exif_date = time.replace(':', '').replace(' ', 'T') #compact iso format
        exif_date = time.replace(":", "-", 2)  # microsoft excel acceptable ISO format
    except KeyError:
        pass

    return exif_date


def get_gps_date(tags):
    """Return the GPS date found in the EXIF tags."""

    gps_date = ""
    try:
        date = tags["GPS GPSDate"].values
        time = tags["GPS GPSTimeStamp"].values
        if date:
            # gps_date = '{0}T{1}{2}{3}'.format(date.replace(':', ''),
            # time[0], time[1], float(time[2].num)/time[2].den)
            gps_date = "{0} {1}:{2}:{3}".format(
                date.replace(":", "-"),
                time[0],
                time[1],
                float(time[2].num) / time[2].den,
            )
        else:
            gps_date = ""
    except KeyError:
        pass
    return gps_date


def create_csv(csv_path, folder):
    """Create a CSV file describing all the photos in folder."""

    # pylint: disable=too-many-locals

    header = "folder,photo,id,namedate,exifdate,lat,lon,gpsdate,size,filedate"
    with csv23.open(csv_path, "w") as csv_file:
        csv_writer = csv.writer(csv_file)
        csv23.write(csv_writer, header.split(","))
        for root, dirs, files in os.walk(root):
            folder = os.path.basename(root)
            # Remove the skip dirs from the current sub directories
            for skipdir in Config.skip_dirs:
                if skipdir in dirs:
                    dirs.remove(skipdir)
            for filename in files:
                base, extension = os.path.splitext(filename)
                if extension.lower() == ".jpg":
                    code, name_date = get_name_parts(base)
                    path = os.path.join(root, filename)
                    size = os.path.getsize(path)
                    with open(path, "rb") as in_file:
                        # exifread wants binary data
                        tags = exifread.process_file(in_file, details=False)
                        lat = get_latitude(tags)
                        lon = get_longitude(tags)
                        exif_date = get_exif_date(tags)
                        gps_date = get_gps_date(tags)
                    file_date = datetime.datetime.fromtimestamp(
                        os.path.getmtime(path)
                    ).isoformat()
                    # convert date to a microsoft excel acceptable ISO format
                    file_date = file_date.replace("T", " ")
                    row = [
                        folder,
                        filename,
                        code,
                        name_date,
                        exif_date,
                        lat,
                        lon,
                        gps_date,
                        size,
                        file_date,
                    ]
                    csv23.write(csv_writer, row)


create_csv(Config.csv_path, Config.photo_root)
