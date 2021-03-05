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

from PIL import Image, ExifTags


class Config(object):
    """Namespace for configuration parameters. Edit as needed."""

    # pylint: disable=useless-object-inheritance,too-few-public-methods

    # Root folder - the common prefix for the `photo_folder` and `web_folder`
    # optional if you choose to provide a absolute path for both paths.
    root_folder = r"T:\PROJECTS\AKR\FMSS\PHOTOS"

    # Photo folder - the absolute path prefix for location of photo folders
    # and photo files.  Photos can be in the photo_folder or in sub folders
    # to any depth.
    photo_folder = os.path.join(root_folder, "ORIGINAL")

    # Thumb folder - the location in which to create thumbnails of the
    # photos found in `photo_folder`.  An identical path structure will be
    # created as needed. new web folders will only be created if it doesn't
    # exist, or is older than the matching original photo file.
    thumb_folder = os.path.join(root_folder, "THUMB")

    # Thumb size - the (width, height) of the thumbnail.
    # Image will not be stretched or clipped. so there may be some black
    # bands on the sides or top/bottom depending on the aspect ratio of the
    # original image.
    thumb_size = (200, 150)


def is_jpeg(path):
    """Return True if the file at path is a JPEG photo file."""
    if not os.path.isfile(path):
        return False
    ext = os.path.splitext(path)[1].lower()
    return ext in [".jpg", ".jpeg"]


def get_folders(start_dir):
    """Find all the folders below start_dir."""
    start_dir += os.pathsep
    results = []
    for root, folders, _ in os.walk(start_dir):
        relative_path = root.replace(start_dir, "")
        for folder in folders:
            results.append(os.path.join(relative_path, folder))
    return results


def get_photos(folder):
    """Return a list of all the photo files in folder."""
    return [f for f in os.listdir(folder) if is_jpeg(os.path.join(folder, f))]


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


def make_thumbs():
    """Make thumbnails with size for all photos below base."""

    if not os.path.exists(Config.photo_folder):
        print("Photo directory: " + Config.photo_folder + " does not exit.")
        return

    if not os.path.exists(Config.thumb_folder):
        os.mkdir(Config.thumb_folder)

    for folder in get_folders(Config.photo_folder):
        print(folder, end="")
        orig_path = os.path.join(Config.photo_folder, folder)
        new_path = os.path.join(Config.thumb_folder, folder)
        if not os.path.exists(new_path):
            os.mkdir(new_path)
        for photo in get_photos(orig_path):
            src = os.path.join(orig_path, photo)
            dest = os.path.join(new_path, photo)
            if os.path.exists(src) and (
                not os.path.exists(dest)
                or os.path.getmtime(dest) < os.path.getmtime(dest)
            ):
                try:
                    image = Image.open(src)
                    image = apply_orientation(image)
                    image.thumbnail(Config.thumb_size, Image.ANTIALIAS)
                    image.save(dest)
                    print(".", end="")
                except IOError:
                    print("Cannot create thumbnail for", src)


if __name__ == "__main__":
    make_thumbs()
