# -*- coding: utf-8 -*-
"""
Test queries to the FMSS SOAP based web services.

Note: Worked with the older REST service as of June 21, 2016.
The old webservice was retired.
As of June 4, 2018, this worked with the new SOAP services (still underdevelopment)

Written for Python 2.7; will NOT with Python 3.x.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import urllib2


endpoint1 = r"https://mif.pfmd.nps.gov/meaweb/services/FMSSGISLOCQ"
query1 = """
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
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
    lo2="4100", siteid="P117"
)

endpoint2 = r"https://mif.pfmd.nps.gov/meaweb/services/FMSSGISFRPPQ"
query2 = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
  <soapenv:Header/>
  <soapenv:Body>
    <max:QueryFMSSGISFRPP xmlns:max="http://www.ibm.com/maximo">
      <max:FMSSGISFRPPQuery>
        <max:FRPPS>
          <max:FRPP operator="=">{frpp}</max:FRPP>
        </max:FRPPS>
      </max:FMSSGISFRPPQuery>
    </max:QueryFMSSGISFRPP>
  </soapenv:Body>
</soapenv:Envelope>""".format(
    frpp="1"
)

endpoint3 = r"https://mif.pfmd.nps.gov/meaweb/services/FMSSGISASSETQ"
query3 = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
  <soapenv:Header/>
  <soapenv:Body>
    <max:QueryFMSSGISASSET xmlns:max="http://www.ibm.com/maximo">
      <max:FMSSGISASSETQuery>
        <max:ASSETS>
          <max:LO2 operator="=">{lo2}</max:LO2>
          <max:SITEID operator="=">{siteid}</max:SITEID>
          <max:LOCATION operator="=">{loc}</max:LOCATION>
        </max:ASSETS>
      </max:FMSSGISASSETQuery>
    </max:QueryFMSSGISASSET>
  </soapenv:Body>
</soapenv:Envelope>""".format(
    lo2="4100", siteid="P117", loc="43743"
)

endpoint4 = r"https://mif.pfmd.nps.gov/meaweb/services/FMSSGISWOQ"
query4 = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
  <soapenv:Header/>
  <soapenv:Body>
    <max:QueryFMSSGISWO xmlns:max="http://www.ibm.com/maximo">
      <max:FMSSGISWOQuery>
        <max:WORKORDERS>
          <max:LO2 operator="=">{lo2}</max:LO2>
          <max:SITEID operator="=">{siteid}</max:SITEID>
          <max:LOCATION operator="=">{loc}</max:LOCATION>
        </max:WORKORDERS>
      </max:FMSSGISWOQuery>
    </max:QueryFMSSGISWO>
  </soapenv:Body>
</soapenv:Envelope>""".format(
    lo2="4100", siteid="P117", loc="43743"
)


encoded_query = query3.encode("utf-8")
endpoint = endpoint3


# SOAP 1.1 Header
headers = {
    "Content-Type": 'text/xml; charset="utf-8"',
    "Content-Length": "{0}".format(len(encoded_query)),
}

request = urllib2.Request(url=endpoint, headers=headers, data=encoded_query)

response = urllib2.urlopen(request).read()
print(response)
