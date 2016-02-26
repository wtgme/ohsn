# -*- coding: utf-8 -*-
"""
Created on 17:32, 25/02/16

@author: wt
"""

import sys
sys.path.append('..')
import datetime
import pymongo
from api import timelines, friendshipshow
import util.db_util as dbt

print 'Job starts.......'
'''Connecting db and user collection'''

dataset = 'drd'
db = dbt.db_connect_no_auth(dataset)
sample_user = db['com']
sample_time = db['timeline']

print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "\t" + 'Connecting db well'
sample_user.create_index([('id', pymongo.ASCENDING)], unique=True)
sample_user.create_index([('timeline_scraped_times', pymongo.ASCENDING)], unique=False)
sample_time.create_index([('user.id', pymongo.ASCENDING),
                          ('id', pymongo.DESCENDING)], unique=False)
sample_time.create_index([('id', pymongo.ASCENDING)], unique=True)
user_list = []
for user in sample_user.find({},['id']):
    user_list.append(user[id])


print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "\t" + 'Start a crawl'
print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "\t" + 'Start to crawl network'
friendshipshow.generate_network(user_list, dataset)

print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "\t" + 'Start to crawl timeline'

timelines.stream_timeline(sample_user, sample_time, 1, 10000)

print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'Finish a crawl'