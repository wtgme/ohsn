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
import ohsn.util.io_util as iot


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


def add_retweet_edge(netdb, userid, retweeted, createdat, statusid, part=None):
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
    if part:
        edge['tags'] = part

    try:
        netdb.insert(edge)
    except pymongo.errors.DuplicateKeyError:
        pass
        #print "forming retweet edge Duplicate Key ERROR! this shouldn't happen..."
        #print 'retweet\t' + str(userid) +"\t"+ str(retweeted) +"\t"+ str(createdat) +"\t"+ str(statusid)
        #exit()


def add_reply_edge(netdb, userid, replied_to, createdat, statusid, part=None):
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
    if part:
        edge['tags'] = part

    #print 'reply-to\t' + str(userid) +"\t"+ str(replied_to) +"\t"+ str(createdat) +"\t"+ str(statusid)

    try:
        netdb.insert(edge)
    except pymongo.errors.DuplicateKeyError:
        pass
        #print "forming reply edge Duplicate Key ERROR! this shouldn't happen..."
        #print 'reply-to\t' + str(userid) +"\t"+ str(replied_to) +"\t"+ str(createdat) +"\t"+ str(statusid)


def add_direct_mentions_edge(netdb, userid, mentioned, createdat, statusid, part=None):
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
    if part:
        edge['tags'] = part

    try:
        netdb.insert(edge)
    except pymongo.errors.DuplicateKeyError:
        pass
        #print "forming mentions edge Duplicate Key ERROR! this shouldn't happen..."
        #print 'mentions\t' + str(userid) +"\t"+ str(mentioned) +"\t"+ str(createdat) +"\t"+ str(statusid)


def add_undirect_mentions_edge(netdb, userid, mentioned, createdat, statusid, part=None):
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
    if part:
        edge['tags'] = part

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
        count = poi.find_one({'net_anal.tnmined': {'$exists': False}})
        # count = poi.count({"timeline_count": {'$gt': 0}, '$or': [{'net_anal.tnmined': {'$exists': False}},
        #                                      {'net_anal.tnmined': False}], 'level': {'$lte': level}})
        if count is None:
            break
        # else:
        #     print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") +"\t"+ str(count) + " remaining"

        # for user in poi.find({"timeline_count": {'$gt': 0}, '$or': [{'net_anal.tnmined': {'$exists': False}},
        #                                      {'net_anal.tnmined': False}], 'level': {'$lte': level}}, {'id': 1}).limit(250):
        for user in poi.find({'net_anal.tnmined': {'$exists': False}}).limit(250):
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


def process_tweets(timelines, network):
    for tweet in timelines.find(no_cursor_timeout=True):
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

def hashtag_related_networks(dbname, timename, netname):
    '''
    Extract users' behavior network for tweets that are related to hashtags of interests
    :param dbname:
    :param timename:
    :param netname:
    :return:
    '''
    hashtags = iot.read_recovery_ed_keywords()
    timeline = dbutil.db_connect_col(dbname, timename)
    network = dbutil.db_connect_col(dbname, netname)
    network.create_index([("id0", pymongo.ASCENDING),
                         ("id1", pymongo.ASCENDING),
                         ("type", pymongo.ASCENDING),
                         ("statusid", pymongo.ASCENDING)],
                        unique=True)
    filter = {}
    filter['$and'] = [{'$where': 'this.entities.hashtags.length>0'}, {'$where': 'this.entities.user_mentions.length>0'}]

    for tweet in timeline.find(filter, no_cursor_timeout=True):
        tags = tweet['entities']['hashtags']
        hash_tag_flag = False
        part = set([])
        for tag in tags:
            tagv = tag['text'].encode('utf-8').lower().replace('_', '').replace('-', '')
            part.add(tagv)
            # if tagv in hashtags:
            hash_tag_flag = True
        if hash_tag_flag:
            # print tweet['text']
            udmention_list = []
            if ('retweeted_status' in tweet) and len(tweet['retweeted_status']['entities']['user_mentions'])>0:
                for udmention in tweet['retweeted_status']['entities']['user_mentions']:
                    udmention_list.append(udmention['id'])
            for mention in tweet['entities']['user_mentions']:
                if ('in_reply_to_user_id' in tweet) and (mention['id'] == tweet['in_reply_to_user_id']): # reply
                    add_reply_edge(network, tweet['user']['id'], tweet['in_reply_to_user_id'], tweet['created_at'], tweet['id'], list(part))

                elif ('retweeted_status' in tweet) and (mention['id'] == tweet['retweeted_status']['user']['id']): # Retweet
                    add_retweet_edge(network, tweet['user']['id'], tweet['retweeted_status']['user']['id'], tweet['created_at'], tweet['id'], list(part))

                elif mention['id'] in udmention_list:  # mentions in Retweet content
                    add_undirect_mentions_edge(network, tweet['user']['id'], mention['id'], tweet['created_at'], tweet['id'], list(part))

                else:  # original mentions
                    add_direct_mentions_edge(network, tweet['user']['id'], mention['id'], tweet['created_at'], tweet['id'], list(part))


def refine_recovery(dbname, netname):
    '''
    refine the users who have use hashtag #recovery
    :param dbname:
    :param netname:
    :return:
    '''
    network = dbutil.db_connect_col(dbname, netname)
    proed = set(['proed', 'proana', 'promia', 'proanorexia', 'proanamia', 'proanatips', 'proanatip'])
    proedrel = proed
    for link in network.find(no_cursor_timeout=True):
        tags = set(link['tags'])
        if len(proed.intersection(tags)) > 0:
            proedrel = proedrel.union(tags)
    print len(proedrel)
    users = iot.get_values_one_field(dbname, netname, 'id0')
    print len(users)
    for user in users:
        # print user
        utags = set()
        for link in network.find({'id0': user}):
            utags.add(tag for tag in link['tags'])
        if len(utags.intersection(proedrel)) == 0:
            network.delete_many({'id0': user})






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
    process_db('depression', 'neg_com', 'neg_timeline', 'neg_bnet', 10000)
    # process_db('fed2', 'com', 'timeline', 'bnet', 10000)
    # process_db('random', 'scom', 'timeline', 'bnet', 10000)
    # process_db('young', 'scom', 'timeline', 'bnet', 10000)
    # process_db('sed', 'com', 'timeline', 'bnet', 10)
    # process_db('srd', 'com', 'timeline', 'bnet', 10)
    # process_db('syg', 'com', 'timeline', 'bnet', 10)

    # times = dbutil.db_connect_col('fed', 'ed_tag')
    # # times = dbutil.db_connect_col('fed', 'prorec_tag')
    # nets = dbutil.db_connect_col('fed', 'bnet_ed_tag')
    # nets.create_index([("id0", pymongo.ASCENDING),
    #                              ("id1", pymongo.ASCENDING),
    #                              ("type", pymongo.ASCENDING),
    #                              ("statusid", pymongo.ASCENDING)],
    #                             unique=True)
    # process_tweets(times, nets)

    # hashtag_related_networks('fed', 'timeline', 'hbnet')
    # refine_recovery('fed', 'hbnet')