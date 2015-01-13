from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_GET
import requests
from api import get_rates_from_usps, get_label_from_usps, BadRequestError


def bad_error(e):
    data = HttpResponse(status=400)  
    data.write(e)    
    return data
    
# View for getting rates from USPS
@require_GET
def rates(request):
    try:
        response = get_rates_from_usps(request.GET)
        return JsonResponse(response)
    except BadRequestError as e:        
        return bad_error(e)
  
  
# View for getting a label from USPS
@require_GET    
def label(request):
    try:
        response = get_label_from_usps(request.GET)
        image = response[0].decode('base64')
        data = HttpResponse(image, content_type="application/pdf")
        data['Content-Disposition'] = 'filename=%s'%response[1]
        return data
    except BadRequestError as e:  
        data = HttpResponse(status=400)  
        data.write(e)    
        return bad_error(e)