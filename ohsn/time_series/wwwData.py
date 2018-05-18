# -*- coding: utf-8 -*-
"""
Created on 14:30, 17/10/17

@author: wt
"""
import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))


import ohsn.util.db_util as dbt
import ohsn.util.io_util as iot
import ohsn.util.graph_util as gt
import pymongo
import datetime
import pandas as pd
import re
import sys
from ohsn.lexiconsmaster.lexicons.liwc import Liwc
import pickle
from ohsn.api import timelines
from ohsn.api import lookup


def profile(dbname, comname):
    com = dbt.db_connect_col(dbname, comname)
    com.create_index([('id', pymongo.ASCENDING)], unique=True)

    idset = set()
    with open('/media/data/twitter_rv.net', 'r') as infile:
        for line in infile:
            ids = line.strip().split()
            for idstr in ids:
                idset.add(int(idstr))
            if len(idset) > 90:
                lookup.lookup_user_list(list(idset), com, 1, 'N')
                idset = set()



def timeline(dbname, comname, timename):
    # return users' timelines from a time to a time
    max_id = '4451234362' # Mon Sep 28 20:03:05 +0000 2009
    com = dbt.db_connect_col(dbname, comname)
    timeline = dbt.db_connect_col(dbname, timename)

    com.create_index([('timeline_scraped_times', pymongo.ASCENDING)])
    timeline.create_index([('user.id', pymongo.ASCENDING),
                          ('id', pymongo.DESCENDING)])
    timeline.create_index([('id', pymongo.ASCENDING)], unique=True)

    print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "\t" + 'Connect Twitter.com'
    timelines.retrieve_timeline(com, timeline, max_id, request_times=1, tweetTrim=True)
    print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'finish timeline for sample users'


if __name__ == '__main__':
    profile('www', 'com')
    # timeline('www', 'com', 'timeline')