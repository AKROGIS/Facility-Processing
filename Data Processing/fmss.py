import urllib2
import json

location_url = 'http://inpniscvnpunit2/fmss/api/locations?siteid={0}&page={1}' #returns JSON
asset_url = 'http://inpniscvnpunit2/fmss/api/assets?siteid={0}&page={1}' #returns JSON

#Response is JSON, converted to Python it looks like:
response = {u'TotalItems': 2,
            u'TotalPages': 1,
            u'PagedList': ['item1', 'item2', '...'],
            u'Page': 1,
            u'PageSize': 25}

#example item in PagedList
example =  {u'LOCATIONSID': 5128917331L,
           u'STATUS': {u'maxvalue': u'OPERATING',
                       u'Value': u'OPERATING'},
           u'SOURCESYSID': u'',
           u'DESCRIPTION': u'ANM Alaska Packers Historic Site & Access Area',
           u'LO11': u'AC',
           u'LO6': 37978.81,
           u'CHANGEBY': u'RSHERMAN',
           u'LO2': u'3100',
           u'LOCHIERARCHY': {u'ORGID': u'NPS',
                             u'LOCHIERARCHYID': 1517752492,
                             u'SYSTEMID': u'PRIMARY',
                             u'PARENT': u'ANIA'},
           u'SITEID': u'P117',
           u'LOCATION': u'95774',
           u'SITE': {u'SITEUID': u'1005',
                     u'PARKALPHA': u'ANIA'},
           u'LO5': 58,
           u'ORGID': u'NPS',
           u'LO14': u'',
           u'LO9': 3123.6,
           u'LOCOPER': {u'FLO3': u'4',
                        u'SHIFTNUM': u'',
                        u'LOCOPERID': 3059260311L,
                        u'WARRANTYEXPDATE': None},
           u'CHANGEDATE': u'2014-02-14T12:24:44-07:00',
           u'LO7': 0.082}

#Map of common names for keys in example
location_fields = {'LO2':'Asset Code',
                   'LO5':'API',
                   'LO6':'CRV',
                   'LO7':'FCI',
                   'LO9':'DM',
                   'LO11':'Unit of Measure',
                   #No Unit of Measure QTY
                   #No Aquisition Date
                   'LO14':'unkown', #empty on all records
                   'LOCOPER.FL03':'Optimizer Band'} #usually blank, occassionally "{UNITCODE}001"

#The Status.maxvalue does not vary for a given status.value 
status = {'EXCESS':'OPERATING', #value:maxvalue
          'INACTIVE':'OPERATING',
          'NOTREADY':'NOTREADY',
          'OPERATING':'OPERATING',
          'PLANNED':'NOTREADY',
          'REMOVED':'DECOMMISSIONED',
          'SITE':'OPERATING'}

#Site Id by Park Unit Code (Site ID is used in URL Query)
sites = {'AKRO':'P115',
         'ANCH':'P166',
         'FAIR':'P120',
         'ALEU':'P165', #empty
         'ALAG':'P116',
         'ANIA':'P117',
         'BELA':'P118',
         'CAKR':'P119', #empty
         'DENA':'P167',
         'GAAR':'P121',
         'GLBA':'P003',
         'KATM':'P122',
         'KEFJ':'P123',
         'KLGO':'P168',
         'LACL':'P169',
         'KOVA':'P124', #empty
         'NOAT':'P125', #empty
         'SITK':'P126',
         'WEAR':'P127',
         'WRST':'P128',
         'YUCH':'P170'}

#List of Asset Codes seen in All Alaska Sites
assetCodes = {0000:'Site',
              1100:'Road',
              1300:'Parking Area',
              1700:'Road Bridge',
              1800:'Road Tunnel', #not used
              2100:'Trail',
              2200:'Trail Bridge',
              2300:'Trail Tunnel',
              3100:'Grounds',
              3800:'Fence',
              4100:'Building',
              5100:'Utility-Water',
              5200:'Utility-Sewer',
              5300:'Utility-Heat',
              5400:'Utility-Elec',
              5500:'Utility-Comm',
              5700:'Utility-Fuel',
              5800:'Utility-Waste',
              6200:'Constructed Waterway',
              6300:'Marina/Waterfront System',
              6400:'Aviation System',
              7100:'Monument',
              7200:'Maintained Archeological Sites',
              7400:'Towers/Missile Silos',
              7500:'Intepretive Media',
              7900:'Amphitheater'}

def myStr(s):
    if s:
        return str(s)
    else:
        return ''

#loc_header = ['Park','Asset_Code','Location','Description','Status','StatusMax','Organization','Parent_Organization','Parent_Location',
#              'API','CRV','FCI','DM','Unit_of_Measure','unk','Optimizer_Band','LocationsId']
loc_header = ['Park','Asset_Code','Location','Description','Status','Parent_Location',
              'API','CRV','FCI','DM','Unit_of_Measure']

def locations(park):
    page = 1
    done,data = locations_page(park,page)
    while not done:
        page += 1
        done,moredata = locations_page(park,page)
        data += moredata
    return data

