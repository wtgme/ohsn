# -*- coding: utf-8 -*-
"""
Created on 11:00 PM, 12/28/15

@author: tw
"""


import sys
sys.path.append('..')
import util.db_util as dbt
import pymongo
import datetime

# '''Connect db and stream collections'''
db = dbt.db_connect_no_auth('stream')
track_seed = db['user_track']
track_poi = db['poi_track']
track_poi.create_index("id", unique=True)
track_poi.create_index([('level', pymongo.ASCENDING), ('pre_level_node', pymongo.ASCENDING)], unique=False)


def trans_seed_to_poi(seed_db, poi_db):
    for user in seed_db.find({}):
        user['pre_level_node'] = None
        user['level'] = 0
        try:
            poi_db.insert(user)
        except pymongo.errors.DuplicateKeyError:
            pass


print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'Transform seed to poi'
trans_seed_to_poi(track_seed, track_poi)