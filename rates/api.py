import requests
import xml.etree.ElementTree as ET

USPS_KEY = '161SELF05974'
USPS_PASS = '136AV76AZ752'
SERVER = 'https://secure.shippingapis.com/ShippingAPI.dll'


# Error to throw might need JSON response rather than simple string
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
    if size.lower() == 'large':
        width = params.get('width')
        height = params.get('height')
        length = params.get('length')
        girth = params.get('girth')
    machinable = params.get('machinable', 'true')
    
    if fcm == '' and service == 'FIRST CLASS' \
    or service == 'FIRST CLASS COMMERCIAL' \
    or service == 'FIRST CLASS HFP COMMERCIAL':
        raise BadRequestError(2, 'You must specify a first class mail type (fcm_type) for First Class Service')

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
            <Width>%s</Width>
            <Height>%s</Height>
            <Length>%s</Length>
            <Girth>%s</Girth>
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
        rate_list.append(rate_d)
    rate_response = {'data': rate_list}
    return rate_response
    
    
def build_label_xml(label_list):
    labels = ['FromName', 'FromFirm', 'FromAddress1', 'FromAddress2', 'FromCity', 'FromState', 'FromZip5', 'FromZip4',\
            'ToName', 'ToFirm','ToAddress1','ToAddress2','ToCity','ToState','ToZip5','ToZip4',\
            'ToPOBoxFlag', 'WeightInOunces', 'ServiceType', 'SeparateReceiptPage', 'POZipCode','ImageType','AddressServiceRequested',\
            'HoldForManifest', 'Container','Size','Width','Length','Height','Girth','ReturnCommitments']
    root = ET.Element('DelivConfirmCertifyV4.0Request', attrib={'USERID':USPS_KEY, 'PASSWORD':USPS_PASS})
    ET.SubElement(root, 'Revision').text = '2'
    for i in range(len(labels)):
        ET.SubElement(root, labels[i]).text = label_list[i+2]
    return ET.tostring(root, encoding="UTF-8", method='xml')

# Get helper for view for label retrieval    
def get_label_from_usps(params):
    delivery_confirm = [USPS_KEY, USPS_PASS]
    delivery_confirm.append(params.get('f_name', ''))
    delivery_confirm.append(params.get('f_company', ''))
    delivery_confirm.append(params.get('f_address_1',''))
    delivery_confirm.append(params.get('f_address_2'))
    delivery_confirm.append(params.get('f_city'))
    delivery_confirm.append(params.get('f_state'))
    delivery_confirm.append(params.get('f_zip5'))
    delivery_confirm.append(params.get('f_zip4', ''))
    
    delivery_confirm.append(params.get('to_name', ''))
    delivery_confirm.append(params.get('to_company', ''))
    delivery_confirm.append(params.get('to_address_1',''))
    delivery_confirm.append(params.get('to_address_2'))
    delivery_confirm.append(params.get('to_city'))
    delivery_confirm.append(params.get('to_state'))
    delivery_confirm.append(params.get('to_zip5'))
    delivery_confirm.append(params.get('to_zip4', ''))
    delivery_confirm.append(params.get('to_pob', ''))
    
    delivery_confirm.append(params.get('weight', ''))
    delivery_confirm.append(params.get('mail_class', ''))
    delivery_confirm.append(params.get('separate_receipt', ''))
    delivery_confirm.append(params.get('po_zip', ''))
    delivery_confirm.append('PDF')
    delivery_confirm.append(params.get('address_service_request',''))
    delivery_confirm.append(params.get('hold_for_manifest',''))
    
    delivery_confirm.append(params.get('container', ''))
    delivery_confirm.append(params.get('size',''))
    delivery_confirm.append(params.get('width', ''))
    delivery_confirm.append(params.get('length', ''))
    delivery_confirm.append(params.get('height', ''))
    delivery_confirm.append(params.get('girth', ''))
    delivery_confirm.append(params.get('return_commitments',''))
    
    label_xml = build_label_xml(delivery_confirm)
    data = {'XML':label_xml, 'API':'DelivConfirmCertifyV4'}
    label_response = requests.get(SERVER, params=data)
    
    root = ET.fromstring(label_response.content)
    # Pass through USPS Error code
    if root.tag == 'Error':
        raise BadRequestError(4, root.find('Description').text)
    else:
        image = root.find('DeliveryConfirmationLabel').text
        img_name = root.find('DeliveryConfirmationNumber').text + '.pdf'
        return (image, img_name)