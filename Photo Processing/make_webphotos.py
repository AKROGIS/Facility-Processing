# -*- coding: utf-8 -*-

"""Creates and updates a collection of web photos (with annotation) for photos listed in a CSV

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


def get_connection_or_die():
    conn_string = ("DRIVER={{SQL Server Native Client 11.0}};"
                   "SERVER={0};DATABASE={1};Trusted_Connection=Yes;")
    conn_string = conn_string.format('inpakrovmais', 'akr_facility')
    try:
        connection = pyodbc.connect(conn_string)
        return connection
    except pyodbc.Error:
        # Try to alternative connection string for 2008
        conn_string2 = conn_string.replace('SQL Server Native Client 11.0', 'SQL Server Native Client 10.0')
    try:
        connection = pyodbc.connect(conn_string)
        return connection
    except pyodbc.Error as e:
        # Additional alternatives are 'SQL Native Client' (2005) and 'SQL Server' (2000)
        print("Rats!!  Unable to connect to the database.")
        print("Make sure you have the SQL Server Client installed and")
        print("your AD account has the proper DB permissions.")
        print("Contact regan_sarwas@nps.gov for assistance.")
        print("  Connection: " + conn_string)
        print("         and: " + conn_string2)
        print("  Error: " + e[1])
        sys.exit()


def shadow(ul, wh, offset, fontsize):
    newul = (ul[0] - offset, ul[1] - offset + fontsize * .15)
    newlr = (ul[0] + wh[0] + offset, ul[1] + fontsize + offset)
    return [newul, newlr]


def datestr(date):
    """date is a datetime object"""
    if not date:
        return "No Date/Time"
    return '{:%Y-%m-%d %I:%M:%S%p}'.format(date)


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

    return "{0} {1}°  {2} {3}°".format(latdir, latstr, londir, lonstr)


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
    if desc:
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


def photos(parkdir):
    return [f for f in os.listdir(parkdir) if is_jpeg(os.path.join(parkdir, f))]


def get_photo_data(conn, park, photo):
    try:
        row = conn.cursor().execute("""
             SELECT B.FACLOCID as tag, B.Shape.STY as lat,  B.Shape.STX as lon,
                    P.ATCHDATE as [date], B.MAPLABEL as [desc]
               FROM gis.AKR_ATTACH_evw as P
          LEFT JOIN gis.AKR_BLDG_CENTER_PT_evw as B
                 ON B.FACLOCID = P.FACLOCID OR B.FACASSETID = P.FACASSETID OR B.FEATUREID = P.FEATUREID OR B.GEOMETRYID = P.GEOMETRYID 
          LEFT JOIN dbo.FMSSEXPORT as F
                 ON f.Location = B.FACLOCID
              WHERE F.Asset_Code = 4100
                AND P.UNITCODE = ? and P.ATCHALTNAME = ?
                """, (park, photo)).fetchone()
    except pyodbc.Error as de:
        print ("Database error ocurred", de)
        row = None
    if row:
        return park, row.tag, row.lat, row.lon, row.date, row.desc
    return park, 'unknown', 0, 0, None, ''


def make_webphotos(base, config):
    origdir = os.path.join(base, "ORIGINAL")
    webdir = os.path.join(base, "WEB")
    conn = get_connection_or_die()

    if not os.path.exists(origdir):
        print "Photo directory: " + origdir + " does not exit."
        return

    if not os.path.exists(webdir):
        os.mkdir(webdir)

    for park in parks(origdir):
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
    make_webphotos(base_dir, options)
