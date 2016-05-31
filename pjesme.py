#! /usr/bin/python

from pyquery import PyQuery as pq
import pycurl

FILENAME = 'list.txt'

f = open(FILENAME, 'r')
names = map(lambda x: x[:-1], f.readlines())

# doc = pq('youtube.com')
