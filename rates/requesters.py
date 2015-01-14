import requests
import xml.etree.ElementTree as ET
from ratesapp.settings import DEBUG
from collections import OrderedDict

# Error to throw might need JSON response rather than simple string
class BadRequestError(Exception):
    def __init__(self, number, description):
        self.number = number
        self.description = description
    def __str__(self):
        return 'Error number: %s\n Description: %s' % (self.number, self.description)
        
         
class USPSRequester(object):
    USPS_KEY = '161SELF05974'
    USPS_PASS = '136AV76AZ752'
    LABEL_SERVER = 'https://secure.shippingapis.com/ShippingAPI.dll'
    RATE_SERVER = 'http://production.shippingapis.com/ShippingAPI.dll'
    SERVER = {'rate':RATE_SERVER, 'label':LABEL_SERVER}
    
    def __init__(self, endpoint_type, request_qd):
        self.endpoint_type = endpoint_type
        self.request_qd = request_qd
        self.dict_of_request = OrderedDict()
        
    def validate_size(self):
        if not self.dict_of_request['Width'] \
        or not self.dict_of_request['Length'] \
        or not self.dict_of_request['Height'] \
        or not self.dict_of_request['Girth']:
            raise BadRequestError(2, 'Dimensions are missing for package;\
             unable to calculate postage. Additional Info: All dimensions \
             must be greater than 0.')

    
    def build_xml_root(self):
        root = ET.Element(self.request_type, attrib={'USERID':self.USPS_KEY, 'PASSWORD':self.USPS_PASS})
        if self.endpoint_type == 'rate':
            ET.SubElement(root,'Revision')
        elif self.endpoint_type == 'label':
            ET.SubElement(root, 'Revision').text = '2'
        return root

    def generate_xml_string(self):
        root = self.build_xml_root()
        for elem in self.dict_of_request:
            ET.SubElement(root, elem).text = self.dict_of_request[elem]
        return ET.tostring(root, encoding="UTF-8", method="xml")
        
    def make_request(self):
        xml = self.generate_xml_string()
        data = {'XML':xml, 'API':self.API}
        return ET.fromstring((requests.get(self.SERVER[self.endpoint_type], params=data)).content)
        
class RatesRequester(USPSRequester):
    international = False
    API = 'RateV4'
    request_type = 'RateV4Request'
    def __init__(self, request_qd):
        super(RatesRequester, self).__init__('rate', request_qd)
        self.required = ['d_zip','o_zip','lbs']
        
    def setup_international(self):
        self.international = True
        self.API = 'IntlRateV2'
        self.request_type = 'IntlRateV2Request'
        self.required = ['lbs','oz','mail_type','value']
    
    def fill_dict_of_requests(self):
        if self.request_qd.get('country'):
            self.setup_international()
            self.validate_required_fields()
            self.dict_of_request['Pounds'] = self.request_qd.get('lbs', '0')
            self.dict_of_request['Ounces'] = self.request_qd.get('oz', '')
            self.dict_of_request['Machinable'] = self.request_qd.get('machinable', 'true')
            self.dict_of_request['MailType'] = self.request_qd.get('mail_type')
            self.dict_of_request['ValueOfContents'] = self.request_qd.get('value')
            self.dict_of_request['Country'] = self.request_qd.get('country')
            self.dict_of_request['Container'] = self.request_qd.get('container', '')
            self.dict_of_request['Size'] = self.request_qd.get('size', 'REGULAR')
            
            self.dict_of_request['Width'] = self.request_qd.get('width',1)
            self.dict_of_request['Length'] = self.request_qd.get('length',1)
            self.dict_of_request['Height'] = self.request_qd.get('height',1)
            self.dict_of_request['Girth'] = self.request_qd.get('girth',0)
            if self.dict_of_request['Size'].lower() == 'large':
                self.validate_size()
        else:
            self.validate_required_fields()
            self.dict_of_request['Service'] = self.request_qd.get('mail_class', 'ALL')
            self.dict_of_request['FirstClassMailType'] = self.request_qd.get('fcm_type', '')
            self.validate_first_class()
            self.dict_of_request['ZipOrigination'] = self.request_qd.get('o_zip')
            self.dict_of_request['ZipDestination'] = self.request_qd.get('d_zip')
            self.dict_of_request['Pounds'] = self.request_qd.get('lbs', '0')
            self.dict_of_request['Ounces'] = self.request_qd.get('oz', '0')
            self.dict_of_request['Container'] = self.request_qd.get('container', '')
            #validate container if size == large
            self.dict_of_request['Size'] = self.request_qd.get('size', 'REGULAR')
            if self.dict_of_request['Size'].lower() == 'large':
                self.dict_of_request['Width'] = self.request_qd.get('width')
                self.dict_of_request['Length'] = self.request_qd.get('length')
                self.dict_of_request['Height'] = self.request_qd.get('height')
                self.dict_of_request['Girth'] = self.request_qd.get('girth')
                self.validate_size()
            # self.dict_of_request['Value'] = self.request_qd.get('value','')
            # self.dict_of_request['AmountToCollect'] = self.request_qd.get('amt_to_collect','')
            self.dict_of_request['Machinable'] = self.request_qd.get('machinable', 'true')
            # self.dict_of_request['ReturnLocations'] = self.request_qd.get('return_loc','')
            # self.dict_of_request['ReturnServiceInfo']= self.request_qd.get('return_info','')
        
    def generate_xml_string(self):
        root = super(RatesRequester, self).build_xml_root()
        package = ET.SubElement(root,'Package', attrib={'ID':'1ST'})
        for elem in self.dict_of_request:
            ET.SubElement(package, elem).text = str(self.dict_of_request[elem])
        return ET.tostring(root, encoding="UTF-8", method='xml')
    
    def validate_required_fields(self):
        # These are required parameters
        for param in self.required:
            if not self.request_qd.get(param):
                raise BadRequestError(1, 'You are missing the required %s'%param)
        
    
    def validate_first_class(self):
        if self.dict_of_request['FirstClassMailType'] == '' and \
          self.dict_of_request['Service'] == 'FIRST CLASS' \
          or self.dict_of_request['Service'] == 'FIRST CLASS COMMERCIAL' \
          or self.dict_of_request['Service'] == 'FIRST CLASS HFP COMMERCIAL':
            raise BadRequestError(2, 'You must specify a first class mail type (fcm_type) for First Class Service')
    
    def create_response(self, root):
        rate_list = []
        if self.international:
            keys = ['Service', 'Postage','SvcDescription']
        else:
            keys = ['Postage', 'Rate','MailService']
        #then parse and return the data into a dictionary with a list of rates
        for postage in root[0].findall(keys[0]):
            rate = postage.find(keys[1])
            mail_s = postage.find(keys[2])
            rate_list.append({'Rate': rate.text, 'Mail Class': mail_s.text})
        return rate_list

