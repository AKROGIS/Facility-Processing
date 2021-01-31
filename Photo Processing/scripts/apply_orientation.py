# -*- coding: utf-8 -*-

"""
Rotates an image to normalize it based on the EXIF rotation tag

Written for Python 2.7; may work with Python 3.x.

Third party requirements:
* Pillow (PIL) - https://pypi.python.org/pypi/Pillow
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import sys

try:
    from PIL import Image
except ImportError:
    module_missing("Pillow")


def module_missing(name):
    """Prints details about missing 3rd party module (name) and exits."""

    print("Module {0} not found, make sure it is installed.".format(name))
    exec_dir = os.path.split(sys.executable)[0]
    pip = os.path.join(exec_dir, "Scripts", "pip")
    print("Install with: {0} install {1}".format(pip, name))
    print("Reference: https://pypi.python.org/pypi/{0}".format(name))
    sys.exit()


def flip_horizontal(im):
    return im.transpose(Image.FLIP_LEFT_RIGHT)


def flip_vertical(im):
    return im.transpose(Image.FLIP_TOP_BOTTOM)


def rotate_180(im):
    return im.transpose(Image.ROTATE_180)


def rotate_90(im):
    return im.transpose(Image.ROTATE_90)


def rotate_270(im):
    return im.transpose(Image.ROTATE_270)


def transpose(im):
    return rotate_90(flip_horizontal(im))


def transverse(im):
    return rotate_90(flip_vertical(im))


orientation_funcs = [
    None,
    lambda x: x,
    flip_horizontal,
    rotate_180,
    flip_vertical,
    transpose,
    rotate_270,
    transverse,
    rotate_90,
]


def apply_orientation(im):
    """
    Extract the oritentation EXIF tag from the image, which should be a PIL Image instance,
    and if there is an orientation tag that would rotate the image, apply that rotation to
    the Image instance given to do an in-place rotation.

    :param Image im: Image instance to inspect
    :return: A possibly transposed image instance
    """

    try:
        kOrientationEXIFTag = 0x0112
        if hasattr(im, "_getexif"):  # only present in JPEGs
            e = im._getexif()  # returns None if no EXIF data
            if e is not None:
                # log.info('EXIF data found: %r', e)
                orientation = e[kOrientationEXIFTag]
                f = orientation_funcs[orientation]
                return f(im)
    except:
        # We'd be here with an invalid orientation value or some random error?
        pass  # log.exception("Error applying EXIF Orientation tag")
    return im
