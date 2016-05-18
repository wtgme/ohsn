# -*- coding: utf-8 -*-
"""
Created on 12:04, 18/11/15

Mining relationship network from users' timelines
Relationship:
Tweet: 0
Retweet: 1;
Reply: 2;
Direct Mention: 3;
undirect mention: 4

@author: wt
"""

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
from ohsn.util import db_util as dbutil
import datetime
import pymongo


def add_tweet_edge(netdb, userid, createdat, statusid):
    edge = {}
    edge['id0'] = userid
    # edge['screen_name_0'] =
    edge['id1'] = userid
    # edge['screen_name_1'] =
    edge['type'] = 0
    # edge['relationship'] = 'friend'
    # this is an observation we can merge observations into weighted and time period later.
    edge['created_at'] = createdat
    # edge['first-date'] = createdat
    edge['statusid'] = statusid

    #print 'tweet\t' + str(userid) +"\t"+ str(createdat) +"\t"+ str(statusid)

    try:
        netdb.insert(edge)
    except pymongo.errors.DuplicateKeyError:
        pass
        #print "forming tweet edge Duplicate Key ERROR! this shouldn't happen..."
        #print 'tweet\t' + str(userid) +"\t"+ str(createdat) +"\t"+ str(statusid)


def add_retweet_edge(netdb, userid, retweeted, createdat, statusid):
    edge = {}
    edge['id0'] = userid
    # edge['screen_name_0'] =
    edge['id1'] = retweeted
    # edge['screen_name_1'] =
    edge['type'] = 1
    # edge['relationship'] = 'friend'
    # this is an observation we can merge observations into weighted and time period later.
    edge['created_at'] = createdat
    # edge['first-date'] = createdat
    edge['statusid'] = statusid
    #print 'retweet\t' + str(userid) +"\t"+ str(retweeted) +"\t"+ str(createdat) +"\t"+ str(statusid)

    try:
        netdb.insert(edge)
    except pymongo.errors.DuplicateKeyError:
        pass
        #print "forming retweet edge Duplicate Key ERROR! this shouldn't happen..."
        #print 'retweet\t' + str(userid) +"\t"+ str(retweeted) +"\t"+ str(createdat) +"\t"+ str(statusid)
        #exit()


def add_reply_edge(netdb, userid, replied_to, createdat, statusid):
    edge = {}
    edge['id0'] = userid
    # edge['screen_name_0'] =
    edge['id1'] = replied_to
    # edge['screen_name_1'] =
    edge['type'] = 2
    # edge['relationship'] = 'friend'
    # this is an observation we can merge observations into weighted and time period later.
    edge['created_at'] = createdat
    # edge['first-date'] = createdat
    edge['statusid'] = statusid

    #print 'reply-to\t' + str(userid) +"\t"+ str(replied_to) +"\t"+ str(createdat) +"\t"+ str(statusid)

    try:
        netdb.insert(edge)
    except pymongo.errors.DuplicateKeyError:
        pass
        #print "forming reply edge Duplicate Key ERROR! this shouldn't happen..."
        #print 'reply-to\t' + str(userid) +"\t"+ str(replied_to) +"\t"+ str(createdat) +"\t"+ str(statusid)

def add_direct_mentions_edge(netdb, userid, mentioned, createdat, statusid):
    edge = {}
    edge['id0'] = userid
    # edge['screen_name_0'] =
    edge['id1'] = mentioned
    # edge['screen_name_1'] =
    edge['type'] = 3
    # edge['relationship'] = 'friend'
    # this is an observation we can merge observations into weighted and time period later.
    edge['created_at'] = createdat
    # edge['first-date'] = createdat
    edge['statusid'] = statusid

    #print 'mentions\t' + str(userid) +"\t"+ str(mentioned) +"\t"+ str(createdat) +"\t"+ str(statusid)

    try:
        netdb.insert(edge)
    except pymongo.errors.DuplicateKeyError:
        pass
        #print "forming mentions edge Duplicate Key ERROR! this shouldn't happen..."
        #print 'mentions\t' + str(userid) +"\t"+ str(mentioned) +"\t"+ str(createdat) +"\t"+ str(statusid)


def add_undirect_mentions_edge(netdb, userid, mentioned, createdat, statusid):
    edge = {}
    edge['id0'] = userid
    # edge['screen_name_0'] =
    edge['id1'] = mentioned
    # edge['screen_name_1'] =
    edge['type'] = 4
    # edge['relationship'] = 'friend'
    # this is an observation we can merge observations into weighted and time period later.
    edge['created_at'] = createdat
    # edge['first-date'] = createdat
    edge['statusid'] = statusid

    #print 'mentions\t' + str(userid) +"\t"+ str(mentioned) +"\t"+ str(createdat) +"\t"+ str(statusid)

    try:
        netdb.insert(edge)
    except pymongo.errors.DuplicateKeyError:
        pass
        #print "forming mentions edge Duplicate Key ERROR! this shouldn't happen..."
        #print 'mentions\t' + str(userid) +"\t"+ str(mentioned) +"\t"+ str(createdat) +"\t"+ str(statusid)


