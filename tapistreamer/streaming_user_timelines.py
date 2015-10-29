# -*- coding: utf-8 -*-
"""
Created on 20:34, 26/10/15

@author: wt
"""

import sys
sys.path.append('..')
import util.db_util as dbutil

db = dbutil.db_connect_no_auth('twitter_test')
stream_collection = db['streamtrack']
timelines_collection = db['timelines']

'''the type of tweet is dict'''
for tweet in stream_collection.find().limit(10):
    print type(tweet)
    # timelines_collection.insert(tweet)





