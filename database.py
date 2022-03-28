import pandas as pd
import requests
import time
from bs4 import BeautifulSoup
import re


def retry_requests(url, payloads, headers):

    for i in range(3):
        try:
            return requests.get(url, params=payloads, headers=headers)
        except:
            print('An error occurred, try after 1 minute')
            time.sleep(60)

    return None


def get_codes(url):

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.80 Safari/537.36'
    }

    response = retry_requests(url, None, headers)
    result = []
    try:
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all(href=re.compile("^javascript:Link2Stk\('"))
        for link in links:
            result.append(link.getText().split()[0])
    except:
        print('No information found')
    return result
