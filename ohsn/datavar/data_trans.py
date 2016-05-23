# -*- coding: utf-8 -*-
"""
Created on 9:18 PM, 2/25/16
finanlize data of ED, RD, YG for dynamic monitor

@author: tw
"""

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
import pymongo
from ohsn.util import db_util as dbt


def transform():
    db = dbt.db_connect_no_auth('rd')
    cols = db['com']
    db = dbt.db_connect_no_auth('drd')
    cold = db['com']
    cold.create_index([('id', pymongo.ASCENDING)], unique=True)
    for user in cols.find({'level': 3}, ['id', 'screen_name',
                               "description", "friends_count",
                               "followers_count", "statuses_count"]):
        cold.insert({'id': user['id'],
                     'screen_name':user['screen_name'],
                     'description': user['description'],
                     'friends_count': user['friends_count'],
                     'followers_count': user['followers_count'],
                     'statuses_count': user['statuses_count']})


def select_sub(dbname, colname, newcolname, timename, newtimename):
    db = dbt.db_connect_no_auth(dbname)
    com = db[colname]
    newcom = db[newcolname]
    newcom.create_index("id", unique=True)
    newcom.create_index([('level', pymongo.ASCENDING)],
                        unique=False)

    timeline = db[timename]
    newtimeline = db[newtimename]
    newtimeline.create_index([('user.id', pymongo.ASCENDING),
                              ('id', pymongo.DESCENDING)])
    newtimeline.create_index([('id', pymongo.ASCENDING)], unique=True)

    for user in com.find({'level': 1}, no_cursor_timeout=True):
        try:
            newcom.insert(user)
        except pymongo.errors.DuplicateKeyError:
            pass
        for tw in timeline.find({'user.id': user['id']}, no_cursor_timeout=True):
            try:
                newtimeline.insert(tw)
            except pymongo.errors.DuplicateKeyError:
                pass


def select_sub_poi(dbname, colname, newcolname, filter):
    db = dbt.db_connect_no_auth(dbname)
    com = db[colname]
    newcom = db[newcolname]
    newcom.create_index("id", unique=True)

    for user in com.find(filter, no_cursor_timeout=True):
        try:
            newcom.insert(user)
        except pymongo.errors.DuplicateKeyError:
            pass


def get_users(dbname, colname, filter):
    user_set = set()
    db = dbt.db_connect_no_auth(dbname)
    cols = db[colname]
    for user in cols.find(filter, ['id']):
        user_set.add(user['id'])
    return user_set


def test_common():
    filter = {'timeline_count': {'$exists': True}}
    eds, rds, ygs = get_users('fed', 'scom', filter), \
                    get_users('random', 'com', filter), \
                    get_users('young', 'com', filter)
    print len(eds), len(rds), len(ygs)
    # rds, ygs = get_users('rd'), get_users('yg')
    print eds.intersection(rds)
    print eds.intersection(ygs)
    print ygs.intersection(rds)


def test_timline():
    db = dbt.db_connect_no_auth('rd')
    cols = db['com']
    for user in cols.find({'timeline_count': {'$lt': 3200}}, ['id', 'timeline_count', 'statuses_count']):
        # print user
        if (user['statuses_count']-user['timeline_count']) > 100:
            print user['id']
            cols.update({'id': user['id']}, {'$set': {"timeline_count": 0,
                        'timeline_scraped_times': 0}}, upsert=False)


def select_non_common_user():
    eds = get_users('ded')
    rds = get_users('drd')
    db = dbt.db_connect_no_auth('yg')
    cols = db['com']
    db = dbt.db_connect_no_auth('dyg')
    cold = db['com']
    size = len(eds)-cold.count()
    for user in cols.find({'level': 3}, ['id', 'screen_name',
                               "description", "friends_count",
                               "followers_count", "statuses_count"]):
        if user['id'] not in eds and size > 0 and user['id'] not in rds:
            cold.insert({'id': user['id'],
                         'screen_name':user['screen_name'],
                         'description': user['description'],
                         'friends_count': user['friends_count'],
                         'followers_count': user['followers_count'],
                         'statuses_count': user['statuses_count']})
            size -= 1
        else:
            break


def remove_common_user(userset, dbname, comname, timename, netname):
    db = dbt.db_connect_no_auth(dbname)
    com = db[comname]
    timeline = db[timename]
    net = db[netname]
    for user in userset:
        com.delete_one({'id': user})
        timeline.delete_many({'user.id': user})
        net.delete_many({'user': user})
        net.delete_many({'follower': user})


def remove_non_targeted_user():
    sets = get_users('dyg')
    db = dbt.db_connect_no_auth('yg')
    poidb = db['com']
    netdb = db['net']
    for user in poidb.find({}, ['id']):
        if user['id'] not in sets:
            poidb.delete_one({'id': user['id']})
            netdb.delete_many({'user': user['id']})
            netdb.delete_many({'follower': user['id']})

if __name__ == '__main__':
    # test_common()
    '''Random and Young have common users'''
    # common_user = set([131440683, 845244367, 954124423, 923196810, 60784269, 1444610702, 2724721424L, 716641426, 70689475, 474063127, 1527039008, 2299584033L, 2570478117L, 924127014, 2817935658L, 65084587, 17810992, 415304375, 3197798516L, 4170340703L, 627783996, 415556669, 461747789, 631594784, 335713091, 1685873604, 163995592, 4888509389L, 1257645007, 915137490, 1053231187, 1205510869, 330611545, 485170011, 2889291231L, 401563492, 2661407845L, 95307879, 1144191595, 361493650, 41803502, 96648433, 2828410228L, 223145087])
    # remove_common_user(common_user, 'random', 'com', 'timeline', 'net')
    # remove_common_user(common_user, 'young', 'com', 'timeline', 'net')
    # test_common()

    # db = dbt.db_connect_no_auth('fed')
    # cols = db['com']
    # for user in cols.find({'level': {'$lte': 1}}, ['id', 'screen_name']):
    #     print user['screen_name']

    select_sub_poi('random', 'com', 'scom', {'timeline_count': {'$exists': True}})
    select_sub_poi('young', 'com', 'scom', {'timeline_count': {'$exists': True}})

    # select_sub('fed', 'com', 'scom', 'timeline', 'stimeline')



