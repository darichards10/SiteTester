from django.shortcuts import render
import requests
from django.http import JsonResponse
from urllib.parse import urlparse

def calculate_ttfb(request):
    if 'url' in request.GET:
        url = request.GET['url']
        if not urlparse(url).scheme:
            url = 'https://' + url
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes
            ttfb = response.elapsed.total_seconds()
            return JsonResponse({'ttfb': ttfb})
        except requests.exceptions.RequestException as e:
            return JsonResponse({'error': str(e)})
    else:
        return JsonResponse({'error': 'URL parameter is missing'})
    
def index(request):
    return render(request, 'index.html')

