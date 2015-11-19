# -*- coding: utf-8 -*-
"""
Created on 15:04, 29/10/15

@author: wt

1. Extracting unique twitter users from twitter streaming data

Due to user embedded within tweets cannot always be relied upon, this file is discarded, using streaming_poi_info.py

"""
import sys
sys.path.append('..')
import util.db_util as dbt
import util.twitter_util as twt
import pymongo

'''Connect db and stream collections'''
db = dbt.db_connect_no_auth('stream')
sample = db['streamsample']
track = db['streamtrack']


'''Extracting users from stream files, add index for id to avoid duplicated users'''
sample_poi = db['poi_sample']
sample_poi.ensure_index("id", unique=True)
track_poi = db['poi_track']
track_poi.ensure_index("id", unique=True)

'''Get all documents in stream collections'''
sample_user_list = sample.find()
track_user_list = track.find()

print 'extract users from sample streams'
for doc in sample_user_list:
    try:
        sample_poi.insert(doc['user'])
    except pymongo.errors.DuplicateKeyError:
        # print 'find duplicated users'
        continue
print 'extract users from track streams'
for doc in track_user_list:
    try:
        track_poi.insert(doc['user'])
    except pymongo.errors.DuplicateKeyError:
        # print 'find duplicated users'
        continue
