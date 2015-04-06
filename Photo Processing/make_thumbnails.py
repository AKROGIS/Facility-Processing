#!/usr/bin/env python

"""Creates and updates a collection of thumbnails for photos listed in a CSV"""

__author__ = "Regan Sarwas, GIS Team, Alaska Region, National Park Service"
__email__ = "regan_sarwas@nps.gov"
__copyright__ = "Public Domain - product of the US Government"

from PIL import Image
import os
import os.path
import csv

import apply_orientation

root = os.path.dirname(os.path.abspath(__file__))
photo_csv = os.path.join(root, "PhotoList.csv")
thumbdir = os.path.join(root, "thumb")

size = (200, 150)

if not os.path.exists(thumbdir):
    os.mkdir(thumbdir)

with open(photo_csv, 'rb') as fh:
    fh.readline()  # remove the header
    photo_reader = csv.reader(fh, delimiter=',', quotechar='"')
    for row in photo_reader:
        # folder,photo,id,namedate,exifdate,lat,lon,gpsdate,size,filedate
        # 0     ,1    ,2 ,3       ,4       ,5  ,6  ,7      ,8   ,9
        unit = row[0]
        name = row[1]
        src = os.path.join(root, unit, name)
        dest_dir = os.path.join(thumbdir, unit)
        if not os.path.exists(dest_dir):
            os.mkdir(dest_dir)
        dest = os.path.join(dest_dir, name)
        if os.path.exists(src) and (not os.path.exists(dest) or os.path.getmtime(dest) < os.path.getmtime(dest)):
            try:
                im = Image.open(src)
                im = apply_orientation.apply_orientation(im)
                im.thumbnail(size, Image.ANTIALIAS)
                im.save(dest)
            except IOError:
                print "cannot create thumbnail for", src