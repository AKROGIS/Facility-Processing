# -*- coding: utf-8 -*-
"""
Creates and updates a collection of thumbnails for photos listed in a CSV.

File paths are hard coded in the script relative to the scipt's location.
The database connection string and schema are also hardcoded in the script.

Written for Python 2.7; may work with Python 3.x.

Third party requirements:
* Pillow (PIL) - https://pypi.python.org/pypi/Pillow
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import os

from PIL import Image

import apply_orientation  # dependency on PIL


def is_jpeg(path):
    if not os.path.isfile(path):
        return False
    ext = os.path.splitext(path)[1].lower()
    return ext in [".jpg", ".jpeg"]


def parks(parent):
    return [f for f in os.listdir(parent) if os.path.isdir(os.path.join(parent, f))]


def folders(start_dir):
    start_dir = start_dir + "\\"
    results = []
    for root, dirs, files in os.walk(start_dir):
        relative_path = root.replace(start_dir, "")
        for d in dirs:
            results.append(os.path.join(relative_path, d))
    return results


def photos(parkdir):
    return [f for f in os.listdir(parkdir) if is_jpeg(os.path.join(parkdir, f))]


def make_thumbs(base, size):
    origdir = os.path.join(base, "ORIGINAL")
    thumbdir = os.path.join(base, "THUMB")

    if not os.path.exists(origdir):
        print("Photo directory: " + origdir + " does not exit.")
        return

    if not os.path.exists(thumbdir):
        os.mkdir(thumbdir)

    for park in folders(origdir):
        print(park, end="")
        orig_park_path = os.path.join(origdir, park)
        new_park_path = os.path.join(thumbdir, park)
        if not os.path.exists(new_park_path):
            os.mkdir(new_park_path)
        for photo in photos(orig_park_path):
            src = os.path.join(orig_park_path, photo)
            dest = os.path.join(new_park_path, photo)
            if os.path.exists(src) and (
                not os.path.exists(dest)
                or os.path.getmtime(dest) < os.path.getmtime(dest)
            ):
                try:
                    im = Image.open(src)
                    im = apply_orientation.apply_orientation(im)
                    im.thumbnail(size, Image.ANTIALIAS)
                    im.save(dest)
                    print(".", end="")
                except IOError:
                    print("Cannot create thumbnail for", src)


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Assumes script is in a sub folder of the Processing folder which is sub to the photos base folder.
    base_dir = os.path.dirname(os.path.dirname(script_dir))
    thumb_size = (200, 150)
    make_thumbs(base_dir, thumb_size)
