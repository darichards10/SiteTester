from django.shortcuts import render
import requests
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import json
import requests
import logging
from os import system, name 
import json
from django.http import JsonResponse
import requests
import time
import concurrent.futures


#LCP
observer_code = """
const observer = new PerformanceObserver((list) => {
  const entries = list.getEntries();
  const lastEntry = entries[entries.length - 1]; // Use the latest LCP candidate
  console.log("LCP:", lastEntry.startTime);
  console.log(lastEntry);
  const lcpData = {
    'URL': window.location.href,
    'LCP': lastEntry.startTime
  };
  window.localStorage.setItem('LCP_DATA', JSON.stringify(lcpData));
});
observer.observe({ type: 'largest-contentful-paint', buffered: true });
"""


def get_all_links(url):
    print('getting links...')
    visited_urls = set()
    if url in visited_urls:
        return []

    visited_urls.add(url)
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    links = soup.find_all('a')

    all_links = []
    for link in links:
        href = link.get('href')
        if href:
            full_url = urljoin(url, href)
            if full_url.startswith(url):
                all_links.append(full_url)

    all_links = list(set(all_links))
    return all_links

def test_all_links(links):
        
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-cookies')
    chrome_options.add_argument('--disk-cache-size=0')
    chrome_options.add_argument('--media-cache-size=0')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    logging.basicConfig(level=logging.WARNING)
    driver = webdriver.Chrome(options=chrome_options)


    data = []
    headers = ['URL', 'Time to Interactive (ms)', 'Time to First Byte (ms)', 'LCP (ms)', 'Load Time (ms)' , 'Page Size (Bytes)']

    for index, url in enumerate(links, start=1):
        if name == 'nt':
            _ = system('cls')
        else:
            _ = system('clear')
        total_urls = len(links)
        print(f"\r{index}/{total_urls} - {url}")
        
        try:
            driver.get(url)

            # Add the LCP observation code to the page before loading the URL
            driver.execute_script(observer_code)
            h = requests.head(url)

            wait = WebDriverWait(driver, 5)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

            load_time = driver.execute_script(
                "return (window.performance.timing.loadEventEnd - window.performance.timing.navigationStart) || 0"
            )
            time_to_interactive = driver.execute_script(
                "return (window.performance.timing.domInteractive - window.performance.timing.navigationStart) || 0"
            )
            time_to_first_byte = driver.execute_script(
                "return window.performance.timing.responseStart - window.performance.timing.navigationStart || 0"
            )



            # Get the LCP data stored in local storage and parse it
            lcp_data_str = driver.execute_script("return window.localStorage.getItem('LCP_DATA')")
            lcp_data = json.loads(lcp_data_str) if lcp_data_str else {'LCP': 'N/A'}

            page_size = driver.execute_script(
                "return window.performance.getEntriesByType('resource').reduce((acc, entry) => acc + entry.transferSize, 0)"
            )



            print(f"Testing URL: {url} - Load Time: {load_time} - Time to Interactive: {time_to_interactive} - Time to First Byte: {time_to_first_byte} - LCP: {lcp_data['LCP']} - Page Size: {page_size}")


            data.append({
                'URL': url,
                'Time to Interactive (ms)': time_to_interactive,
                'Time to First Byte (ms)': time_to_first_byte,
                'LCP (ms)': f'{lcp_data["LCP"]:.1f}',
                'Load Time (ms)': load_time,
                'Page Size (Bytes)': page_size
            })

        except Exception as e:
            print(f"Error for URL {url}: {e}")
    driver.quit()
    return data

import concurrent.futures

def simulate_user(url):
    try:
        start_time = time.time()
        response = requests.get(url)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        print(f"Request to {url} - Status code: {response.status_code} - Response Time: {response_time:.2f} seconds")
        
        return url, round(float(response_time), 3)
    except requests.RequestException as e:
        print(f"Error requesting {url}: {e}")
        return None
    
def load_test(urls, users, ramp_up_time, hold_time):
    response_times = []  # List to store response times
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(simulate_user, url) for url in urls for _ in range(int(users))]
        
        for future in concurrent.futures.as_completed(futures):
            response_time = future.result()
            if response_time is not None:
                response_times.append(response_time)
            
            # Ramp up time between user threads
            time.sleep(int(ramp_up_time) / int(users))
        
        # Hold time for all user threads
        time.sleep(int(hold_time))
    
    return response_times

def run_test(request):
    if request.method == 'GET':
        url = request.GET.get('url')
        users = request.GET.get('users')
        ramp_up = request.GET.get('ramp_up')
        hold_time = request.GET.get('hold_time')
    links = get_all_links(url)
    data = test_all_links(links)
    load_data = load_test(links, users, ramp_up, hold_time)
    combined_data = {
        'test_results': data,
        'load_test_results': load_data
    }
    json_response = json.dumps(combined_data)

    return JsonResponse({'result': json_response})

def index(request):
    return render(request, 'index.html')

