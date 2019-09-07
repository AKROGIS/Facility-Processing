# -*- coding: utf-8 -*-

"""Creates and updates a collection of web photos (with annotation) for photos listed in a CSV

It assumes that the photos are in the AKR_ATTACH table and they have a link to an
FMSS feature for annotation details.

author: Regan Sarwas, GIS Team, Alaska Region, National Park Service"
email: regan_sarwas@nps.gov"
"""

import sys
import os

try:
    import pyodbc
except ImportError:
    pyodbc = None
    pydir = os.path.dirname(sys.executable)
    print 'pyodbc module not found, make sure it is installed with'
    print pydir + r'\Scripts\pip.exe install pyodbc'
    print 'Don''t have pip?'
    print 'Download <https://bootstrap.pypa.io/get-pip.py> to ' + pydir + r'\Scripts\get-pip.py'
    print 'Then run'
    print sys.executable + ' ' + pydir + r'\Scripts\get-pip.py'
    sys.exit()


try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    Image, ImageDraw, ImageFont = None, None, None
    pydir = os.path.dirname(sys.executable)
    print 'PIL module not found, make sure it is installed with'
    print pydir + r'\Scripts\pip.exe install Pillow'
    print 'Don''t have pip?'
    print 'Download <https://bootstrap.pypa.io/get-pip.py> to ' + pydir + r'\Scripts\get-pip.py'
    print 'Then run'
    print sys.executable + ' ' + pydir + r'\Scripts\get-pip.py'
    sys.exit()

import apply_orientation  # dependency on PIL


def get_connection_or_die(server, db):
    # See https://github.com/mkleehammer/pyodbc/wiki/Connecting-to-SQL-Server-from-Windows
    drivers = [ '{ODBC Driver 17 for SQL Server}',    # supports SQL Server 2008 through 2017
                '{ODBC Driver 13.1 for SQL Server}',  # supports SQL Server 2008 through 2016
                '{ODBC Driver 13 for SQL Server}',    # supports SQL Server 2005 through 2016
                '{ODBC Driver 11 for SQL Server}',    # supports SQL Server 2005 through 2014
                '{SQL Server Native Client 11.0}',    # DEPRECATED: released with SQL Server 2012
                # '{SQL Server Native Client 10.0}',    # DEPRECATED: released with SQL Server 2008
    ]
    conn_template = "DRIVER={0};SERVER={1};DATABASE={2};Trusted_Connection=Yes;"
    for driver in drivers:
        conn_string = conn_template.format(driver, server, db)
        try:
            connection = pyodbc.connect(conn_string)
            return connection
        except pyodbc.Error:
            pass
    print("Rats!! Unable to connect to the database.")
    print("Make sure you have an ODBC driver installed for SQL Server")
    print("and your AD account has the proper DB permissions.")
    print("Contact regan_sarwas@nps.gov for assistance.")
    sys.exit()


def shadow(ul, wh, offset, fontsize):
    newul = (ul[0] - offset, ul[1] - offset + fontsize * .15)
    newlr = (ul[0] + wh[0] + offset, ul[1] + fontsize + offset)
    return [newul, newlr]


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
        latdir = 'S'
        latstr = latstr[1:]
    else:
        latdir = 'N'
    if lon < 0:
        londir = 'W'
        lonstr = lonstr[1:]
    else:
        londir = 'E'

    return u"{0} {1}°  {2} {3}°".format(latdir, latstr, londir, lonstr)


def annotate(image, data, config):
    unit, tag, lat, lon, date, desc = data
    font = config['font']
    fontsize = config['fontsize']
    margin = config['margin']
    white = config['whites'][image.mode]
    black = config['blacks'][image.mode]

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
    if not os.path.isfile(path):
        return False
    ext = os.path.splitext(path)[1].lower()
    return ext in ['.jpg', '.jpeg']


def parks(parent):
    return [f for f in os.listdir(parent) if os.path.isdir(os.path.join(parent, f))]


def folders(start_dir):
    start_dir = start_dir + '\\'
    results = []
    for root, dirs, files in os.walk(start_dir):
        relative_path = root.replace(start_dir, '')
        for d in dirs:
                results.append(os.path.join(relative_path, d))
    return results


def photos(parkdir):
    return [f for f in os.listdir(parkdir) if is_jpeg(os.path.join(parkdir, f))]


