#! /usr/bin/python

from pyquery import PyQuery as pq
import pycurl
from urllib import urlencode
from io import BytesIO
import time
import os
import sys
import urlparse
from multiprocessing import Process
import argparse

DEFAULT_LIST = 'list.txt'
COOKIEJAR = 'tmp/{}.cookie'
DEFAULT_OUTPUT_DIR = 'songs'
OUTPUT = '{}/{}.mp3'

DEFAULT_WAIT = 10 

YOUTUBE_URL = 'http://www.youtube.com{}'
QUERY_URL = YOUTUBE_URL.format('/results?search_query={}')
WATCH_URL = YOUTUBE_URL.format('/watch?v={}')
CONVERT_URL = 'http://www.flv2mp3.org/convert/'
DOWNLOAD_URL = 'http://www.flv2mp3.org/download/direct/mp3/yt_{}/'

MP3_MAGIC = 'ID3'

parser = argparse.ArgumentParser(
        description='Download songs from Youtube and convert them to mp3.')
parser.add_argument('lists', metavar='LIST_FILE', nargs='*', 
        default=[DEFAULT_LIST], help='''file containing song names 
        (default: {})'''.format(DEFAULT_LIST))
parser.add_argument('-f', '--force', action='store_true', 
        help='ignore if the song is already downloaded')
parser.add_argument('-o', '--output', default=DEFAULT_OUTPUT_DIR, metavar='DIR',
        help='''directory where to store downloaded songs 
        (default: {})'''.format(DEFAULT_OUTPUT_DIR))
parser.add_argument('-w', '--wait', default=DEFAULT_WAIT, metavar='SECS', 
        type=int, help='''wait between download attempts 
        (default: {})'''.format(DEFAULT_WAIT))
args = parser.parse_args()

def download_song(name, id, c):
    filename = OUTPUT.format(args.output, name)

    while True:
        time.sleep(args.wait)

        try:
            f = open(filename, 'w')
        except IOError as e:
            print '{} -> error while opening file: {}'.format(name, e)
            return

        c.reset()
        c.setopt(c.URL, DOWNLOAD_URL.format(id))
        c.setopt(c.FOLLOWLOCATION, True)
        c.setopt(c.WRITEDATA, f)
        c.setopt(c.COOKIEJAR, COOKIEJAR.format(id))

        try:
            c.perform()

            size = f.tell()
            f.close()
        except Exception as e:
            print '{} -> download error: {}'.format(name, e)
            return

        f = open(filename, 'r')
        ok = f.read(len(MP3_MAGIC)) == MP3_MAGIC
        f.close()

        if ok:
            c.close()

            print '{} -> {:.3f} MB'.format(name, float(size) / (1 << 20))
            return
        else:
            os.remove(filename)

            if c.getinfo(pycurl.HTTP_CODE) == 500:
                print '{} -> unable to convert (500)'.format(name)
                return

if not os.path.exists(args.output):
    os.makedirs(args.output)

if not os.path.exists('tmp'):
    os.makedirs('tmp')

names = []

for filename in args.lists:
    try:
        f = open(filename, 'r')
        names.extend(map(lambda x: x.strip(), f.readlines()))
    except IOError as e:
        print 'Error while reading list "{}": {}'.format(filename, e)

print 'Requesting conversion...'

data = {}

for name in names:
    if name.startswith('#'):
        filename = name[1:]
        direct = True
    else:
        filename = name
        direct = False

    if not args.force and os.path.isfile(OUTPUT.format(args.output, filename)):
        print '{} -> exists'.format(name)
        continue

    if direct:
        id = name[1:]
        title = id
        url = WATCH_URL.format(id)
    else:
        try:
            doc = pq(QUERY_URL.format(name))
        except Exception as e:
            print '{} -> query error: {}'.format(name, e)
            continue

        object = doc('h3.yt-lockup-title > a')
        path = object.attr('href')
        title = object.html()
        
        if not path:
            print '{} -> no results'.format(name)
            continue

        url = YOUTUBE_URL.format(path)
        id = urlparse.parse_qs(urlparse.urlparse(url).query)['v'][0]

    postdata = {'url': url, 'format': 1, 'service': 'youtube'}

    c = pycurl.Curl()
    c.setopt(c.URL, CONVERT_URL)
    c.setopt(c.POSTFIELDS, urlencode(postdata))
    c.setopt(c.WRITEFUNCTION, lambda x: None)
    c.setopt(c.COOKIEJAR, COOKIEJAR.format(id))

    try:
        c.perform()
    except Exception as e:
        print '{} -> request error:'.format(name, e)
        continue

    print '{} -> {} [{}]'.format(name, title.encode('utf8'), id)
    data[filename] = id, c

if len(data) == 0:
    print '\nNothing to download.'
    exit()

print 'Downloading...'

processes = []

for name, (id, c) in data.iteritems():
    if __name__ == '__main__':
        p = Process(target=download_song, args=(name, id, c))
        processes.append(p)
        p.start()

for p in processes:
    p.join()

print 'Done.'
