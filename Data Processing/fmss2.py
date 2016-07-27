# Tool to query FMSS SOAP based web services as of June 21, 2016
# Note that the older REST service was retired.
# The new SOAP services is still underdevelopment.
# This no longer works, as of July 27, 2016, because it is requiring authentication

import urllib2

assetCode = '1100'
siteid = 'P417'

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
</soap:Envelope>""".format(lo2 = assetCode, siteid = siteid)

encoded_query = query.encode('utf-8')

#SOAP 1.2 Header
headers = {"Host": host,
           "Content-Type": "application/soap+xml; charset=UTF-8; action="+action,
           "Content-Length": str(len(encoded_query))}

request = urllib2.Request(url = endpoint,
                          headers = headers,
                          data = encoded_query)
response = urllib2.urlopen(request).read()
print response
