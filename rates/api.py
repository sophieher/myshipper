import requests

import xml.etree.ElementTree as ET

def validate_required_rates(params):
    # These are required parameters
    if not params.get('o_zip') or not params.get('d_zip') or not params.get('lbs'):
        #TODO: raise an error here before going on 
        pass

def get_rates_from_usps(params):
    data = {'data': 'something'}
    KEY = '564ORDOR2223'
    package = '1ST'
    
    # check that the required params are good
    if not validate_required_rates(params):
        pass #raise the error
        
    if params.get('mail_class'):
        service = params.get('mail_class', 'ALL')
    
    if service == 'FIRST CLASS' or service == 'FIRST CLASS COMMERCIAL' or service == 'FIRST CLASS HFP COMMERCIAL':
        if params.get('fcm_type'):
            fcm = params.get('fcm_type')
        else:
            # TODO: raise an error for this; it's required if the mail classes are as above
            pass
    
    o_zip = params.get('o_zip')
    d_zip = params.get('d_zip')
    
    pounds = params.get('lbs')
    

    oz = params.get('oz', 0)
    
    size = params.get('size', 'REGULAR')
    
    machinable = params.get('machinable', 'true')

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
    rate_response = {'data': rate_l}
    return rate_response
    
def get_label_from_usps(params):
    '''
    Grabbing the label
    '''
    label_xml = '''<?xml version="1.0" encoding="UTF-8" ?>
    <DelivConfirmCertifyV4.0Request USERID="161SELF05974" PASSWORD="136AV76AZ752">
      <Revision>2</Revision>
      <ImageParameters />
      <FromName>John Doe</FromName>
      <FromFirm>USPS</FromFirm>
      <FromAddress1>RM 2100</FromAddress1>
      <FromAddress2>475 LEnfant Plaza SW</FromAddress2>
      <FromCity>Washington</FromCity>
      <FromState>DC</FromState>
      <FromZip5>20260</FromZip5>
      <FromZip4/>
      <ToName>Janice Dickens</ToName>
      <ToFirm>XYZ Corporation</ToFirm>
      <ToAddress1>Ste 100</ToAddress1>
      <ToAddress2>2 Massachusetts Ave NE</ToAddress2>
      <ToCity>Washington</ToCity>
      <ToState>DC</ToState>
      <ToZip5>20212</ToZip5>
      <ToZip4 />
      <ToPOBoxFlag></ToPOBoxFlag>
      <WeightInOunces>10</WeightInOunces>
      <ServiceType>Priority</ServiceType>
      <SeparateReceiptPage>False</SeparateReceiptPage>
      <POZipCode>20770</POZipCode>
      <ImageType>TIF</ImageType>
      <AddressServiceRequested>False</AddressServiceRequested>
      <HoldForManifest>N</HoldForManifest>
      <Container>NONRECTANGULAR</Container>
      <Size>LARGE</Size>
      <Width>7</Width>
      <Length>20.5</Length>
      <Height>15</Height>
      <Girth>60</Girth>
     <ReturnCommitments>true</ReturnCommitments>
    </DelivConfirmCertifyV4.0Request> 
    '''
    label_url = 'https://secure.shippingapis.com/ShippingAPI.dll?API=DelivConfirmCertifyV4&XML='+label_xml
    label_response = requests.get(label_url)
    root = ET.fromstring(label_response.content)
    image = root.find('DeliveryConfirmationLabel').text
    img_name = root.find('DeliveryConfirmationNumber').text + '.png'
    return image