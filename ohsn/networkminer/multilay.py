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
import ohsn.networkminer.timeline_network_miner as timiner

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

def extract_network(dbname, timename, bnetname, typename='ED'):
    # Extract different networks from different types of content
    typemap = {'ED': -1,
               'Non-ED': 1,
               'Non-tag': 0}
    type = typemap[typename]
    time = dbt.db_connect_col(dbname, timename)
    bnet = dbt.db_connect_col(dbname, bnetname)
    bnet.create_index([("id0", pymongo.ASCENDING),
                                 ("id1", pymongo.ASCENDING),
                                 ("type", pymongo.ASCENDING),
                                 ("statusid", pymongo.ASCENDING)],
                                unique=True)
    for tweet in time.find({'type': type}, no_cursor_timeout=True):
        if len(tweet['entities']['user_mentions']) < 1:
                continue
        else:
            udmention_list = []
            if ('retweeted_status' in tweet) and len(tweet['retweeted_status']['entities']['user_mentions'])>0:
                for udmention in tweet['retweeted_status']['entities']['user_mentions']:
                    udmention_list.append(udmention['id'])
            for mention in tweet['entities']['user_mentions']:
                if ('in_reply_to_user_id' in tweet) and (mention['id'] == tweet['in_reply_to_user_id']): # reply
                    timiner.add_reply_edge(bnet, tweet['user']['id'], tweet['in_reply_to_user_id'], tweet['created_at'], tweet['id'])

                elif ('retweeted_status' in tweet) and (mention['id'] == tweet['retweeted_status']['user']['id']): # Retweet
                    timiner.add_retweet_edge(bnet, tweet['user']['id'], tweet['retweeted_status']['user']['id'], tweet['created_at'], tweet['id'])

                elif mention['id'] in udmention_list:  # mentions in Retweet content
                    timiner.add_undirect_mentions_edge(bnet, tweet['user']['id'], mention['id'], tweet['created_at'], tweet['id'])

                else:  # original mentions
                    timiner.add_direct_mentions_edge(bnet, tweet['user']['id'], mention['id'], tweet['created_at'], tweet['id'])



if __name__ == '__main__':
    # constrcut_data()
    extract_network('fed', 'pro_timeline', 'ed_bnet', 'ED')
    extract_network('fed', 'pro_timeline', 'non_ed_bnet', 'Non-ED')
    extract_network('fed', 'pro_timeline', 'non_tag_bnet', 'Non-tag')