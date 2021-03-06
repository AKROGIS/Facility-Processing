# -*- coding: utf-8 -*-
"""
Tool to query FMSS SOAP based web services.

Note: Worked with the older REST service as of June 21, 2016.
The old webservice was retired.
As of June 4, 2018, this worked with the new SOAP services (still underdevelopment)

File paths are hard coded in the script and relative to the current working directory.

Written for Python 2.7; it may with Python 3.x.

Third party requirements:
* pyodbc - https://pypi.python.org/pypi/pyodbc
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import csv
import sys
import xml.etree.ElementTree as eT

try:
    import urllib2
except ImportError:
    # Python 3 replacement
    import urllib.request as urllib2

import pyodbc

import csv23

# pylint: disable=invalid-name,missing-function-docstring

# Python 2/3 compatible xrange() cabability
# pylint: disable=undefined-variable,redefined-builtin
if sys.version_info[0] < 3:
    range = xrange


def location_query(site_id, asset_code):
    # host = "mif.pfmd.nps.gov"
    # action = '"urn:processDocument"'
    endpoint = "https://uat1mif.pfmd.nps.gov/meawebuat1/services/FMSSGISLOCQ"

    query = """<soapenv:Envelope xmlns:soapenv="http://www.w3.org/2003/05/soap-envelope">
      <soapenv:Header/>
      <soapenv:Body>
        <max:QueryFMSSGISLOC xmlns:max="http://www.ibm.com/maximo">
          <max:FMSSGISLOCQuery>
            <max:LOCATIONS>
              <max:LO2 operator="=">{lo2}</max:LO2>
              <max:SITEID operator="=">{siteid}</max:SITEID>
            </max:LOCATIONS>
          </max:FMSSGISLOCQuery>
        </max:QueryFMSSGISLOC>
      </soapenv:Body>
    </soapenv:Envelope>""".format(
        lo2=asset_code, siteid=site_id
    )

    encoded_query = query.encode("utf-8")

    # HTTP Header for SOAP 1.2
    headers = {  # "Host": host,
        "Content-Type": 'application/soap+xml; charset="utf-8"',
        # "SOAPAction": action,
        "Content-Length": "{0}".format(len(encoded_query)),
    }

    request = urllib2.Request(url=endpoint, headers=headers, data=encoded_query)
    response = urllib2.urlopen(request).read()
    return response


def frpp_query(location_id):
    endpoint = "https://uat1mif.pfmd.nps.gov/meawebuat1/services/FMSSGISFRPPQ"

    query = """<soapenv:Envelope xmlns:soapenv="http://www.w3.org/2003/05/soap-envelope">
      <soapenv:Header/>
      <soapenv:Body>
        <int:FMSSGISFRPPQ xmlns:int="http://www.ibm.com/maximo">
          <int:Content>
            <int:FMSSGISFRPP>
              <int:FRPP>
                <int:LOCATION operator="=">{locationid}</int:LOCATION>
              </int:FRPP>
            </int:FMSSGISFRPP>
          </int:Content>
        </int:FMSSGISFRPPQ>
      </soapenv:Body>
    </soapenv:Envelope>""".format(
        locationid=location_id
    )

    encoded_query = query.encode("utf-8")

    # HTTP Header for SOAP 1.2
    headers = {
        "Content-Type": 'application/soap+xml; charset="utf-8"',
        "Content-Length": "{0}".format(len(encoded_query)),
    }

    request = urllib2.Request(url=endpoint, headers=headers, data=encoded_query)
    response = urllib2.urlopen(request).read()
    return response


def asset_query(site_id, asset_code):
    endpoint = "https://uat1mif.pfmd.nps.gov/meawebuat1/services/FMSSGISASSETQ"

    query = """<soapenv:Envelope xmlns:soapenv="http://www.w3.org/2003/05/soap-envelope">
      <soapenv:Header/>
      <soapenv:Body>
        <max:QueryFMSSGISLOC xmlns:max="http://www.mro.com/mx/integration">
          <max:FMSSGISLOCQuery>
            <max:LOCATIONS>
              <max:LO2 operator="=">{lo2}</max:LO2>
              <max:SITEID operator="=">{siteid}</max:SITEID>
            </max:LOCATIONS>
          </max:FMSSGISLOCQuery>
        </max:QueryFMSSGISLOC>
      </soapenv:Body>
    </soapenv:Envelope>""".format(
        lo2=asset_code, siteid=site_id
    )

    encoded_query = query.encode("utf-8")

    # HTTP Header for SOAP 1.2
    headers = {
        "Content-Type": 'application/soap+xml; charset="utf-8"',
        "Content-Length": "{0}".format(len(encoded_query)),
    }

    request = urllib2.Request(url=endpoint, headers=headers, data=encoded_query)
    response = urllib2.urlopen(request).read()
    return response


# No example/test for a work order query FMSSGISWOQ

table_column_names = [
    "UNITCODE",
    "Asset_Code",  # LO2
    "Asset_Type",
    "Parent_FACLOCID",
    "Status",  # STATUS
    "FACLOCID",  # LOCATION
    "Description",  # DESCRIPTION
    # 'Facility_Type',
    # 'OB', #?Optimizer Band
    "API",  # LO5
    "CRV",  # LO6
    "FCI",  # LO7
    "DM",  # LO9
    "UM",  # LO11
    "Qty",  # LO12
    # '??',  # LO14
    "YearBlt",  # YEARBUILT
    # 'Rank',
    # 'Occupant'    # NOT ORGID
    # 'Historic_Status',
    # 'LCS',
    # 'Long_Description'
]

xml_tags = [
    "STATUS",
    "LOCATION",
    "DESCRIPTION",
    "LO5",
    "LO6",
    "LO7",
    "LO9",
    "LO11",
    "LO12",
    "YEARBUILT",
]
ns = "{http://www.ibm.com/maximo}"
ns_tags = [ns + xtag for xtag in xml_tags]


sites = {
    "AKRO": "P115",
    "ANCH": "P166",
    "FAIR": "P120",
    "ALEU": "P165",  # empty
    "ALAG": "P116",
    "ANIA": "P117",
    "BELA": "P118",
    "CAKR": "P119",  # empty
    "DENA": "P167",
    "GAAR": "P121",
    "GLBA": "P003",
    "KATM": "P122",
    "KEFJ": "P123",
    "KLGO": "P168",
    "LACL": "P169",
    "KOVA": "P124",  # empty
    "NOAT": "P125",  # empty
    "SITK": "P126",
    "WEAR": "P127",
    "WRST": "P128",
    "YUCH": "P170",
}

# List of Asset Codes seen in All Alaska Sites
asset_types = {
    0000: "Site",
    1100: "Road",
    1300: "Parking Area",
    1700: "Road Bridge",
    1800: "Road Tunnel",  # not used
    2100: "Trail",
    2200: "Trail Bridge",
    2300: "Trail Tunnel",
    3100: "Grounds",
    3800: "Fence",
    4100: "Building",
    5100: "Utility-Water",
    5200: "Utility-Sewer",
    5300: "Utility-Heat",
    5400: "Utility-Elec",
    5500: "Utility-Comm",
    5700: "Utility-Fuel",
    5800: "Utility-Waste",
    6200: "Constructed Waterway",
    6300: "Marina/Waterfront System",
    6400: "Aviation System",
    7100: "Monument",
    7200: "Maintained Archeological Sites",
    7400: "Towers/Missile Silos",
    7500: "Intepretive Media",
    7900: "Amphitheater",
}


def location_to_rows(data, location):
    # noinspection PyUnresolvedReferences
    attributes = [
        elem.text if elem is not None else ""
        for elem in [location.find(tag) for tag in ns_tags]
    ]
    try:
        parent = location.find(ns + "LOCHIERARCHY").find(ns + "PARENT").text
    except AttributeError:
        parent = ""
    row = data + [parent] + attributes
    return row


def convert_xml_to_rows(data, response):
    xml_root = eT.fromstring(response)
    locations = xml_root.iter(ns + "LOCATIONS")
    return [location_to_rows(data, location) for location in locations]


def convert_xml_to_csv(data, response, csv_writer):
    rows = convert_xml_to_rows(data, response)
    for row in rows:
        csv23.write(csv_writer, row)


def test_service():
    asset_code = "4100"
    site_id = "P117"
    response = location_query(site_id, asset_code)
    return response


def test_service2():
    response = frpp_query("100905")
    return response


def test_csv(csv_path):
    with csv23.open(csv_path, "w") as csv_file:
        csv_writer = csv.writer(csv_file)
        csv23.write(csv_writer, table_column_names)
        response = test_service()
        convert_xml_to_csv(["ANIA", "4100", "Building"], response, csv_writer)


def build_csv(csv_path):
    with csv23.open(csv_path, "w") as csv_file:
        csv_writer = csv.writer(csv_file)
        csv23.write(csv_writer, table_column_names)
        for site in sites:
            site_id = sites[site]
            for asset_code in asset_types:
                data = [site, "{0}".format(asset_code), asset_types[asset_code]]
                print(data)
                response = location_query(site_id, "{0}".format(asset_code))
                convert_xml_to_csv(data, response, csv_writer)


def get_connection_or_die(server, database):
    """
    Get a Trusted pyodbc connection to the SQL Server database on server.

    Try several connection strings.
    See https://github.com/mkleehammer/pyodbc/wiki/Connecting-to-SQL-Server-from-Windows

    Exit with an error message if there is no successful connection.
    """
    drivers = [
        "{ODBC Driver 17 for SQL Server}",  # supports SQL Server 2008 through 2017
        "{ODBC Driver 13.1 for SQL Server}",  # supports SQL Server 2008 through 2016
        "{ODBC Driver 13 for SQL Server}",  # supports SQL Server 2005 through 2016
        "{ODBC Driver 11 for SQL Server}",  # supports SQL Server 2005 through 2014
        "{SQL Server Native Client 11.0}",  # DEPRECATED: released with SQL Server 2012
        # '{SQL Server Native Client 10.0}',    # DEPRECATED: released with SQL Server 2008
    ]
    conn_template = "DRIVER={0};SERVER={1};DATABASE={2};Trusted_Connection=Yes;"
    for driver in drivers:
        conn_string = conn_template.format(driver, server, database)
        try:
            connection = pyodbc.connect(conn_string)
            return connection
        except pyodbc.Error:
            pass
    print("Rats!! Unable to connect to the database.")
    print("Make sure you have an ODBC driver installed for SQL Server")
    print("and your AD account has the proper DB permissions.")
    print("Contact akro_gis_helpdesk@nps.gov for assistance.")
    sys.exit()


def execute_sql(connection, sql):
    wcursor = connection.cursor()
    wcursor.execute(sql)
    try:
        wcursor.commit()
    except pyodbc.Error as de:
        print("Database error ocurred", de)


def chunks(l, n):
    """Yield successive n-sized chunks from list l."""
    for i in range(0, len(l), n):
        yield l[i : i + n]


def create_table(connection, name):
    # sql = ("if not exists (select * from sys.tables where name='Locations_In_CartoDB')"
    # do not check if the table exists; I want to fail if the able exists
    sql = (
        "create table [{0}] ("
        "	[UNITCODE] [nvarchar](max) NULL,"
        "	[Asset_Code] [int] NULL,"
        "	[Asset_Type] [nvarchar](max) NULL,"
        "	[Parent_FACLOCID] [nvarchar](10) NULL,"
        "	[Status] [nvarchar](max) NULL,"
        "	[FACLOCID] [nvarchar](10) NOT NULL,"
        "	[Description] [nvarchar](max) NULL,"
        "	[API] [int] NULL,"
        "	[CRV] [numeric](38, 8) NULL,"
        "	[FCI] [numeric](38, 8) NULL,"
        "	[DM] [numeric](38, 8) NULL,"
        "	[UM] [nvarchar](max) NULL,"
        "	[Qty] [nvarchar](max) NULL,"
        "	[YearBlt] [int] NULL,"
        "	[Long_Description] [nvarchar](max) NULL,"
        " CONSTRAINT [PK_{0}] PRIMARY KEY CLUSTERED ([FACLOCID] ASC))"
    ).format(name)
    execute_sql(connection, sql)
    sql = "GRANT SELECT ON [{0}] TO PUBLIC".format(name)
    execute_sql(connection, sql)


def delete_table(connection, name):
    sql = "IF OBJECT_ID('{0}', 'U') IS NOT NULL DROP TABLE {0}; ".format(name)
    execute_sql(connection, sql)


def escape_single_quote(s):
    return s.replace("'", "''")


def sql_clean(row):
    return [escape_single_quote(n) if n is not None else "NULL" for n in row]


def test_fill_table(connection, name):
    wcursor = connection.cursor()
    sql = "insert into [{0}] ([FACLOCID], [description]) values ".format(
        name,
    )
    values = "(93492,'{0}')".format("Résumé")
    print(sql + values)
    wcursor.execute(sql + values)
    try:
        wcursor.commit()
    except pyodbc.Error as de:
        print("Database error ocurred", de)


def fill_table(connection, name):
    wcursor = connection.cursor()
    sql = "insert into [{0}] ({1}) values ".format(name, ",".join(table_column_names))
    for site in sites:  # in ['ANIA']:
        site_id = sites[site]
        for asset_code in asset_types:  # in [4100]:
            data = [site, "{0}".format(asset_code), asset_types[asset_code]]
            print(data)
            response = location_query(site_id, "{0}".format(asset_code))
            rows = convert_xml_to_rows(data, response)

            # SQL Server is limited to 1000 rows in an insert
            for chunk in chunks(rows, 999):
                values = ",".join(
                    [
                        (
                            "('{0}',{1},'{2}','{3}','{4}','{5}','{6}',{7},{8},{9},"
                            "{10},'{11}','{12}',{13})"
                        ).format(*sql_clean(row))
                        for row in chunk
                    ]
                )
                # print(sql + values)
                wcursor.execute(sql + values)
    try:
        wcursor.commit()
    except pyodbc.Error as de:
        print("Database error ocurred", de)


def rename_table(connection, old_name, new_name):
    sql = "exec sp_rename '{0}', '{1}';".format(old_name, new_name)
    sql += "exec sp_rename '{1}.PK_{0}', 'PK_{1}', N'INDEX';".format(old_name, new_name)
    execute_sql(connection, sql)


def copy_column(connection, column_name, from_table, to_table):
    key = "FACLOCID"
    sql = (
        "update t set [{0}] = f.[{0}] "
        "from [{1}] as f join [{2}] as t "
        "on t.[{3}] = f.[{3}]"
    ).format(column_name, from_table, to_table, key)
    # print(sql)
    execute_sql(connection, sql)


def update_db():

    # pylint: disable=broad-except

    conn = get_connection_or_die("inpakrovmais", "akr_facility2")
    try:
        create_table(conn, "FMSSExport_New")
        fill_table(conn, "FMSSExport_New")
        copy_column(conn, "Long_Description", "FMSSExport", "FMSSExport_New")
        delete_table(conn, "FMSSExport")
        #  delete_table(conn, 'FMSSExport_Old')
        #  rename_table(conn, 'FMSSExport', 'FMSSExport_Old')
        rename_table(conn, "FMSSExport_New", "FMSSExport")
    except Exception as ex:
        print(ex)
    finally:
        # Make sure to remove the 'FMSSExport_New' if it exists (problem),
        # so we can try again next time.
        try:
            delete_table(conn, "FMSSExport_New")
            print("Deleted table FMSSExport_New")
        except pyodbc.Error as ex:
            print(ex)


print(test_service2())
# test_csv('out.csv')
# build_csv('out.csv')
# update_db()
