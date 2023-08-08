import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import json
import requests
import sys
import logging
from os import system, name 

website_url = str(sys.argv[1])
visited_urls = set()

def get_all_links(url, website_url):
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
            full_url = urljoin(website_url, href)  # Convert to absolute URL
            if full_url.startswith(website_url):
                all_links.append(full_url)

    return all_links

all_links = get_all_links(website_url, website_url)
all_links = list(set(all_links))
print("Number of links: {}".format(len(all_links)))

# Add the LCP observation code here
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

urls = all_links
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

for index, url in enumerate(urls, start=1):
    if name == 'nt':
        _ = system('cls')
    else:
        _ = system('clear')
    total_urls = len(urls)
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

csv_file = str(sys.argv[2])  # Replace with your desired output file name

with open(csv_file, 'w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=headers)
    writer.writeheader()
    del data[0]
    writer.writerows(data)

print("Data saved successfully!")
