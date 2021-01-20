##########################################
# Web-Crawler Challenge #2.1
##########################################
import re
from string import Template

import faker
import requests
from bs4 import BeautifulSoup as bs


url = 'https://www.walmart.com/browse/4044'

fake = faker.Faker()
headers = {'User-Agent': fake.user_agent()}
dpmt_msg = Template('\n\nThe Departments of `HOME` are:\n${DEPARTMENTS}')

session = requests.Session()
resp = session.get(url, headers=headers)
soup = bs(resp.content)
pattern = re.compile('\\d+_\\d+$')
departments = [i['href'] for i in soup.find_all('a', {'href': pattern}) if len(i.attrs) == 1]

print(dpmt_msg.substitute(DEPARTMENTS='\n\t'+'\n\t'.join(departments)+'\n\n'))

##########################################
# Web-Crawler Challenge #2.2
##########################################

# from requests_html import HTMLSession
# session = HTMLSession()
# url = 'https://www.walmart.com/browse/4044'
# session.headers['User-Agent'] = fake.user_agent()
# # session.proxies.update({'https':'https://1.192.122.208:8908'})
# r = session.get(url)
# r.html.render(sleep=2, keep_page=True, scrolldown=1)
import os
import time
from io import StringIO

import lxml.html
from splinter import Browser
"""
Download the `chromedriver` from here:

    https://sites.google.com/a/chromium.org/chromedriver/downloads

and extract the downloaded folder. Be sure to download a driver that is compatible
with your current version of Chrome!
If you are using a different browser, download the right driver, and follow the
same steps. If it's not chrome, you'll need to enter a different name.
Splinter plays pretty nice with chrome and firefox.

Copy the filepath to the *directory* where the `chromedriver_dir` executable was extracted to
and paste it below, assinging it to the variable ``chromedriver_dir``
"""


chromedriver_dir = '/home/jtieken/Downloads/'
os.environ['PATH'] = os.environ['PATH'] + ":" + chromedriver_dir

b = Browser('chrome')
b.visit(url)
time.sleep(2)
text = StringIO()
text.write(b.html)
text.seek(0)
tree = lxml.html.parse(text)
page2_url = tree.xpath('//ul[@class="paginator-list"]/li/a/@href')[1]

print(f"The URL to page 2 of the `HOME` department:\n\n\t{page2_url}")

b.driver.close()
