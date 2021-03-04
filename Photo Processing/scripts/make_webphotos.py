# -*- coding: utf-8 -*-
"""
Creates and updates a collection of web photos (with annotation) for photos listed in a CSV.

It assumes that the photos are in the AKR_ATTACH table and they have a link to an
FMSS feature for annotation details.

File paths are hard coded in the script relative to the scipt's location.
The database connection string and schema are also hardcoded in the script.

Written for Python 2.7; may work with Python 3.x.

Third party requirements:
* pyodbc - https://pypi.python.org/pypi/pyodbc
* Pillow (PIL) - https://pypi.python.org/pypi/Pillow
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import os
import sys

import pyodbc
from PIL import Image, ImageDraw, ImageFont, ExifTags


def get_connection_or_die(server, database):
    """
    Get a Trusted pyodbc connection to the SQL Server database on server.

    Try several connection strings.
    See https://github.com/mkleehammer/pyodbc/wiki/Connecting-to-SQL-Server-from-Windows

    Exit with an error message if there is no successful connection.
    """
    drivers = [
        "{ODBC Driver 17 for SQL Server}",  # supports SQL Server 2008 through 2017
        "{ODBC Driver 13.1 for SQL Server}",  # supports SQL Server 2008 through 2016
        "{ODBC Driver 13 for SQL Server}",  # supports SQL Server 2005 through 2016
        "{ODBC Driver 11 for SQL Server}",  # supports SQL Server 2005 through 2014
        "{SQL Server Native Client 11.0}",  # DEPRECATED: released with SQL Server 2012
        # '{SQL Server Native Client 10.0}',    # DEPRECATED: released with SQL Server 2008
    ]
    conn_template = "DRIVER={0};SERVER={1};DATABASE={2};Trusted_Connection=Yes;"
    for driver in drivers:
        conn_string = conn_template.format(driver, server, database)
        try:
            connection = pyodbc.connect(conn_string)
            return connection
        except pyodbc.Error:
            pass
    print("Rats!! Unable to connect to the database.")
    print("Make sure you have an ODBC driver installed for SQL Server")
    print("and your AD account has the proper DB permissions.")
    print("Contact akro_gis_helpdesk@nps.gov for assistance.")
    sys.exit()


def shadow(origin, size, offset, fontsize):
    """Return the bounding box for a text shadow."""
    left, upper = origin
    width, _ = size
    upper_left = (left - offset, upper - offset + fontsize * 0.15)
    lower_right = (left + width + offset, upper + fontsize + offset)
    return [upper_left, lower_right]


def datestr(date):
    """date is a ISO formated date time string"""
    if not date:
        return "No Date/Time"
    return date


def latlonstr(lat, lon):
    """lat and len are floats"""
    if not lat or not lon:
        return "Location unknown"

    latstr = "{:.6f}".format(lat)
    lonstr = "{:.6f}".format(lon)

    if lat < 0:
        latdir = "S"
        latstr = latstr[1:]
    else:
        latdir = "N"
    if lon < 0:
        londir = "W"
        lonstr = lonstr[1:]
    else:
        londir = "E"

    return "{0} {1}°  {2} {3}°".format(latdir, latstr, londir, lonstr)


def annotate(image, data, config):
    """Add annotations to the image using the data formatted per config."""

    # pylint: disable=too-many-locals

    unit, tag, lat, lon, date, desc = data
    font = config["font"]
    fontsize = config["fontsize"]
    margin = config["margin"]
    white = config["whites"][image.mode]
    black = config["blacks"][image.mode]

    newsize = image.size  # may be smaller than the thumbnail size
    draw = ImageDraw.Draw(image)
    if not tag:
        tag = "Unknown FMSS ID"
    if unit:
        text = unit + " - " + tag
    else:
        text = tag
    textsize = font.getsize(text)
    origin = (margin, newsize[1] - 2 * (margin + fontsize))
    rect = shadow(origin, textsize, 1, fontsize)
    draw.rectangle(rect, black, black)
    draw.text(origin, text, white, font)

    if desc:
        text = desc
    else:
        text = unit
    textsize = font.getsize(text)
    origin = (newsize[0] - textsize[0] - margin, newsize[1] - 2 * (margin + fontsize))
    rect = shadow(origin, textsize, 1, fontsize)
    draw.rectangle(rect, black, black)
    draw.text(origin, text, white, font)

    text = latlonstr(lat, lon)
    textsize = font.getsize(text)
    origin = (margin, newsize[1] - margin - fontsize)
    rect = shadow(origin, textsize, 1, fontsize)
    draw.rectangle(rect, black, black)
    draw.text(origin, text, white, font)

    text = datestr(date)
    textsize = font.getsize(text)
    origin = (newsize[0] - textsize[0] - margin, newsize[1] - margin - fontsize)
    rect = shadow(origin, textsize, 1, fontsize)
    draw.rectangle(rect, black, black)
    draw.text(origin, text, white, font)

    del draw


def is_jpeg(path):
    """Return True if the file at path is a JPEG photo file."""
    if not os.path.isfile(path):
        return False
    ext = os.path.splitext(path)[1].lower()
    return ext in [".jpg", ".jpeg"]


def get_folders(start_dir):
    """Find all the folders below start_dir."""
    start_dir = start_dir + "\\"
    results = []
    for root, folders, _ in os.walk(start_dir):
        relative_path = root.replace(start_dir, "")
        for folder in folders:
            results.append(os.path.join(relative_path, folder))
    return results


def get_photos(parkdir):
    """Return a list of all the photo files in folder."""
    return [f for f in os.listdir(parkdir) if is_jpeg(os.path.join(parkdir, f))]


def get_photo_data(conn, park, photo):
    """Get data for photo in park from the database at conn.

    park is the relative path to a folder containing photo
    Do not assume that park is only the UNITCODE (this was an old
    convention and we now have subfolders)
    """
    search_term = "%/web/" + park.replace("\\", "/") + "/" + photo
    try:
        # FIXME - This query is really slow. I suspect the ORs in the JOIN clause,
        # and unioning many feature classes
        row = (
            conn.cursor()
            .execute(
                """
             SELECT fc.UNITCODE as unit
                   ,COALESCE(a.Location +'/'+ a.Asset, COALESCE(f.Location, 'No FMSS ID')) AS tag
			       ,fc.lat,  fc.lon
                   ,LEFT(p.ATCHDATE,19) AS [date]
				   ,COALESCE(fc.MAPLABEL,
                             COALESCE(fc.[Name],
                                      COALESCE(a.[description],
                                               COALESCE(f.[description], 'no name')))) AS [desc]
               FROM gis.AKR_ATTACH_evw as p
          LEFT JOIN (SELECT UNITCODE, FACLOCID, FACASSETID, FEATUREID, GEOMETRYID,
                            MAPLABEL, BLDGNAME AS NAME, Shape.STY as lat,
                            Shape.STX as lon from gis.AKR_BLDG_CENTER_PT_evw
		             union all
		             SELECT UNITCODE, FACLOCID, FACASSETID, FEATUREID, GEOMETRYID, MAPLABEL,
                            CASE WHEN TRLFEATTYPE = 'Other'
                                 THEN TRLFEATTYPEOTHER
                                 ELSE TRLFEATTYPE
                            END +
                            CASE WHEN TRLFEATSUBTYPE is NULL
                                 THEN ''
                                 ELSE ', ' + TRLFEATSUBTYPE
                            END AS [Name],
                            Shape.STY as lat, Shape.STX as lon from gis.TRAILS_FEATURE_PT_evw
		             union all
		             SELECT UNITCODE, FACLOCID, FACASSETID, FEATUREID, GEOMETRYID,
                            MAPLABEL, TRLNAME AS NAME, Shape.STStartPoint().STY as lat,
                            Shape.STStartPoint().STX as lon from gis.TRAILS_LN_evw
		             union all
		             SELECT UNITCODE, FACLOCID, FACASSETID, FEATUREID, GEOMETRYID,
                            MAPLABEL, RDNAME AS NAME, Shape.STStartPoint().STY as lat,
                            Shape.STStartPoint().STX as lon from gis.ROADS_LN_evw
		             union all
		             SELECT UNITCODE, FACLOCID, FACASSETID, FEATUREID, GEOMETRYID,
                            MAPLABEL, LOTNAME AS NAME, Shape.STCentroid().STY as lat,
                            Shape.STCentroid().STX as lon from gis.PARKLOTS_PY_evw
		             union all
                     SELECT UNITCODE, FACLOCID, FACASSETID, FEATUREID, GEOMETRYID,
                            MAPLABEL, ASSETNAME AS NAME, Shape.STY as lat,
                            Shape.STX as lon from gis.AKR_ASSET_PT_evw
					 )
				 AS fc
                 ON fc.FACLOCID = p.FACLOCID OR fc.FACASSETID = p.FACASSETID
                 OR fc.FEATUREID = p.FEATUREID OR fc.GEOMETRYID = p.GEOMETRYID
          LEFT JOIN dbo.FMSSEXPORT as f
                 ON f.Location = fc.FACLOCID
          LEFT JOIN dbo.FMSSExport_Asset as a
                 ON a.Asset = fc.FACASSETID
              WHERE p.ATCHLINK LIKE ?
                """,
                search_term,
            )
            .fetchone()
        )
    except pyodbc.Error as ex:
        print("Database error ocurred", ex)
        row = None
    if row:
        return row.unit, row.tag, row.lat, row.lon, row.date, row.desc
    return park, "unknown", 0, 0, None, ""


def apply_orientation(image):
    """Returns a correctly rotated image per the EXIF data."""

    # pylint: disable=protected-access
    # consider using exifread instead https://pypi.org/project/ExifRead/

    orientation = None
    try:
        for orientation in ExifTags.TAGS:
            if ExifTags.TAGS[orientation] == "Orientation":
                break

        exif = image._getexif()

        if exif[orientation] == 3:
            image = image.rotate(180, expand=True)
        elif exif[orientation] == 6:
            image = image.rotate(270, expand=True)
        elif exif[orientation] == 8:
            image = image.rotate(90, expand=True)
    except (AttributeError, KeyError, IndexError):
        # image doesn't have orientation exif
        pass
    return image


def make_webphotos(base, config, conn):
    """Make web sized photos below base with data from conn."""
    origdir = os.path.join(base, "ORIGINAL")
    webdir = os.path.join(base, "WEB")

    if not os.path.exists(origdir):
        print("Photo directory: " + origdir + " does not exit.")
        return

    if not os.path.exists(webdir):
        os.mkdir(webdir)

    for park in get_folders(origdir):
        print(park, end="")
        orig_park_path = os.path.join(origdir, park)
        new_park_path = os.path.join(webdir, park)
        if not os.path.exists(new_park_path):
            os.mkdir(new_park_path)
        for photo in get_photos(orig_park_path):
            src = os.path.join(orig_park_path, photo)
            dest = os.path.join(new_park_path, photo)
            if os.path.exists(src) and (
                not os.path.exists(dest)
                or os.path.getmtime(dest) < os.path.getmtime(dest)
            ):
                try:
                    data = get_photo_data(conn, park, photo)
                    image = Image.open(src)
                    image = apply_orientation(image)
                    image.thumbnail(config["size"], Image.ANTIALIAS)
                    annotate(image, data, config)
                    image.save(dest)
                    print(".", end="")
                except IOError:
                    print("Cannot create thumbnail for", src)


def main():
    """Make web sized photos with Config parameters."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Assumes script is in a sub folder of the Processing folder
    # which is sub to the photos base folder.
    base_dir = os.path.dirname(os.path.dirname(script_dir))
    # base_dir = r'C:\tmp\facility_photos\test'
    options = {
        "size": (1024, 768),
        "blacks": {"L": 0, "RGB": (0, 0, 0)},
        "whites": {"L": 255, "RGB": (255, 255, 255)},
        "margin": 8,
        "fontsize": 18,
        "font": ImageFont.truetype(os.path.join(script_dir, "ARLRDBD.TTF"), 18),
    }
    conn = get_connection_or_die("inpakrovmais", "akr_facility2")
    make_webphotos(base_dir, options, conn)


if __name__ == "__main__":
    main()
