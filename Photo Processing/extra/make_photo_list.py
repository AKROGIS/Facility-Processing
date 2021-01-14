# -*- coding: utf-8 -*-

"""
Creates a CSV list of photos (and select EXIF metadata) for all photos below a folder.

Absolute file paths are hard coded in the script.

Written for Python 2.7; may work with Python 3.x.
"""

from __future__ import print_function

import os
import datetime
import exifread  # https://pypi.python.org/pypi/ExifRead

# C:\Python27\ArcGIS10.5\Scripts\pip.exe --cert "C:\users\resarwas\DOIRootCA.crt" install exifread

# root = "/Users/regan_sarwas/Desktop/photos/"
root = r"T:\PROJECTS\AKR\FMSS\Photos\Original"
# root = os.path.dirname(os.path.abspath(__file__))
# csv = os.path.join(root, "PhotoList.csv")
csv = r"C:\tmp\PhotoList.csv"

with open(csv, "w") as f:
    f.write("folder,photo,id,namedate,exifdate,lat,lon,gpsdate,size,filedate\n")
    for root, dirs, files in os.walk(root):
        folder = os.path.basename(root)
        # folder = root.replace(start, '.')
        for skipdir in [
            "thumbs",
            "webphotos",
            "thumb",
            "web-photo",
            "web-photos",
            "All_Buildings_V6.gdb",
        ]:
            if skipdir in dirs:
                dirs.remove(skipdir)
        for filename in files:
            base, extension = os.path.splitext(filename)
            if extension.lower() == ".jpg":
                path = os.path.join(root, filename)
                newbase = base.lower().replace("_", "-")
                if -1 < newbase.find("-tag"):
                    newbase = newbase.replace("-tag", "")
                if -1 < newbase.find("-thm"):
                    newbase = newbase.replace("-thm", "")
                try:
                    code, namedate = newbase.split("-", 1)
                except ValueError:
                    code, namedate = newbase, ""
                size = os.path.getsize(path)
                lat, lon, exifdate, gpsdate = "", "", "", ""
                with open(path, "rb") as pf:
                    tags = exifread.process_file(pf, details=False)
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
                    except KeyError:
                        pass
                    except ZeroDivisionError:
                        pass
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
                    except KeyError:
                        pass
                    except ZeroDivisionError:
                        pass
                    try:
                        time = tags["EXIF DateTimeOriginal"].values
                        # exifdate = time.replace(':', '').replace(' ', 'T') #compact iso format
                        exifdate = time.replace(
                            ":", "-", 2
                        )  # microsoft excel acceptable ISO format
                    except KeyError:
                        pass
                    try:
                        date = tags["GPS GPSDate"].values
                        time = tags["GPS GPSTimeStamp"].values
                        if date:
                            # gpsdate = '{0}T{1}{2}{3}'.format(date.replace(':', ''),
                            #                                 time[0], time[1], float(time[2].num)/time[2].den)
                            gpsdate = "{0} {1}:{2}:{3}".format(
                                date.replace(":", "-"),
                                time[0],
                                time[1],
                                float(time[2].num) / time[2].den,
                            )
                        else:
                            gpsdate = ""
                    except KeyError:
                        pass
                filedate = datetime.datetime.fromtimestamp(
                    os.path.getmtime(path)
                ).isoformat()
                filedate = filedate.replace(
                    "T", " "
                )  # microsoft excel acceptable ISO format
                f.write(
                    "{0},{1},{2},{3},{4},{5},{6},{7},{8},{9}\n".format(
                        folder,
                        filename,
                        code,
                        namedate,
                        exifdate,
                        lat,
                        lon,
                        gpsdate,
                        size,
                        filedate,
                    )
                )
