# -*- coding: utf-8 -*-
"""
Created on 11:59, 19/11/15
Aggregate the count of relationship of users existing in timeline
count the net collections to generate aggregated counts

Iterate all data using cursor
for user0 in poidb.find({'level': {'$lte': level}}, {'_id':0, 'id':1}):
    print user0#

NOT USING (this manner cannot iterate all data)
data = poidb.find({'level': {'$lte': level}}, {'_id':0, 'id':1})
for user0 in data:
    print user0

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
sample_network_agg.create_index([("id0", pymongo.ASCENDING),
                            ("id1", pymongo.ASCENDING),
                            ("relationship", pymongo.ASCENDING)],
                           unique=True)
track_network_agg.create_index([("id0", pymongo.ASCENDING),
                            ("id1", pymongo.ASCENDING),
                            ("relationship", pymongo.ASCENDING)],
                           unique=True)

def aggregate(poidb, netdb, aggnetdb, level):
    relationships = netdb.distinct('relationship')
    print relationships
    poidb.create_index([('timeline_count', pymongo.DESCENDING),
                        ('net_anal.aggred', pymongo.ASCENDING),
                        ('net_anal.tnmined', pymongo.ASCENDING),
                        ('level', pymongo.ASCENDING)], unique=False)

    while True:
        count = poidb.count({"timeline_count": {'$gte': 3000},
                             "net_anal.aggred": {'$exists': False},
                             'net_anal.tnmined': True,
                             'level': {'$lte': level}})
        if count == 0:
            break
        else:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") +"\t"+ str(count) + " remaining"

        # print type(relationships[0])
        for user0 in poidb.find({"timeline_count": {'$gte': 3000},
                                 "net_anal.aggred": {'$exists': False},
                                 'net_anal.tnmined': True,
                                 'level': {'$lte': level}},
                                ['id']).limit(250):
            # print type(user0)
            for user1 in netdb.distinct('id1', {'id0': user0['id']}):
                user_exist = poidb.count({'id': user1,
                                        'timeline_count':{'$gte': 3000},
                                        'net_anal.tnmined': True,
                                        'level': {'$lte': level}})
                if user_exist:
                    for relationship in relationships:
                        count = netdb.count({'id0': user0['id'], 'id1': user1, 'relationship': relationship})
                        if count > 0:
                            try:
                                aggnetdb.insert({'id0': user0['id'], 'id1': user1, 'relationship': relationship, 'count': count})
                                # aggnetdb.update({'id0': user0['id'], 'id1': user1['id'], 'relationship': relationship}, {'$set': {'count': count}}, upsert=True)
                            except Exception:
                                pass
                                # print 'duplicate insert'
                # else:
                #     print user1, 'does not satisfy'
            poidb.update({'id': user0['id']}, {'$set': {"net_anal.aggred": True}})



# def aggregate(poidb, netdb, aggnetdb, level):
#     while True:
#         count = netdb.count({"aggred_flag": {'$exists': False}})
#         if count == 0:
#             break
#         else:
#             print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") +"\t"+ str(count) + " remaining"
#         for relation in netdb.find({"aggred_flag": {'$exists': False}}).limit(250):
#             id0 = relation['id0']
#             id1 = relation['id1']
#             relationship = relation['relationship']
#             user0 = poidb.find_one({'id': id0}, {'timeline_count': 1, 'level': 1})
#             user1 = poidb.find_one({'id': id1}, {'timeline_count': 1, 'level': 1})
#
#             if user0 and user1 and (user0['level'] <= level) and (user1['level'] <= level):
#                 count = netdb.count({'id0': id0, 'id1': id1, 'relationship': relationship})
#                 if count > 0:
#                     try:
#                         aggnetdb.insert({'id0': id0, 'id1': id1, 'relationship': relationship, 'count': count})
#                     except pymongo.errors.DuplicateKeyError:
#                         # print 'duplicate insert'
#                         pass
#             netdb.update_many({'id0': id0, 'id1': id1, 'relationship': relationship}, {'$set': {"aggred_flag": True}})


# print sample_network.count({'id0': 50883209, 'id1': 45112524, 'relationship': 'mentioned'})
print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), '--------------sample--------------'
aggregate(sample_poi, sample_network, sample_network_agg, 2)
# print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), '--------------track--------------'
# aggregate(track_poi, track_network, track_network_agg, 1)

print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), '--------------finish--------------'

