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
        print ('%d\t%d\t%s') %(tweet['id'], tweet['from_user_id'], tweet['created_at'])


def follow_net():
    # recover follow network among users
    g = gt.load_network_ian('TwitterProAna', 'users')
    g.write_graphml('follow.graphml')


if __name__ == '__main__':
    # filter_user()
    overlap()

    # data_transform()
    # tweet_stat()
    # follow_net()