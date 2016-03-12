# -*- coding: utf-8 -*-
"""
Created on 17:54, 06/12/15

@author: wt
"""

# import sys
# from os import path
# sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
import sys
sys.path.append('..')
import util.db_util as dbutil
import datetime
import pymongo

#### Connecting db and collections
db = dbutil.db_connect_no_auth('stream')
sample_poi = db['poi_track']
sample_network = db['net_track']
print 'successfully connected'

for relation in sample_network.find({'relationship': 'mentioned'}, {'_id':0, 'id0':1, 'id1':1, 'relationship':1}):
    user0_id = relation['id0']
    user1_id = relation['id1']
    user0_level = sample_poi.find_one({'id': user0_id}, {'_id':0, 'timeline_count':1, 'level':1})
    user1_level = sample_poi.find_one({'id': user1_id}, {'_id':0, 'timeline_count':1, 'level':1})
    print relation , user0_level,  user1_level


