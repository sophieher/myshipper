from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import requests
import xml.etree.ElementTree as ET

# Create your views here.

def rates(request):
    data = {'data': 'something'}
    KEY = '564ORDOR2223'
    package = '1ST'
    service = 'ALL'
    fcm = 'LETTER'
    o_zip = '44106'
    d_zip = '20770'
    pounds = '0'
    oz = '3.5'
    size = 'REGULAR'
    machinable = 'true'

    xml_string = """<RateV4Request USERID="%s"><Revision/>

        <Package ID="%s">
            <Service>%s</Service>

            <FirstClassMailType>%s</FirstClassMailType>

            <ZipOrigination>%s</ZipOrigination>

            <ZipDestination>%s</ZipDestination>

            <Pounds>%s</Pounds>

            <Ounces>%s</Ounces>

            <Container/>

            <Size>%s</Size>

            <Machinable>%s</Machinable>

        </Package>
    </RateV4Request>""" % (KEY, package, service, fcm, o_zip, d_zip, pounds, oz, size, machinable)
    
    url = 'http://production.shippingapis.com/ShippingAPI.dll?API=RateV4&XML='+xml_string
    
    response = requests.get(url)
    root = ET.fromstring(response.content)

    rate_l = []
    for postage in root[0].findall('Postage'):
        rate_d = {}
        rate = postage.find('Rate')
        mail_s = postage.find('MailService')
        rate_d['Rate'] = rate.text
        rate_d['Mail Class'] = mail_s.text
        rate_l.append(rate_d)
    return JsonResponse(rate_l, safe=False)