#!/usr/bin/env python

"""Creates and updates a collection of thumbnails for photos listed in a CSV"""

__author__ = "Regan Sarwas, GIS Team, Alaska Region, National Park Service"
__email__ = "regan_sarwas@nps.gov"
__copyright__ = "Public Domain - product of the US Government"


import sys
import os

try:
    from PIL import Image
except ImportError:
    Image = None
    pydir = os.path.dirname(sys.executable)
    print 'PIL module not found, make sure it is installed with'
    print pydir + r'\Scripts\pip.exe install Pillow'
    print 'Don''t have pip?'
    print 'Download <https://bootstrap.pypa.io/get-pip.py> to ' + pydir + r'\Scripts\get-pip.py'
    print 'Then run'
    print sys.executable + ' ' + pydir + r'\Scripts\get-pip.py'
    sys.exit()

import apply_orientation  # dependency on PIL


def is_jpeg(path):
    if not os.path.isfile(path):
        return False
    ext = os.path.splitext(path)[1].lower()
    return ext in ['.jpg', '.jpeg']


def parks(parent):
    return [f for f in os.listdir(parent) if os.path.isdir(os.path.join(parent, f))]


def photos(parkdir):
    return [f for f in os.listdir(parkdir) if is_jpeg(os.path.join(parkdir, f))]


def make_thumbs(base, size):
    origdir = os.path.join(base, "ORIGINAL")
    thumbdir = os.path.join(base,  "THUMB")

    if not os.path.exists(origdir):
        print "Photo directory: " + origdir + " does not exit."
        return

    if not os.path.exists(thumbdir):
        os.mkdir(thumbdir)

    for park in parks(origdir):
        print park,
        orig_park_path = os.path.join(origdir, park)
        new_park_path = os.path.join(thumbdir, park)
        if not os.path.exists(new_park_path):
            os.mkdir(new_park_path)
        for photo in photos(orig_park_path):
            src = os.path.join(orig_park_path, photo)
            dest = os.path.join(new_park_path, photo)
            if os.path.exists(src) and (not os.path.exists(dest) or os.path.getmtime(dest) < os.path.getmtime(dest)):
                try:
                    im = Image.open(src)
                    im = apply_orientation.apply_orientation(im)
                    im.thumbnail(size, Image.ANTIALIAS)
                    im.save(dest)
                    print '.',
                except IOError:
                    print "Cannot create thumbnail for", src


if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Assumes script is in a sub folder of the Processing folder which is sub to the photos base folder.
    base_dir = os.path.dirname(os.path.dirname(script_dir))
    thumb_size = (200, 150)
    make_thumbs(base_dir, thumb_size)