def get_photo_data(conn, park, photo):
    # Park is the relative path to a folder containing photo
    # Do not assume that park is only the UNITCODE (this was an old convention and we now have subfolders)
    try:
        row = conn.cursor().execute("""
             SELECT p.UNITCODE as unit
                   ,COALESCE(p.FACLOCID, COALESCE(p.FACASSETID, COALESCE(p.FEATUREID, 'no id'))) AS tag
			       ,fc.lat,  fc.lon
                   ,LEFT(p.ATCHDATE,19) AS [date]
				   ,COALESCE(a.[description], COALESCE(f.[description], COALESCE(fc.MAPLABEL, COALESCE(fc.[NAME], 'no name')))) AS [desc]
               FROM gis.AKR_ATTACH_evw as p
          LEFT JOIN dbo.FMSSEXPORT as f
                 ON f.Location = P.FACLOCID
          LEFT JOIN dbo.FMSSExport_Asset as a
                 ON a.Asset = p.FACASSETID
          LEFT JOIN (SELECT FACLOCID, FACASSETID, FEATUREID, GEOMETRYID, MAPLABEL, BLDGNAME AS NAME, Shape.STY as lat, Shape.STX as lon from gis.AKR_BLDG_CENTER_PT_evw
		             union all
		             SELECT FACLOCID, FACASSETID, FEATUREID, GEOMETRYID, MAPLABEL, TRLFEATNAME AS NAME, Shape.STY as lat, Shape.STX as lon from gis.TRAILS_FEATURE_PT_evw
		             union all
		             SELECT FACLOCID, FACASSETID, FEATUREID, GEOMETRYID, MAPLABEL, TRLNAME AS NAME, Shape.STStartPoint().STY as lat, Shape.STStartPoint().STX as lon from gis.TRAILS_LN_evw
		             union all
		             SELECT FACLOCID, FACASSETID, FEATUREID, GEOMETRYID, MAPLABEL, RDNAME AS NAME, Shape.STStartPoint().STY as lat, Shape.STStartPoint().STX as lon from gis.ROADS_LN_evw
		             union all
		             SELECT FACLOCID, FACASSETID, FEATUREID, GEOMETRYID, MAPLABEL, LOTNAME AS NAME, Shape.STCentroid().STY as lat, Shape.STCentroid().STX as lon from gis.PARKLOTS_PY_evw
					 )
				 AS fc
                 ON fc.FACLOCID = p.FACLOCID OR fc.FACASSETID = p.FACASSETID OR fc.FEATUREID = p.FEATUREID OR fc.GEOMETRYID = p.GEOMETRYID 
              WHERE p.UNITCODE = ? and p.ATCHALTNAME = ?
                """, (park, photo)).fetchone()
    except pyodbc.Error as de:
        print ("Database error ocurred", de)
        row = None
    if row:
        return park, row.tag, row.lat, row.lon, row.date, row.desc
    return park, 'unknown', 0, 0, None, ''


def make_webphotos(base, config, conn):
    origdir = os.path.join(base, "ORIGINAL")
    webdir = os.path.join(base, "WEB")

    if not os.path.exists(origdir):
        print "Photo directory: " + origdir + " does not exit."
        return

    if not os.path.exists(webdir):
        os.mkdir(webdir)

    for park in folders(origdir):
        print park,
        orig_park_path = os.path.join(origdir, park)
        new_park_path = os.path.join(webdir, park)
        if not os.path.exists(new_park_path):
            os.mkdir(new_park_path)
        for photo in photos(orig_park_path):
            src = os.path.join(orig_park_path, photo)
            dest = os.path.join(new_park_path, photo)
            if os.path.exists(src) and (not os.path.exists(dest) or os.path.getmtime(dest) < os.path.getmtime(dest)):
                try:
                    data = get_photo_data(conn, park, photo)
                    im = Image.open(src)
                    im = apply_orientation.apply_orientation(im)
                    im.thumbnail(config['size'], Image.ANTIALIAS)
                    annotate(im, data, config)
                    im.save(dest)
                    print '.',
                except IOError:
                    print "Cannot create thumbnail for", src


if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Assumes script is in a sub folder of the Processing folder which is sub to the photos base folder.
    base_dir = os.path.dirname(os.path.dirname(script_dir))
    options = {
        'size': (1024, 768),
        'blacks': {'L': 0, 'RGB': (0, 0, 0)},
        'whites': {'L': 255, 'RGB': (255, 255, 255)},
        'margin': 8,
        'fontsize': 18,
        'font': ImageFont.truetype(os.path.join(script_dir, "ARLRDBD.TTF"), 18)
    }
    conn = get_connection_or_die('inpakrovmais', 'akr_facility2')
    make_webphotos(base_dir, options, conn)
