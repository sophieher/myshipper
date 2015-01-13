import requests
import xml.etree.ElementTree as ET
from ratesapp.settings import DEBUG

USPS_KEY = '161SELF05974'
USPS_PASS = '136AV76AZ752'
LABEL_SERVER = 'https://secure.shippingapis.com/ShippingAPI.dll'
RATE_SERVER = 'http://production.shippingapis.com/ShippingAPI.dll'
SERVER = {'rate':RATE_SERVER, 'label':LABEL_SERVER}

API = {'rate':'RateV4','label':'DelivConfirmCertifyV4'}
# Would change the API if User ID key was validated for actual label printing
if DEBUG:
    LABEL_API = 'DelivConfirmCertifyV4'
    LABEL_REQUEST = 'DelivConfirmCertifyV4.0Request'
else:
    LABEL_API = 'DeliveryConfirmationV4'
    LABEL_REQUEST = 'DeliveryConfirmationV4.0Request'
    

# Error to throw might need JSON response rather than simple string
class BadRequestError(Exception):
    def __init__(self, number, description):
        self.number = number
        self.description = description
    def __str__(self):
        return 'Error number: %s\n Description: %s' % (self.number, self.description)
        
class DictBuilder(object):
    def __init__(self, key_list,params):
        self.od = OrderedDict(zip(key_list, params))
        print self.od
    def getdict(self):
        return self.od
    
def validate_required_rates(params):
    # These are required parameters
    if not params.get('o_zip'):
        raise BadRequestError(1, 'You are missing the required origin zip')
    elif not params.get('d_zip'):
        raise BadRequestError(1, 'You are missing the required destination zip')
    elif not params.get('lbs'):
        raise BadRequestError(1, 'You are missing the required weight in lbs')

       
def build_xml_root(endpoint):
    if endpoint == 'rate':
        root = ET.Element('RateV4Request', attrib={'USERID':USPS_KEY})
        ET.SubElement(root,'Revision')
    elif endpoint == 'label':
        root = ET.Element(LABEL_REQUEST, attrib={'USERID':USPS_KEY, 'PASSWORD':USPS_PASS})
        ET.SubElement(root, 'Revision').text = '2'
    return root

def build_xml(endpoint, dict_of_request):
    root = build_xml_root(endpoint)
    if endpoint=='rate':
        package = ET.SubElement(root,'Package', attrib={'ID':'1ST'})
        for elem in dict_of_request:
            ET.SubElement(package, elem).text = dict_of_request[elem]
    elif endpoint=='label':
        for elem in dict_of_request:
            ET.SubElement(root, elem).text = dict_of_request[elem]
    return ET.tostring(root, encoding="UTF-8", method='xml')

from collections import OrderedDict
def get_rates_from_usps(params):    
    # check that the required params are good
    # print build_xml('rate', DictBuilder(rater, params).getdict())
    validate_required_rates(params)
    rate = OrderedDict()
    
    rate['Service'] = params.get('mail_class', 'ALL')
    rate['FirstClassMailType'] = params.get('fcm_type', '')
    rate['ZipOrigination'] = params.get('o_zip')
    rate['ZipDestination'] = params.get('d_zip')
    rate['Pounds'] = params.get('lbs', '0')
    rate['Ounces'] = params.get('oz', '0')
    rate['Container'] = params.get('container', '')
    rate['Size'] = params.get('size', 'REGULAR')
    
    if rate['Size'].lower() == 'large':
        rate['Width'] = params.get('width')
        rate['Length'] = params.get('length')
        rate['Height'] = params.get('height')
        rate['Girth'] = params.get('girth')
        if not rate['Width'] or not rate['Length'] or not rate['Height'] or not rate['Girth']:
            raise BadRequestError(2, 'Dimensions are missing for package; unable to calculate postage. Additional Info: All dimensions must be greater than 0.')
    rate['Machinable'] = params.get('machinable', 'true')
    
    if rate['FirstClassMailType'] == '' and rate['Service'] == 'FIRST CLASS' \
    or rate['Service'] == 'FIRST CLASS COMMERCIAL' \
    or rate['Service'] == 'FIRST CLASS HFP COMMERCIAL':
        raise BadRequestError(2, 'You must specify a first class mail type (fcm_type) for First Class Service')

    st = usps_request('rate', rate).content
    root = ET.fromstring(st)
    rate_list = []
    for postage in root[0].findall('Postage'):
        rate = postage.find('Rate')
        mail_s = postage.find('MailService')
        rate_list.append({'Rate': rate.text, 'Mail Class': mail_s.text})
    rate_response = {'data': rate_list}
    return rate_response
    
def usps_request(endpoint_type, dict_of_request):
    xml = build_xml(endpoint_type,dict_of_request)
    data = {'XML':xml, 'API':API[endpoint_type]}
    return requests.get(SERVER[endpoint_type], params=data)

# Get helper for view for label retrieval    
def get_label_from_usps(params):
    labels = OrderedDict()
    labels['FromName'] = params.get('f_name', '')
    labels['FromFirm'] = params.get('f_company', '')
    labels['FromAddress1'] = params.get('f_address_1','')
    labels['FromAddress2'] = params.get('f_address_2')
    labels['FromCity'] = params.get('f_city')
    labels['FromState'] = params.get('f_state')
    labels['FromZip5'] = params.get('f_zip5')
    labels['FromZip4'] = params.get('f_zip4', '')
    
    labels['ToName'] = params.get('to_name', '')
    labels['ToFirm'] = params.get('to_company', '')
    labels['ToAddress1'] = params.get('to_address_1','')
    labels['ToAddress2'] = params.get('to_address_2')
    labels['ToCity'] = params.get('to_city')
    labels['ToState'] = params.get('to_state')
    labels['ToZip5'] = params.get('to_zip5')
    labels['ToZip4'] = params.get('to_zip4', '')
    labels['ToPOBoxFlag'] = params.get('to_pob', '')
    
    labels['WeightInOunces'] = params.get('weight', '')
    labels['ServiceType'] = params.get('mail_class', '')
    labels['SeparateReceiptPage'] = params.get('separate_receipt', '')
    labels['POZipCode'] = params.get('po_zip', '')
    labels['ImageType'] = 'PDF'
    labels['AddressServiceRequested'] = params.get('address_service_request','')
    labels['HoldForManifest'] = params.get('hold_for_manifest','')
    
    labels['Container'] = params.get('container', '')
    labels['Size'] = params.get('size','')
    labels['Width'] = params.get('width', '')
    labels['Length'] = params.get('length', '')
    labels['Height'] = params.get('height', '')
    labels['Girth'] = params.get('girth', '')
    labels['ReturnCommitments'] = params.get('return_commitments','')
    
    st = usps_request('label', labels).content
    root = ET.fromstring(st)
    # Pass through USPS Error code
    if root.tag == 'Error':
        raise BadRequestError(4, root.find('Description').text)
    else:
        image = root.find('DeliveryConfirmationLabel').text
        img_name = root.find('DeliveryConfirmationNumber').text + '.pdf'
        return (image, img_name)