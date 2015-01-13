from django.test import TestCase, Client
from django.core.urlresolvers import reverse

client = Client()
default_rates_string = '{"data": [{"Rate": "38.80", "Mail Class": "Priority Mail Express 1-Day&lt;sup&gt;&#8482;&lt;/sup&gt;"}, {"Rate": "38.80", "Mail Class": "Priority Mail Express 1-Day&lt;sup&gt;&#8482;&lt;/sup&gt; Hold For Pickup"}, {"Rate": "44.95", "Mail Class": "Priority Mail Express 1-Day&lt;sup&gt;&#8482;&lt;/sup&gt; Flat Rate Boxes"}, {"Rate": "44.95", "Mail Class": "Priority Mail Express 1-Day&lt;sup&gt;&#8482;&lt;/sup&gt; Flat Rate Boxes Hold For Pickup"}, {"Rate": "19.99", "Mail Class": "Priority Mail Express 1-Day&lt;sup&gt;&#8482;&lt;/sup&gt; Flat Rate Envelope"}, {"Rate": "19.99", "Mail Class": "Priority Mail Express 1-Day&lt;sup&gt;&#8482;&lt;/sup&gt; Flat Rate Envelope Hold For Pickup"}, {"Rate": "19.99", "Mail Class": "Priority Mail Express 1-Day&lt;sup&gt;&#8482;&lt;/sup&gt; Legal Flat Rate Envelope"}, {"Rate": "19.99", "Mail Class": "Priority Mail Express 1-Day&lt;sup&gt;&#8482;&lt;/sup&gt; Legal Flat Rate Envelope Hold For Pickup"}, {"Rate": "19.99", "Mail Class": "Priority Mail Express 1-Day&lt;sup&gt;&#8482;&lt;/sup&gt; Padded Flat Rate Envelope"}, {"Rate": "19.99", "Mail Class": "Priority Mail Express 1-Day&lt;sup&gt;&#8482;&lt;/sup&gt; Padded Flat Rate Envelope Hold For Pickup"}, {"Rate": "10.55", "Mail Class": "Priority Mail 2-Day&lt;sup&gt;&#8482;&lt;/sup&gt;"}, {"Rate": "17.90", "Mail Class": "Priority Mail 2-Day&lt;sup&gt;&#8482;&lt;/sup&gt; Large Flat Rate Box"}, {"Rate": "12.65", "Mail Class": "Priority Mail 2-Day&lt;sup&gt;&#8482;&lt;/sup&gt; Medium Flat Rate Box"}, {"Rate": "5.95", "Mail Class": "Priority Mail 2-Day&lt;sup&gt;&#8482;&lt;/sup&gt; Small Flat Rate Box"}, {"Rate": "5.75", "Mail Class": "Priority Mail 2-Day&lt;sup&gt;&#8482;&lt;/sup&gt; Flat Rate Envelope"}, {"Rate": "5.90", "Mail Class": "Priority Mail 2-Day&lt;sup&gt;&#8482;&lt;/sup&gt; Legal Flat Rate Envelope"}, {"Rate": "6.10", "Mail Class": "Priority Mail 2-Day&lt;sup&gt;&#8482;&lt;/sup&gt; Padded Flat Rate Envelope"}, {"Rate": "5.75", "Mail Class": "Priority Mail 2-Day&lt;sup&gt;&#8482;&lt;/sup&gt; Gift Card Flat Rate Envelope"}, {"Rate": "5.75", "Mail Class": "Priority Mail 2-Day&lt;sup&gt;&#8482;&lt;/sup&gt; Small Flat Rate Envelope"}, {"Rate": "5.75", "Mail Class": "Priority Mail 2-Day&lt;sup&gt;&#8482;&lt;/sup&gt; Window Flat Rate Envelope"}, {"Rate": "8.76", "Mail Class": "Standard Post&lt;sup&gt;&#174;&lt;/sup&gt;"}, {"Rate": "3.17", "Mail Class": "Media Mail Parcel"}, {"Rate": "3.02", "Mail Class": "Library Mail Parcel"}]}'


class RatesTest(TestCase):
    
    def test_rates_no_params(self):
        response = client.get(reverse('rates'))
        self.assertEqual(response.status_code, 200)
    
    def test_rates_200(self):
        response = client.get('/rates/', {'o_zip':78756, 'd_zip':'01354', 'lbs':2})
        self.assertEqual(response.status_code, 200)
    
    def test_rates_content(self):
        response = client.get('/rates/', {'o_zip':78756, 'd_zip':'01354', 'lbs':2})
        self.assertEqual(response.content, default_rates_string)
        
    def test_rates_content_type(self):
        response = client.get('/rates/', {'o_zip':78756, 'd_zip':'01354', 'lbs':2})
        self.assertEqual(response['Content-Type'], 'application/json')
        
        
class LabelsTest(TestCase):
    label_test_request = {'f_name':'Sophie Hernandez', 'f_address_2':'5310 Joe Sayers Ave Apt 120',\
        'f_city':'Austin','f_state':'TX','f_zip5':78756,'to_name':'Ben','to_address_2':'101 West 6th Street #405','to_city':'Austin',\
        'to_zip5':78701,'to_state':'tx', 'mail_class':'Priority','weight':5}
    
    def test_labels_no_params(self):
        response = client.get(reverse('label'))
        self.assertEqual(response.status_code, 200)
        
    def test_labels_200(self):
        response = client.get('/label/', self.label_test_request)
        self.assertEqual(response.status_code, 200)
        
    def test_labels_content_type(self):
        response = client.get('/label/', self.label_test_request)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        
    def test_labels_content(self):
        response = client.get('/label/', self.label_test_request)
        pdf_text = open('test.txt').read()
        out_text = open('out1.txt', 'w')
        out_text.write(response.content)
        out_text.close()
        out_text = open('out1.txt').read()
        self.assertEqual(out_text[:500], pdf_text[:500])