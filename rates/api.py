import requests

import xml.etree.ElementTree as ET

def get_rates_from_usps(params):
    data = {'data': 'something'}
    KEY = '564ORDOR2223'
    package = '1ST'
    
    # These are required parameters
    if not params.get('o_zip') or not params.get('d_zip') or not params.get('lbs'):
        #TODO: raise an error here before going on 
        pass
        
    if params.get('mail_class'):
        service = params.get('mail_class')
    else:
        service = 'ALL'
    
    if service == 'FIRST CLASS' or service == 'FIRST CLASS COMMERCIAL' or service == 'FIRST CLASS HFP COMMERCIAL':
        if params.get('fcm_type'):
            fcm = params.get('fcm_type')
        else:
            # TODO: raise an error for this; it's required if the mail classes are as above
            pass
    
    o_zip = params.get('o_zip')
    d_zip = params.get('d_zip')
    
    pounds = params.get('lbs')
    
    if params.get('oz'):
        oz = params.get('oz')
    else:
        oz = 0
    
    if params.get('size'):
        size = params.get('size')
    else:
        size = 'REGULAR'
    
    if params.get('machinable'):
        machinable = params.get('machinable')
    else:
        machinable = 'true'

    xml_string = """<RateV4Request USERID="%s"><Revision/>
        <Package ID="%s">
            <Service>%s</Service>
            <ZipOrigination>%s</ZipOrigination>
            <ZipDestination>%s</ZipDestination>
            <Pounds>%s</Pounds>
            <Ounces>%s</Ounces>
            <Container/>
            <Size>%s</Size>
            <Machinable>%s</Machinable>
        </Package>
    </RateV4Request>""" % (KEY, package, service, o_zip, d_zip, pounds, oz, size, machinable)
    
    url = 'http://production.shippingapis.com/ShippingAPI.dll?API=RateV4&XML='+xml_string
    
    response = requests.get(url)
    root = ET.fromstring(response.content)
    print 'RESPONSE CONTENT ', response.content
    rate_l = []
    for postage in root[0].findall('Postage'):
        rate_d = {}
        rate = postage.find('Rate')
        mail_s = postage.find('MailService')
        rate_d['Rate'] = rate.text
        rate_d['Mail Class'] = mail_s.text
        rate_l.append(rate_d)
        
    return rate_l