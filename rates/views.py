from django.shortcuts import render
from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_GET
import requests
from api import get_rates_from_usps


# View for getting rates from USPS
@require_GET
def rates(request):
    response = get_rates_from_usps(request.GET)
    print request.GET['o_zip']
    return JsonResponse(response, safe=False)