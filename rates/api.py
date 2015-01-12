import requests
import xml.etree.ElementTree as ET

USPS_KEY = '161SELF05974'
USPS_PASS = '136AV76AZ752'

#Error to throw might need JSON response rather than simple string
class BadRequestError(Exception):
    def __init__(self, number, description):
        self.number = number
        self.description = description
    def __str__(self):
        return 'Error number: %s\n Description: %s' % (self.number, self.description)
        

def validate_required_rates(params):
    # These are required parameters
    if not params.get('o_zip') or not params.get('d_zip') or not params.get('lbs'):
        raise BadRequestError(1, 'You are missing the required parameters')

def get_rates_from_usps(params):
    package = '1ST'
    
    # check that the required params are good
    validate_required_rates(params)
        
    service = params.get('mail_class', 'ALL')
    fcm = params.get('fcm_type', '')
    o_zip = params.get('o_zip')
    d_zip = params.get('d_zip')
    pounds = params.get('lbs', 0)
    container = params.get('container', '')
    oz = params.get('oz', 0)
    size = params.get('size', 'REGULAR')
    machinable = params.get('machinable', 'true')
    
    if fcm == '' and service == 'FIRST CLASS' \
    or service == 'FIRST CLASS COMMERCIAL' \
    or service == 'FIRST CLASS HFP COMMERCIAL':
        raise BadRequestError(2, 'You must specify a first class mail type for First Class Service')

    xml_string = """<RateV4Request USERID="%s"><Revision/>
        <Package ID="%s">
            <Service>%s</Service>
            <FirstClassMailType>%s</FirstClassMailType>
            <ZipOrigination>%s</ZipOrigination>
            <ZipDestination>%s</ZipDestination>
            <Pounds>%s</Pounds>
            <Ounces>%s</Ounces>
            <Container>%s</Container>
            <Size>%s</Size>
            <Machinable>%s</Machinable>
        </Package>
    </RateV4Request>""" % \
    (USPS_KEY, package, service, fcm, o_zip, d_zip, pounds, oz, container, size, machinable)
    
    url = 'http://production.shippingapis.com/ShippingAPI.dll?API=RateV4&XML='+xml_string
    
    response = requests.get(url)
    root = ET.fromstring(response.content)
        
    rate_list = []
    for postage in root[0].findall('Postage'):
        rate_d = {}
        rate = postage.find('Rate')
        mail_s = postage.find('MailService')
        rate_d['Rate'] = rate.text
        rate_d['Mail Class'] = mail_s.text
        rate_l.append(rate_d)
    rate_response = {'data': rate_list}
    return rate_response
    
    
import itertools
# Get helper for view for label retrieval    
def get_label_from_usps(params):
    '''
    Grabbing the label
    '''
    delivery_confirm = [USPS_KEY, USPS_PASS]
    delivery_confirm.append(params.get('f_name', ''))
    delivery_confirm.append(params.get('f_company', ''))
    delivery_confirm.append(params.get('f_address_1'))
    delivery_confirm.append(params.get('f_address_2',''))
    delivery_confirm.append(params.get('f_city'))
    delivery_confirm.append(params.get('f_state'))
    delivery_confirm.append(params.get('f_zip5'))
    delivery_confirm.append(params.get('f_zip4', ''))
    
    delivery_confirm.append(params.get('to_name', ''))
    delivery_confirm.append(params.get('to_company', ''))
    delivery_confirm.append(params.get('to_address_1'))
    delivery_confirm.append(params.get('to_address_2',''))
    delivery_confirm.append(params.get('to_city'))
    delivery_confirm.append(params.get('to_state'))
    delivery_confirm.append(params.get('to_zip5'))
    delivery_confirm.append(params.get('to_zip4', ''))
    delivery_confirm.append(params.get('to_pob', ''))
    
    delivery_confirm.append(params.get('weight', ''))
    delivery_confirm.append(params.get('mail_class', ''))
    delivery_confirm.append(params.get('separate_receipt', ''))
    delivery_confirm.append(params.get('po_zip', ''))
    delivery_confirm.append(params.get('address_service_request',''))
    delivery_confirm.append(params.get('hold_for_manifest',''))
    
    delivery_confirm.append(params.get('container', ''))
    delivery_confirm.append(params.get('size',''))
    delivery_confirm.append(params.get('width', ''))
    delivery_confirm.append(params.get('length', ''))
    delivery_confirm.append(params.get('height', ''))
    delivery_confirm.append(params.get('girth', ''))
    
    delivery_confirm.append(params.get('return_commitments',''))
    
    label_xml = '''<?xml version="1.0" encoding="UTF-8" ?>
    <DelivConfirmCertifyV4.0Request USERID="%s" PASSWORD="%s">
      <Revision>2</Revision>
      <ImageParameters />
      
      <FromName>%s</FromName>
      <FromFirm>%s</FromFirm>
      <FromAddress1>%s</FromAddress1>
      <FromAddress2>%s</FromAddress2>
      <FromCity>%s</FromCity>
      <FromState>%s</FromState>
      <FromZip5>%s</FromZip5>
      <FromZip4>%s</FromZip4>
      
      <ToName>%s</ToName>
      <ToFirm>%s</ToFirm>
      <ToAddress1>%s</ToAddress1>
      <ToAddress2>%s</ToAddress2>
      <ToCity>%s</ToCity>
      <ToState>%s</ToState>
      <ToZip5>%s</ToZip5>
      <ToZip4>%s</ToZip4>
      
      <ToPOBoxFlag>%s</ToPOBoxFlag>
      <WeightInOunces>%s</WeightInOunces>
      <ServiceType>%s</ServiceType>
      <SeparateReceiptPage>%s</SeparateReceiptPage>
      <POZipCode>%s</POZipCode>
      <ImageType>PDF</ImageType>
      <AddressServiceRequested>%s</AddressServiceRequested>
      <HoldForManifest>%s</HoldForManifest>
      
      <Container>%s</Container>
      <Size>%s</Size>
      <Width>%s</Width>
      <Length>%s</Length>
      <Height>%s</Height>
      <Girth>%s</Girth>
      
     <ReturnCommitments>%s</ReturnCommitments>
    </DelivConfirmCertifyV4.0Request> 
    ''' % (tuple(delivery_confirm))
    label_url = 'https://secure.shippingapis.com/ShippingAPI.dll?API=DelivConfirmCertifyV4&XML='+label_xml
    label_response = requests.get(label_url)
    root = ET.fromstring(label_response.content)
    if root.tag == 'Error':
        raise BadRequestError(4, root.find('Description').text)
    image = root.find('DeliveryConfirmationLabel').text
    img_name = root.find('DeliveryConfirmationNumber').text + '.png'
    return image