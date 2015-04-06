#!/usr/bin/env python
# -*- coding: latin-1 -*-

"""Creates and updates a collection of web photos (with annotation) for photos listed in a CSV"""

__author__ = "Regan Sarwas, GIS Team, Alaska Region, National Park Service"
__email__ = "regan_sarwas@nps.gov"
__copyright__ = "Public Domain - product of the US Government"

from PIL import Image, ImageDraw, ImageFont
import os
import os.path
import csv
import dateutil.parser
import dateutil.tz

import apply_orientation

root = os.path.dirname(os.path.abspath(__file__))
photo_csv = os.path.join(root, "PhotoListWithId.csv")
bldg_csv = os.path.join(root, "BuildingLocations.csv")
photo_dir = os.path.join(root, "web")

size = (1024, 768)
blacks = {'L': 0, 'RGB': (0, 0, 0)}
whites = {'L': 255, 'RGB': (255, 255, 255)}
margin = 8
fontsize = 18
font = ImageFont.truetype(os.path.join(root, "ARLRDBD.TTF"), fontsize)


def shadow(ul, wh, offset):
    newul = (ul[0]-offset, ul[1]-offset+fontsize*.15)
    newlr = (ul[0]+wh[0]+offset, ul[1]+fontsize+offset)
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


def annotate(image, unit, tag, lat, lon, date, desc):
    white = whites[image.mode]
    black = blacks[image.mode]
    newsize = image.size  # may be smaller than the thumbnail size
    draw = ImageDraw.Draw(image)
    if not tag:
        tag = "Unknown FMSS ID"
    if desc:
        text = unit + " - " + tag
    else:
        text = tag
    textsize = font.getsize(text)
    origin = (margin, newsize[1]-2*(margin+fontsize))
    rect = shadow(origin, textsize, 1)
    draw.rectangle(rect, black, black)
    draw.text(origin, text, white, font)

    if desc:
        text = desc
    else:
        text = unit
    textsize = font.getsize(text)
    origin = (newsize[0]-textsize[0]-margin, newsize[1]-2*(margin+fontsize))
    rect = shadow(origin, textsize, 1)
    draw.rectangle(rect, black, black)
    draw.text(origin, text, white, font)

    text = latlonstr(lat, lon)
    textsize = font.getsize(text)
    origin = (margin, newsize[1]-margin-fontsize)
    rect = shadow(origin, textsize, 1)
    draw.rectangle(rect, black, black)
    draw.text(origin, text, white, font)

    text = datestr(date)
    textsize = font.getsize(text)
    origin = (newsize[0]-textsize[0]-margin, newsize[1]-margin-fontsize)
    rect = shadow(origin, textsize, 1)
    draw.rectangle(rect, black, black)
    draw.text(origin, text, white, font)

    del draw


def main():
    if not os.path.exists(photo_dir):
        os.mkdir(photo_dir)

    bldginfo = {}
    with open(bldg_csv, 'rb') as fh:
        fh.readline()  # remove the header
        bldg_reader = csv.reader(fh, delimiter=',', quotechar='"')
        for row in bldg_reader:
            # Lat,Long,Unit,FMSS_Id,Park_Id,Name,Description,Type,Status,Occupant,Value,Size,Date
            # 0  ,1   ,2   ,3      ,4      ,5   ,6          ,7   ,8     ,9       ,10   ,11  ,12  
            tag = row[3]
            if tag:
                #unit, lat, lon, desc
                bldginfo[tag] = (row[2], row[0], row[1], row[6])

    with open(photo_csv, 'rb') as fh:
        fh.readline()  # remove the header
        photo_reader = csv.reader(fh, delimiter=',', quotechar='"')
        for row in photo_reader:
            # Id,Date,Unit,File,Latitude,Longitude,Url
            # 0 ,1   ,2   ,3   ,4       ,5        ,6
            tag = row[0]
            try:
                unit, lat, lon, desc = bldginfo[tag]
            except KeyError:
                unit = row[2]
                lat = row[4]
                lon = row[5]
                desc = ""
            date = row[1]
            name = row[3]
            src = os.path.join(root, unit, name)
            dest_dir = os.path.join(photo_dir, unit)
            if not os.path.exists(dest_dir):
                os.mkdir(dest_dir)
            dest = os.path.join(dest_dir, name)
            if os.path.exists(src) and (not os.path.exists(dest) or os.path.getmtime(dest) < os.path.getmtime(dest)):
                #print "processing ", src
                try:
                    im = Image.open(src)
                    im = apply_orientation.apply_orientation(im)
                    im.thumbnail(size, Image.ANTIALIAS)
                    annotate(im, unit, tag, lat, lon, date, desc)
                    im.save(dest)
                except IOError:
                    print "cannot create web photo for ", src, " -> ", dest


if __name__ == "__main__":
    main()