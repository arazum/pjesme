#! /usr/bin/python

from pyquery import PyQuery as pq
import pycurl
from urllib import urlencode
from io import BytesIO
import time


LIST_FILE = 'list2.txt'
COOKIEJAR = 'cookies.txt'
OUTPUT_FORMAT = 'songs/{}'

QUERY_URL = 'http://www.youtube.com/results?search_query={}'
SELECTOR = 'h3.yt-lockup-title > a'
YOUTUBE_URL = 'http://www.youtube.com{}'
CONVERT_URL = 'http://www.flv2mp3.org/convert/'
DOWNLOAD_URL = 'http://www.flv2mp3.org/download/direct/mp3/yt_{}/'


f = open(LIST_FILE, 'r')
names = map(lambda x: x[:-1], f.readlines())

for name in names:
    doc = pq(QUERY_URL.format(name))
    path = doc(SELECTOR).attr('href')

    url = YOUTUBE_URL .format(path)
    id = path[9:]
    postdata = {'url': url, 'format': 1, 'service': 'youtube'}

    c = pycurl.Curl()
    c.setopt(c.URL, CONVERT_URL)
    c.setopt(c.POSTFIELDS, urlencode(postdata))
    c.setopt(c.WRITEFUNCTION, lambda x: None)
    c.setopt(c.COOKIEJAR, COOKIEJAR)
    c.perform()

    time.sleep(35)

    f = open(OUTPUT_FORMAT.format(name), 'w')

    c.setopt(c.URL, DOWNLOAD_URL.format(id))
    c.setopt(c.FOLLOWLOCATION, True)
    c.setopt(c.WRITEDATA, f)
    c.perform()
    c.close()

    f.close()