def locations_page(park,page):
    try:
        f = urllib2.urlopen(location_url.format(sites[park],page))
    except urllib2.HTTPError:
        print "Unable to retrieve Location page {0} for {1}.".format(page,park)
        return (False,[])
    
    data = json.load(f)
    #print data
    total_pages = data['TotalPages']  # maybe 0 if there is no data
    current_page = data['Page']       # will always be 1 or greater
    done = current_page >= total_pages
    data = location_data(data['PagedList'],park)
    return (done,data)

def location_data(data,park):
    locations = []
    for page in data:
        try:
            parentOrg = page['LOCHIERARCHY']['ORGID']
        except:
            parentOrg = None
        try:
            parentLoc = page['LOCHIERARCHY']['PARENT']
        except:
            parentLoc = None
        try:
            opt = page['LOCOPER']['FL03']
        except:
            opt = None
        values = [park,page['LO2'],page['LOCATION'],page['DESCRIPTION'],page['STATUS']['Value'],
#                  page['STATUS']['maxvalue'],page['ORGID'],parentOrg,parentLoc,
#                  page['LO5'],page['LO6'],page['LO7'],page['LO9'],page['LO11'],page['LO14'],opt,page['LOCATIONSID']]
                  parentLoc,page['LO5'],page['LO6'],page['LO7'],page['LO9'],page['LO11']]
        locations.append(values)
    return locations

def lshowone(park,file=None):
    if file:
        import csv
        with open(file,'wb') as csvfile:
            cf = csv.writer(csvfile)
            cf.writerow(loc_header)
            for item in locations(park):
                item = [s.encode("utf-8") if isinstance(s, (str,unicode)) else s for s in item]
                cf.writerow(item)
    else:
        print ",".join(loc_header)
        for item in locations(park):
            print ",".join([myStr(x) for x in item])

def lshowall(file=None):
    if file:
        import csv
        with open(file,'wb') as csvfile:
            cf = csv.writer(csvfile)
            cf.writerow(loc_header)
            for park in sites:
                for item in locations(park):
                    item = [s.encode("utf-8") if isinstance(s, (str,unicode)) else s for s in item]
                    cf.writerow(item)
    else:
        print ",".join(loc_header)
        for park in sites:
            for item in locations(park):
                print ",".join([myStr(x) for x in item])
 


asset_header = ['Park','Asset_Type','Asset_Code','Asset_ID','Asset_UID','Asset_Num','Location','Description',
                'unk19','unk20','unk21','unk5','unk6','Quantity','Unit_of_Measure','Expiration_Date'
                'Install_Date','Replacement_Cost','Organization']

def assets(park):
    page = 1
    done,data = assets_page(park,page)
    while not done:
        page += 1
        done,moredata = assets_page(park,page)
        data += moredata
    return data

def assets_page(park,page):
    try:
        f = urllib2.urlopen(asset_url.format(sites[park],page))
    except urllib2.HTTPError:
        print "Unable to retrieve Asset page {0} for {1}.".format(page,park)
        return (False,[])
    
    data = json.load(f)
    f.close()
    #print data
    total_pages = data['TotalPages']
    current_page = data['Page']
    print park,current_page,total_pages
    done = current_page >= total_pages
    data = asset_data(data['PagedList'],park)
    return (done,data)

def asset_data(data,park):
    assets = []
    for page in data:
        try:
            parentOrg = page['LOCHIERARCHY']['ORGID']
        except:
            parentOrg = None
        try:
            parentLoc = page['LOCHIERARCHY']['PARENT']
        except:
            parentLoc = None
        try:
            opt = page['LOCOPER']['FL03']
        except:
            opt = None
        values = [park,page['ASSETTYPE'],page['EQ4'],page['ASSETID'],page['ASSETNUM'],page['ASSETUID'],page['LOCATION'],page['DESCRIPTION'],
                  page['EQ19'],page['EQ20'],page['EQ21'],page['EQ5'],page['EQ6'],page['EQ7'],page['EQ8'],page['EQ9'],
                  page['INSTALLDATE'],page['REPLACECOST'],page['ORGID']]
        assets.append(values)
    return assets

def ashowone(park,file=None):
    if file:
        import csv
        with open(file,'wb') as csvfile:
            cf = csv.writer(csvfile)
            cf.writerow(asset_header)
            for item in assets(park):
                item = [s.encode("utf-8") if isinstance(s, (str,unicode)) else s for s in item]
                cf.writerow(item)
    else:
        print ",".join(asset_header)
        for item in assets(park):
            print ",".join([myStr(x) for x in item])

def ashowall(file=None):
    if file:
        import csv
        with open(file,'wb') as csvfile:
            cf = csv.writer(csvfile)
            cf.writerow(asset_header)
            for park in sites:
                for item in assets(park):
                    item = [s.encode("utf-8") if isinstance(s, (str,unicode)) else s for s in item]
                    cf.writerow(item)
    else:
        print ",".join(asset_header)
        for park in sites:
            for item in assets(park):
                print ",".join([myStr(x) for x in item])
 
#lshowall('fmss.csv')
#lshowone('AKRO')
ashowall('assets.csv')
#ashowone('KLGO','klgo.csv')
#ashowone('LACL','lacl.csv')
