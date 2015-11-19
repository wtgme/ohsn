# -*- coding: utf-8 -*-
"""
Created on 11:59, 19/11/15
Aggregate the count of relationship of users existing in timeline
count the net collections to generate aggregated counts

@author: wt
"""

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
import util.db_util as dbutil
import datetime
import pymongo

#### Connecting db and collections
db = dbutil.db_connect_no_auth('stream')
sample_network = db['net_sample']
track_network = db['net_track']

sample_poi = db['poi_sample']
track_poi = db['poi_track']

sample_network_agg = db['net_sample_aggregated']
track_network_agg = db['net_track_aggregated']

def aggregate(poidb, netdb, aggnetdb):
    cursor = netdb.find({})
    i = 0
    try:
        for relation in cursor:
            id0 = relation['id0']
            id1 = relation['id1']
            relationship = relation['relationship']
            user0 = poidb.find_one({'id': id0}, {'timeline_count': 1})
            user1 = poidb.find_one({'id': id1}, {'timeline_count': 1})
            i += 1
            if i%1000 == 0:
                print 'Processed', i, 'records'
            if user1:
                # only count the relationship of users that have 3000 timeline at least
                if (id0 != id1) and (user0['timeline_count'] >= 3000) and (user1['timeline_count'] >= 3000):
                    count = aggnetdb.count({'id0': id0, 'id1': id1, 'relationship': relationship})
                    count += 1
                    aggnetdb.update({'id0': id0, 'id1': id1, 'relationship': relationship}, {'$set': {'id0': id0, 'id1': id1, 'relationship': relationship, 'count': count}}, upsert=True)
    except pymongo.errors.CursorNotFound as detail:
        print 'cursor id not valid at server', relation
        pass

aggregate(sample_poi, sample_network, sample_network_agg)
aggregate(track_poi, track_network, track_network_agg)

