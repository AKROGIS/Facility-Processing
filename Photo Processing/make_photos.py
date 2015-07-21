#!/usr/bin/env python
# -*- coding: latin-1 -*-

"""Creates and updates a collection of web photos (with annotation) for photos listed in a CSV"""

__author__ = "Regan Sarwas, GIS Team, Alaska Region, National Park Service"
__email__ = "regan_sarwas@nps.gov"
__copyright__ = "Public Domain - product of the US Government"


import sys
import os

# dependency PIL (now maintained as Pillow)
# C:\Python27\ArcGIS10.3\Scripts\pip.exe install Pillow

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    Image, ImageDraw, ImageFont = None, None, None
    print 'PIL module not found, make sure it is installed with'
    print 'C:\Python27\ArcGIS10.3\Scripts\pip.exe install Pillow'
    sys.exit()

import apply_orientation  # dependency on PIL


import dateutil.parser
import dateutil.tz


def shadow(ul, wh, offset, fontsize):
    newul = (ul[0] - offset, ul[1] - offset + fontsize * .15)
    newlr = (ul[0] + wh[0] + offset, ul[1] + fontsize + offset)
    return [newul, newlr]


def datestr(date):
    if not date or len(date) < 14:
        return "No Date/Time"
    try:
        d = dateutil.parser.parse(date)
        if date[-1:] == 'Z':
            d = d.astimezone(dateutil.tz.tzlocal())
        return '{:%Y-%m-%d %I:%M:%S%p}'.format(d)
    except ValueError:
        return "Date/Time unknown"


def latlonstr(lat, lon):
    """lat and len are string representations of floats"""
    if not lat or not lon:
        return "Location unknown"
    if lat[0] == '-':
        latdir = 'S'
        lat = lat[1:]
    else:
        latdir = 'N'
    if lon[0] == '-':
        londir = 'W'
        lon = lon[1:]
    else:
        londir = 'E'

    if len(lat) < 9:
        latstr = lat
    else:
        latstr = "{:.6f}".format(float(lat))
    if len(lon) < 10:
        lonstr = lon
    else:
        lonstr = "{:.6f}".format(float(lon))
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


def get_photo_data(park, photo):
    # FIXME: get this data from the database
    tag, lat, lon, date, desc = '123', '123', '123', '123', photo
    return park, tag, lat, lon, date, desc


def make_webphotos(base, config):
    origdir = os.path.join(base, "ORIGINAL")
    webdir = os.path.join(base, "WEB")

    if not os.path.exists(origdir):
        print "Photo directory: " + origdir + " does not exit."
        return

    if not os.path.exists(webdir):
        os.mkdir(webdir)

    for park in parks(origdir):
        orig_park_path = os.path.join(origdir, park)
        new_park_path = os.path.join(webdir, park)
        if not os.path.exists(new_park_path):
            os.mkdir(new_park_path)
        for photo in photos(orig_park_path):
            src = os.path.join(orig_park_path, photo)
            dest = os.path.join(new_park_path, photo)
            if os.path.exists(src) and (not os.path.exists(dest) or os.path.getmtime(dest) < os.path.getmtime(dest)):
                try:
                    data = get_photo_data(park, photo)
                    im = Image.open(src)
                    im = apply_orientation.apply_orientation(im)
                    im.thumbnail(config['size'], Image.ANTIALIAS)
                    annotate(im, config, data)
                    im.save(dest)
                except IOError:
                    print "Cannot create thumbnail for", src


if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)
    options = {
        'size': (1024, 768),
        'blacks': {'L': 0, 'RGB': (0, 0, 0)},
        'whites': {'L': 255, 'RGB': (255, 255, 255)},
        'margin': 8,
        'fontsize': 18,
        'font': ImageFont.truetype(os.path.join(script_dir, "ARLRDBD.TTF"), 18)
    }
    make_webphotos(base_dir, options)