def network_mining(poi, timelines, network, level):
    # TODO: change net_anal.tnmined as int not bool for multiple processing
    #### Start to mining relationship network from users' timelines
    while True:
        count = poi.count({'$or': [{'net_anal.tnmined': {'$exists': False}},
                                            {'net_anal.tnmined': False}]})
        # count = poi.count({"timeline_count": {'$gt': 0}, '$or': [{'net_anal.tnmined': {'$exists': False}},
        #                                      {'net_anal.tnmined': False}], 'level': {'$lte': level}})
        if count == 0:
            break
        else:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") +"\t"+ str(count) + " remaining"

        # for user in poi.find({"timeline_count": {'$gt': 0}, '$or': [{'net_anal.tnmined': {'$exists': False}},
        #                                      {'net_anal.tnmined': False}], 'level': {'$lte': level}}, {'id': 1}).limit(250):
        for user in poi.find({'$or': [{'net_anal.tnmined': {'$exists': False}},
                                            {'net_anal.tnmined': False}]}).limit(250):
            for tweet in timelines.find({'user.id': user['id']}):
                # parse the tweet for mrr edges:

                #tweet['text']= tweet['text'].encode('utf-8','ignore')
                #tweet['text'] = tweet['text'].replace('\n', ' ')
                #print tweet['text']
                # if it doesn't mention or retweet or reply...
                if len(tweet['entities']['user_mentions']) < 1:
                    # add_tweet_edge(network, tweet['user']['id'], tweet['created_at'], tweet['id'])
                    continue
                else:
                    udmention_list = []
                    if ('retweeted_status' in tweet) and len(tweet['retweeted_status']['entities']['user_mentions'])>0:
                        for udmention in tweet['retweeted_status']['entities']['user_mentions']:
                            udmention_list.append(udmention['id'])
                    for mention in tweet['entities']['user_mentions']:
                        if ('in_reply_to_user_id' in tweet) and (mention['id'] == tweet['in_reply_to_user_id']): # reply
                            add_reply_edge(network, tweet['user']['id'], tweet['in_reply_to_user_id'], tweet['created_at'], tweet['id'])

                        elif ('retweeted_status' in tweet) and (mention['id'] == tweet['retweeted_status']['user']['id']): # Retweet
                            add_retweet_edge(network, tweet['user']['id'], tweet['retweeted_status']['user']['id'], tweet['created_at'], tweet['id'])

                        elif mention['id'] in udmention_list:  # mentions in Retweet content
                            add_undirect_mentions_edge(network, tweet['user']['id'], mention['id'], tweet['created_at'], tweet['id'])

                        else:  # original mentions
                            add_direct_mentions_edge(network, tweet['user']['id'], mention['id'], tweet['created_at'], tweet['id'])
            poi.update({'id': user['id']}, {'$set': {"net_anal.tnmined": True}}, upsert=False)



def process_db(dbname, poicol, timecol, bnetcol, level):
    #### Connecting db and collections
    db = dbutil.db_connect_no_auth(dbname)
    sample_poi = db[poicol]
    print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "\t" + 'Connecting POI dbs well'

    sample_time = db[timecol]
    print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "\t" + 'Connecting timeline dbs well'

    sample_network = db[bnetcol]
    sample_network.create_index([("id0", pymongo.ASCENDING),
                                 ("id1", pymongo.ASCENDING),
                                 ("type", pymongo.ASCENDING),
                                 ("statusid", pymongo.ASCENDING)],
                                unique=True)
    # sample_poi.create_index([('timeline_count', pymongo.DESCENDING),
    #                   ('net_anal.tnmined', pymongo.ASCENDING),
    #                   ('level', pymongo.ASCENDING)], unique=False)
    # set every poi to have not been analysed.
    sample_poi.update_many({"net_anal.tnmined": True}, {'$set': {"net_anal.tnmined": False}}, upsert=False)
    print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "\t" + 'Connecting network dbs well'
    # sample_network.delete_many({'relationship': 'tweet'})

    network_mining(sample_poi, sample_time, sample_network, level)

if __name__ == '__main__':
    # process_db('fed', 'com', 'timeline', 'bnet', 10000)
    process_db('echelon', 'poi', 'timelines', 'bnet', 10000)
    # process_db('sed', 'com', 'timeline', 'bnet', 10)
    # process_db('srd', 'com', 'timeline', 'bnet', 10)
    # process_db('syg', 'com', 'timeline', 'bnet', 10)