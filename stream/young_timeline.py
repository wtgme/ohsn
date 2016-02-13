# -*- coding: utf-8 -*-
"""
Created on 16:19, 12/02/16

@author: wt
"""

import sys
sys.path.append('..')
import datetime
import pymongo
from api import timelines
import util.db_util as dbt

print 'Job starts.......'
'''Connecting db and user collection'''
db = dbt.db_connect_no_auth('young')
sample_user = db['com']
sample_time = db['timeline']
print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Connecting db well'
sample_user.create_index([('timeline_scraped_times', pymongo.ASCENDING)])
sample_time.create_index([('user.id', pymongo.ASCENDING),
                          ('id', pymongo.DESCENDING)])
sample_time.create_index([('id', pymongo.ASCENDING)], unique=True)



print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Connect Twitter.com'


# stream_timeline(sample_user, sample_time, 1, 2)
timelines.stream_timeline(sample_user, sample_time, 1)
print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'finish timeline for sample users'