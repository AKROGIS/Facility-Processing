#!/usr/bin/env python

"""Creates a CSV list of photos (and select metadata) for all photos below a folder"""

__author__ = "Regan Sarwas, GIS Team, Alaska Region, National Park Service"
__email__ = "regan_sarwas@nps.gov"
__copyright__ = "Public Domain - product of the US Government"

import os
import datetime
import exifread   # https://pypi.python.org/pypi/ExifRead

#root = "/Users/jjcusick/Desktop/photos/"
#root = r"T:\PROJECTS\AKR\Buildings\PhotosFromAllYears-Geotagged\2014Reprocess"
root = os.path.dirname(os.path.abspath(__file__))
csv = os.path.join(root, "PhotoList.csv")

with open(csv, 'w') as f:
    f.write('folder,photo,id,namedate,exifdate,lat,lon,gpsdate,size,filedate\n')
    for root, dirs, files in os.walk(root):
        folder = os.path.basename(root)
        #folder = root.replace(start, '.')
        for filename in files:
            base, extension = os.path.splitext(filename)
            if extension.lower() == '.jpg':
                path = os.path.join(root, filename)
                newbase = base.lower().replace('_', '-')
                if -1 < newbase.find('-tag'):
                    newbase = newbase.replace('-tag', '')
                if -1 < newbase.find('-thm'):
                    newbase = newbase.replace('-thm', '')
                try:
                    code, namedate = newbase.split("-", 1)
                except ValueError:
                    code, namedate = newbase, ''
                size = os.path.getsize(path)
                lat,lon,exifdate,gpsdate = '','','',''
                with open(path, 'rb') as pf:
                    tags = exifread.process_file(pf, details=False)
                    try:
                        dms = tags['GPS GPSLatitude'].values
                        deg = dms[0].num
                        min = dms[1].num
                        sec = float(dms[2].num)/dms[2].den
                        lat = deg + (min + sec/60)/60 
                        if lat == 0:
                            lat = ''
                    except:
                        pass
                    try:
                        dms = tags['GPS GPSLongitude'].values
                        deg = dms[0].num
                        min = dms[1].num
                        sec = float(dms[2].num)/dms[2].den
                        lon = -1 * (deg + (min + sec/60)/60)
                        if lon == 0:
                            lon = ''
                    except:
                        pass
                    try:
                        time = tags['EXIF DateTimeOriginal'].values
                        #exifdate = time.replace(':','').replace(' ','T') #compact iso format
                        exifdate = time.replace(':','-',2)  # microsoft excel acceptable ISO format
                    except:
                        pass
                    try:
                        date = tags['GPS GPSDate'].values
                        time = tags['GPS GPSTimeStamp'].values
                        if date:
                        	#gpsdate = '{0}T{1}{2}{3}'.format(date.replace(':',''),time[0],time[1],time[2])
                        	gpsdate = '{0} {1}:{2}:{3}'.format(date.replace(':','-'),time[0],time[1],time[2])
                        else:
                            gpsdate = ''
                    except:
                        pass
                filedate = datetime.datetime.fromtimestamp(os.path.getmtime(path)).isoformat()
                filedate = filedate.replace('T',' ')  # microsoft excel acceptable ISO format            
                f.write('{0},{1},{2},{3},{4},{5},{6},{7},{8},{9}\n'.format(folder, filename, code, namedate, exifdate, lat, lon, gpsdate, size, filedate))
