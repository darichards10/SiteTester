from django.shortcuts import render
import requests
from django.http import JsonResponse
from urllib.parse import urlparse
import os

def calculate_ttfb(request):
    if 'url' in request.GET:
        url = request.GET['url']
        if not urlparse(url).scheme:
            url = 'https://' + url
        try:
            response = requests.get(url, cookies=[])
            response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes
            ttfb = response.elapsed.total_seconds()

            try:
                # Use a command-line call or a library to run Lighthouse and get the report
                lighthouse_command = f'lighthouse {url} --output=json --quiet'
                report = os.popen(lighthouse_command).read()

                # Parse the report to extract the Speed Index value
                import json
                report_data = json.loads(report)
                speed_index = report_data['audits']['speed-index']['numericValue']
            except Exception as e:
                speed_index = e.args[0]

            return JsonResponse({
                'ttfb': ttfb,
                'speed_index': speed_index,            
           })
        except requests.exceptions.RequestException as e:
            return JsonResponse({'error': str(e)})
    else:
        return JsonResponse({'error': 'URL parameter is missing'})
    
def index(request):
    return render(request, 'index.html')

