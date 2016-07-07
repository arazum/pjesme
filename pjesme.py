#! /usr/bin/python

from pyquery import PyQuery as pq
import pycurl
import urllib
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
DEFAULT_ATTEMPTS = 10

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
parser.add_argument('-a', '--attempts', default=DEFAULT_ATTEMPTS, metavar='N', 
        type=int, help='''number of download attempts 
        (default: {})'''.format(DEFAULT_ATTEMPTS))
args = parser.parse_args()


def file_exists(title):
    if not args.force and os.path.isfile(OUTPUT.format(args.output, title)):
        print '{} -> exists'.format(title)
        return True
    else:
        return False

def download_song((id, name, title, c)):
    filename = OUTPUT.format(args.output, name)

    for i in range(args.attempts):
        time.sleep(args.wait)

        try:
            f = open(filename, 'w')
        except IOError as e:
            print '{} -> error while opening file: {}'.format(title, e)
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
            print '{} -> download error: {}'.format(title, e)
            return

        f = open(filename, 'r')
        ok = f.read(len(MP3_MAGIC)) == MP3_MAGIC
        f.close()

        if ok:
            c.close()

            print '{} -> {:.3f} MB'.format(title, float(size) / (1 << 20))
            return
        else:
            os.remove(filename)

            if c.getinfo(pycurl.HTTP_CODE) == 500:
                print '{} -> unable to convert (500)'.format(title)
                return

    print '{} -> exceeded download attempt limit ({})'.format(title, args.attempts)

def get_query_data(query):
    # provides: id, url, filename, title, result
    if query.startswith('#'):
        id = query[1:]

        url = WATCH_URL.format(id)
        try:
            doc = pq(url)
        except Exception as e:
            print '{} -> query error: {}'.format(query, e)
            return None

        filename = doc('#eow-title').text().encode('utf8')
        title = filename
        result = filename

        if file_exists(filename):
            return None
    else:
        filename = query
        title = query

        if file_exists(filename):
            return None

        try:
            doc = pq(QUERY_URL.format(urllib.quote(query)))
        except Exception as e:
            print '{} -> query error: {}'.format(query, e)
            return None

        object = doc('h3.yt-lockup-title > a')
        path = object.attr('href')
        result = object.html().encode('utf8')
        
        if not path:
            print '{} -> no results'.format(query)
            return None

        url = YOUTUBE_URL.format(path)
        id = urlparse.parse_qs(urlparse.urlparse(url).query)['v'][0]

    postdata = {'url': url, 'format': 1, 'service': 'youtube'}

    c = pycurl.Curl()
    c.setopt(c.URL, CONVERT_URL)
    c.setopt(c.POSTFIELDS, urllib.urlencode(postdata))
    c.setopt(c.WRITEFUNCTION, lambda x: None)
    c.setopt(c.COOKIEJAR, COOKIEJAR.format(id))

    try:
        c.perform()
    except Exception as e:
        print '{} -> request error:'.format(query, e)
        return None

    print '{} -> {} [{}]'.format(query, result, id)
    return id, filename, title, c

def perform(query):
    data = get_query_data(query)
    if data == None:
        return

    download_song(data)

if not os.path.exists(args.output):
    os.makedirs(args.output)

if not os.path.exists('tmp'):
    os.makedirs('tmp')

queries = []

for filename in args.lists:
    try:
        f = open(filename, 'r')
        queries.extend(map(lambda x: x.strip(), f.readlines()))
    except IOError as e:
        print 'Error while reading list "{}": {}'.format(filename, e)

processes = []

for query in queries:
    if __name__ == '__main__':
        p = Process(target=perform, args=(query,))
        processes.append(p)
        p.start()

for p in processes:
    p.join()
