# Tool to query FMSS SOAP based web services as of June 21, 2016
# Note that the older REST service was retired.
# The new SOAP services is still underdevelopment.
# This no longer works, as of July 27, 2016, because it is requiring authentication

import urllib2
import xml.etree.ElementTree as eT
import csv


def location_query(site_id, asset_code):
    host = "inp2420maxsys1u:9082"
    action = '"urn:processDocument"'
    endpoint = r"http://inp2420maxsys1u:9082/meaweb/services/FMSSGISLOCQ"

    query = u"""<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">
      <soap:Body>
        <max:QueryFMSSGISLOC xmlns:max="http://www.ibm.com/maximo">
          <max:FMSSGISLOCQuery>
            <max:LOCATIONS>
              <max:LO2 operator="=">{lo2}</max:LO2>
              <max:SITEID operator="=">{siteid}</max:SITEID>
            </max:LOCATIONS>
          </max:FMSSGISLOCQuery>
        </max:QueryFMSSGISLOC>
      </soap:Body>
    </soap:Envelope>""".format(lo2=asset_code, siteid=site_id)

    encoded_query = query.encode('utf-8')

    # SOAP 1.2 Header
    headers = {"Host": host,
               "Content-Type": "application/soap+xml; charset=UTF-8; action="+action,
               "Content-Length": str(len(encoded_query))}

    request = urllib2.Request(url=endpoint,
                              headers=headers,
                              data=encoded_query)
    response = urllib2.urlopen(request).read()
    return response


def test():
    asset_code = '1100'
    site_id = 'P417'
    response = location_query(site_id, asset_code)
    print response


def test_csv():
    out_file = 'out.csv'
    asset_code = '1100'
    site_id = 'P417'
    response = location_query(site_id, asset_code)
    xml_root = eT.fromstring(response)
    locations = xml_root.iter('LOCATIONS')
    tags = ['LOCATION', 'DESCRIPTION', 'LO11', 'LO14', 'LO2', 'LO5', 'LO6', 'LO7', 'LO9', 'STATUS', 'YEARBUILT']
    with open(out_file, 'wb') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(tags)
        for location in locations:
            data = [location.find(tag).text for tag in tags]
            csv_writer.writerow(data)


table_column_names = [
    'Region',
    'Park',
    'Asset_Code',   # LO2
    'Asset_Type',
    'Status',       # STATUS
    'Location',     # LOCATION
    'Description',  # DESCRIPTION
    # 'Parent',
    # 'Facility_Type',
    # 'OB', #?Optimizer Band
    'API',  # LO5
    'CRV',  # LO6
    'FCI',  # LO7
    'DM',   # LO9
    'UM',   # LO11
    'Qty',  # LO14
    'YearBlt'  # YEARBUILT
    # 'Rank',
    # 'Occupant',
    # 'Historic_Status',
    # 'LCS',
    # 'Long_Description'
]
xml_tags = ['STATUS', 'LOCATION', 'DESCRIPTION', 'LO5', 'LO6', 'LO7', 'LO9', 'LO11', 'LO14', 'YEARBUILT']


sites = {
    'AKRO': 'P115',
    'ANCH': 'P166',
    'FAIR': 'P120',
    'ALEU': 'P165',  # empty
    'ALAG': 'P116',
    'ANIA': 'P117',
    'BELA': 'P118',
    'CAKR': 'P119',  # empty
    'DENA': 'P167',
    'GAAR': 'P121',
    'GLBA': 'P003',
    'KATM': 'P122',
    'KEFJ': 'P123',
    'KLGO': 'P168',
    'LACL': 'P169',
    'KOVA': 'P124',  # empty
    'NOAT': 'P125',  # empty
    'SITK': 'P126',
    'WEAR': 'P127',
    'WRST': 'P128',
    'YUCH': 'P170'
}

# List of Asset Codes seen in All Alaska Sites
asset_types = {
    0000: 'Site',
    1100: 'Road',
    1300: 'Parking Area',
    1700: 'Road Bridge',
    1800: 'Road Tunnel',  # not used
    2100: 'Trail',
    2200: 'Trail Bridge',
    2300: 'Trail Tunnel',
    3100: 'Grounds',
    3800: 'Fence',
    4100: 'Building',
    5100: 'Utility-Water',
    5200: 'Utility-Sewer',
    5300: 'Utility-Heat',
    5400: 'Utility-Elec',
    5500: 'Utility-Comm',
    5700: 'Utility-Fuel',
    5800: 'Utility-Waste',
    6200: 'Constructed Waterway',
    6300: 'Marina/Waterfront System',
    6400: 'Aviation System',
    7100: 'Monument',
    7200: 'Maintained Archeological Sites',
    7400: 'Towers/Missile Silos',
    7500: 'Intepretive Media',
    7900: 'Amphitheater'
}


def test3():
    out_file = 'out.csv'
    region = 'AKR'
    with open(out_file, 'wb') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(table_column_names)
        for site in sites:
            site_id = sites[site]
            for asset_code in asset_types:
                data = [region, site, str(asset_code), asset_types[asset_code]]
                response = location_query(site_id, str(asset_code))
                xml_root = eT.fromstring(response)
                locations = xml_root.iter('LOCATIONS')
                for location in locations:
                    data += [location.find(tag).text for tag in xml_tags]
                    csv_writer.writerow(data)
