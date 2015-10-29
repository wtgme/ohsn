# -*- coding: utf-8 -*-
"""
Created on 20:34, 26/10/15

@author: wt

1. Get the timelines of users in POI

"""

import sys
sys.path.append('..')
import util.db_util as dbutil
import random
import util.twitter_util as twutil

'''Connecting db and user collection'''
db = dbutil.db_connect_no_auth('stream')
sample_user = db['poi_sample']
track_user = db['poi_track']

sample_time = db['timeline_sample']
track_time = db['timeline_track']

'''Sample 5000 users from user collections'''
sample_count = sample_user.count()
track_count = track_user.count()
sample_sample_ids = random.sample(range(sample_count), 5000)
track_sample_ids = random.sample(range(track_count), 5000)

def store_timeline(id_list, user_collection, timeline_collection):
    for rand_id in id_list:
        twitter_user = user_collection.find()[rand_id]




        timeline_collection.insert()