class LabelRequester(USPSRequester):
    request_type = 'DelivConfirmCertifyV4.0Request'
    API = 'DelivConfirmCertifyV4'
    def __init__(self, request_qd):
        super(LabelRequester, self).__init__('label',request_qd)
    
    def fill_dict_of_requests(self):
        self.dict_of_request['FromName'] = self.request_qd.get('f_name', '')
        self.dict_of_request['FromFirm'] = self.request_qd.get('f_company', '')
        self.dict_of_request['FromAddress1'] = self.request_qd.get('f_address_1','')
        self.dict_of_request['FromAddress2'] = self.request_qd.get('f_address_2')
        self.dict_of_request['FromCity'] = self.request_qd.get('f_city')
        self.dict_of_request['FromState'] = self.request_qd.get('f_state')
        self.dict_of_request['FromZip5'] = self.request_qd.get('f_zip5')
        self.dict_of_request['FromZip4'] = self.request_qd.get('f_zip4', '')
    
        self.dict_of_request['ToName'] = self.request_qd.get('to_name', '')
        self.dict_of_request['ToFirm'] = self.request_qd.get('to_company', '')
        self.dict_of_request['ToAddress1'] = self.request_qd.get('to_address_1','')
        self.dict_of_request['ToAddress2'] = self.request_qd.get('to_address_2')
        self.dict_of_request['ToCity'] = self.request_qd.get('to_city')
        self.dict_of_request['ToState'] = self.request_qd.get('to_state')
        self.dict_of_request['ToZip5'] = self.request_qd.get('to_zip5')
        self.dict_of_request['ToZip4'] = self.request_qd.get('to_zip4', '')
        self.dict_of_request['ToPOBoxFlag'] = self.request_qd.get('to_pob', '')
    
        self.dict_of_request['WeightInOunces'] = self.request_qd.get('weight', '')
        self.dict_of_request['ServiceType'] = self.request_qd.get('mail_class', '')
        self.dict_of_request['SeparateReceiptPage'] = self.request_qd.get('separate_receipt', '')
        self.dict_of_request['POZipCode'] = self.request_qd.get('po_zip', '')
        self.dict_of_request['ImageType'] = 'PDF'
        self.dict_of_request['AddressServiceRequested'] = self.request_qd.get('address_service_request','')
        self.dict_of_request['HoldForManifest'] = self.request_qd.get('hold_for_manifest','')
    
        self.dict_of_request['Container'] = self.request_qd.get('container', '')
        self.dict_of_request['Size'] = self.request_qd.get('size','')
        if self.dict_of_request['Size'].lower() == 'large':
            self.dict_of_request['Width'] = self.request_qd.get('width', '')
            self.dict_of_request['Length'] = self.request_qd.get('length', '')
            self.dict_of_request['Height'] = self.request_qd.get('height', '')
            self.dict_of_request['Girth'] = self.request_qd.get('girth', '')
            self.validate_size()
        self.dict_of_request['ReturnCommitments'] = self.request_qd.get('return_commitments','')
        
    def create_response(self, root):
        # Pass through USPS Error code
        if root.tag == 'Error':
            raise BadRequestError(4, root.find('Description').text)
        else:
            image = root.find('DeliveryConfirmationLabel').text
            img_name = root.find('DeliveryConfirmationNumber').text + '.pdf'
            return (image, img_name)