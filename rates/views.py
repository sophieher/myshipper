from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_GET
import requests
from api import get_rates_from_usps, get_label_from_usps


# View for getting rates from USPS
@require_GET
def rates(request):
    response = get_rates_from_usps(request.GET)
    print request.GET['o_zip']
    return JsonResponse(response)
  
  
# View for getting a label from USPS
@require_GET    
def label(request):
    response = get_label_from_usps(request.GET)
    # image = response.decode('base64')
    # print image
    # return HttpResponse(image, content_type="image/png")
    return HttpResponse(response)