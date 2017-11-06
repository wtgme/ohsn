# -*- coding: utf-8 -*-
"""
Created on 14:30, 17/10/17

@author: wt
"""
import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))


import ohsn.util.db_util as dbt
import ohsn.util.io_util as iot
import ohsn.util.graph_util as gt
import pymongo
import ohsn.api.profiles_check as pck
from datetime import datetime
import ohsn.textprocessor.description_miner as dm
import pandas as pd

# def filter_user():
#     # filter ED users from Ian data
#     conn = dbt.db_connect_no_auth_ian()
#     iandb = conn.connect('TwitterProAna')
#     ianusers = iandb['users']
#     for u in ianusers.find({}, no_cursor_timeout=True):
#         if 'description' in u:
#             text = u['description']
#             if text != None and pck.check_ed_profile(text):
#                 print u['id']
#         else:
#             if 'history' in u:
#                 hists = u['history']
#                 for h in hists:
#                     if 'description' in h:
#                         text = h['description']
#                         if text != None and pck.check_ed_profile(text):
#                             print u['id']
#     conn.disconnect()


def overlap():
    # overlap between two data
    core_ed = set(iot.get_values_one_field('fed', 'scom', 'id'))
    ian_ed = set()
    with open('uid.txt', 'r') as fo:
        for line in fo.readlines():
            ian_ed.add(int(line.strip()))
    print len(core_ed), len(ian_ed), len(core_ed.intersection(ian_ed))

    fed = set(iot.get_values_one_field('fed', 'com', 'id'))
    ian_all = set(iot.get_values_one_field('TwitterProAna', 'users', 'id'))
    print len(fed), len(ian_all), len(fed.intersection(ian_all))
    print len(fed), len(ian_ed), len(fed.intersection(ian_ed))


# def data_transform():
#     # transform data from ian db to local db
#     conn = dbt.db_connect_no_auth_ian()
#     iandb = conn.connect('TwitterProAna')
#     ianusers = iandb['users']
#     users = dbt.db_connect_col('TwitterProAna', 'users')
#     users.create_index([('id', pymongo.ASCENDING)], unique=True)

#     for u in ianusers.find({}, no_cursor_timeout=True):
#         try:
#             users.insert(u)
#         except pymongo.errors.DuplicateKeyError:
#             pass

#     ianusers = iandb['tweets']
#     users = dbt.db_connect_col('TwitterProAna', 'tweets')
#     users.create_index([('user.id', pymongo.ASCENDING),
#                           ('id', pymongo.DESCENDING)])
#     users.create_index([('id', pymongo.ASCENDING)], unique=True)

#     for u in ianusers.find({}, no_cursor_timeout=True):
#         try:
#             users.insert(u)
#         except pymongo.errors.DuplicateKeyError:
#             pass
#     conn.disconnect()


def tweet_stat():
    # stats tweeting activity over time
    tweets = dbt.db_connect_col('TwitterProAna', 'tweets')
    print ('%s\t%s\t%s') %('tid', 'uid', 'date')
    for tweet in tweets.find({}, no_cursor_timeout=True):
        print ('%s\t%s\t%s') %('t'+str(tweet['id']), 'u'+str(tweet['from_user_id']), tweet['created_at'])


def follow_net(dbname, collection):
    # recover follow network among users
    com = dbt.db_connect_col(dbname, collection)
    for row in com.find({'screen_name': {'$exists': True}}, no_cursor_timeout=True):
        ego = str(row['id'])
        if 'followData' in row:
            friends = row['followData']
            # if ('friends' in friends) and ('followers' in friends):
            #     print ego, len(set(friends['friends']).
            #                    intersection(set(friends['followers'])))

            if 'friends' in friends:
                for followee in friends['friends']:
                    print ego + '\t' + str(followee)
            if 'followers' in friends:
                for follower in friends['followers']:
                    print str(follower) + '\t' + ego

    # name_map, edges = {}, set()
    # with open('net.txt', 'r') as fo:
    #     for line in fo.readlines():
    #         n1, n2 = line.split('\t')
    #         n1id = name_map.get(n1, len(name_map))
    #         name_map[n1] = n1id
    #         n2id = name_map.get(n2, len(name_map))
    #         name_map[n2] = n2id
    #         edges.add((n1id, n2id))
    # g = gt.Graph(len(name_map), directed=True)
    # g.vs["name"] = list(sorted(name_map, key=name_map.get))
    # g.add_edges(list(edges))
    # g.es["weight"] = 1
    # g.write_graphml('follow.graphml')


def hashtag_net(dbname, colname):
    # built hashtag_net
    g = gt.load_hashtag_coocurrent_network_undir(dbname, colname)
    g.write_graphml('tag.graphml')


def hot_day(filename, dbname='TwitterProAna', colname='tweets'):
    df = pd.read_csv(filename, sep='\t')
    df['date']  = pd.DatetimeIndex(df.date).normalize()
    # print df
    mask = (df['date'] == '2013-03-27')
    df = df.loc[mask]
    tweets = dbt.db_connect_col(dbname, colname)
    tids = []
    for tid in df['tid']:
        tid = tid.replace('t', '')
        tids.append(int(tid))
    # print tids
    for tweet in tweets.find({'id': {'$in': tids}}):
        print str(tweet['id']), tweet['text'].encode('utf-8')


def bio_information(filename, dbname='TwitterProAna', colname='users'):
    com = dbt.db_connect_col(dbname, colname)
    for row in com.find({'screen_name': {'$exists': True}}, no_cursor_timeout=True):
        name = row['name']
        text = row['description']



if __name__ == '__main__':
    # filter_user()
    # overlap()

    # data_transform()
    # tweet_stat()
    follow_net('TwitterProAna', 'users')
    # hashtag_net('TwitterProAna', 'tweets')
    # hot_day('tweets.csv')