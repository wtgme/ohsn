# -*- coding: utf-8 -*-
"""
Created on 13:18, 13/10/17

@author: wt

This is to study multilay network of pro-ED and pro-recovery users on discussions of different topics
"""


import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))


import ohsn.util.db_util as dbt
import ohsn.util.io_util as iot
import pymongo
import ohsn.util.graph_util as gt

def constrcut_data(filename='data/communication-only-fed-filter-hashtag-cluster.graphml'):
    ## Categorize tweets into three classes: 0: no hashtag; -1: ED tag; 1: non-ED tag.
    user_net = gt.Graph.Read_GraphML(filename)
    uids = [int(uid) for uid in user_net.vs['name']]
    print len(uids)
    edtags = set(iot.read_ed_hashtags())
    times = dbt.db_connect_col('fed', 'timeline')
    poi_time = dbt.db_connect_col('fed', 'pro_timeline')
    poi_time.create_index([('user.id', pymongo.ASCENDING),
                          ('id', pymongo.DESCENDING)])
    poi_time.create_index([('type', pymongo.ASCENDING)])
    poi_time.create_index([('id', pymongo.ASCENDING)], unique=True)

    for tweet in times.find({'user.id': {'$in': uids}}, no_cursor_timeout=True):
        hashtags = tweet['entities']['hashtags']
        tagset = set()
        for hash in hashtags:
            tag = hash['text'].encode('utf-8').lower().replace('_', '').replace('-', '')
            tagset.add(tag)
        if len(tagset) == 0:
            tweet['type'] = 0
        else:
            if len(tagset.intersection(edtags)) > 0:
                tweet['type'] = -1
            else:
                tweet['type'] = 1
        try:
            poi_time.insert(tweet)
        except pymongo.errors.DuplicateKeyError:
            pass


if __name__ == '__main__':
    constrcut_data()
