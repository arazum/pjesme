#! /usr/bin/python

from pyquery import PyQuery as pq
import pycurl
from urllib import urlencode
from io import BytesIO
import time


LIST_FILE = 'list.txt'
COOKIEJAR = 'tmp/{}.cookie'
OUTPUT = 'songs/{}.mp3'

TIME_WAIT = 60

QUERY_URL = 'http://www.youtube.com/results?search_query={}'
SELECTOR = 'h3.yt-lockup-title > a'
YOUTUBE_URL = 'http://www.youtube.com{}'
CONVERT_URL = 'http://www.flv2mp3.org/convert/'
DOWNLOAD_URL = 'http://www.flv2mp3.org/download/direct/mp3/yt_{}/'


f = open(LIST_FILE, 'r')
names = map(lambda x: x[:-1], f.readlines())

print 'Requesting conversion...'

data = {}

for name in names:
    doc = pq(QUERY_URL.format(name))
    object = doc(SELECTOR)
    path = object.attr('href')
    title = object.html()

    url = YOUTUBE_URL .format(path)
    postdata = {'url': url, 'format': 1, 'service': 'youtube'}
    id = path[9:]

    c = pycurl.Curl()
    c.setopt(c.URL, CONVERT_URL)
    c.setopt(c.POSTFIELDS, urlencode(postdata))
    c.setopt(c.WRITEFUNCTION, lambda x: None)
    c.setopt(c.COOKIEJAR, COOKIEJAR.format(id))
    c.perform()

    print '{}: {} [{}]'.format(name, title.encode('utf8'), id)

    data[name] = id, c

print '\nDone. Waiting {} second(s)...'.format(TIME_WAIT)
time.sleep(TIME_WAIT)

print 'Downloading...'

for name, (id, c) in data.iteritems():
    f = open(OUTPUT.format(name), 'w')

    c.reset()
    c.setopt(c.URL, DOWNLOAD_URL.format(id))
    c.setopt(c.FOLLOWLOCATION, True)
    c.setopt(c.WRITEDATA, f)
    c.setopt(c.COOKIEJAR, COOKIEJAR.format(id))
    c.perform()
    c.close()

    print '{}: {:.3f} MB'.format(name, float(f.tell()) / (1 << 20))
    f.close()

print 'Done.'
