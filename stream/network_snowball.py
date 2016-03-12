# -*- coding: utf-8 -*-
"""
Created on 10:20, 02/02/16

@author: wt
1. Import seed users from stream
2. Snowball friends and followers of seed users

1. Snowball with seed users to try getting network similar to ED. Users are far away, and sparser
2. Snowball (just followees) with seed users and check the largest component is big enough.
    The size of components increases suddently, since some nodes are the linker of two components
3. Snowball (followees and followers) with a single users. Loss power lower in networks
4. Snowball with seed users and check community.
5. As all sampling methods based on friends and followers cannot get desired reference data,
i.e., there is no something attractive to let users follow each other, this script is using timeline
sampling method, i.e., snowball next users based on the involved users in current user's timelines.

"""

import sys
sys.path.append('..')
from api import following, timelines, lookup, profiles_check, follower
import util.db_util as dbt
from networkminer import timeline_network_miner
import datetime
import pymongo
import math


def timeline_sampling(dbname, mode='N'):
    db = dbt.db_connect_no_auth(dbname)
    poi = db['tcom']
    timel = db['times']
    bnet = db['bnet']
    stream_users = db['poi']
    poi.create_index("id", unique=True)
    poi.create_index("level", unique=False)
    timel.create_index([('user.id', pymongo.ASCENDING),
                                  ('id', pymongo.DESCENDING)], unique=False)
    timel.create_index([('id', pymongo.ASCENDING)], unique=True)
    bnet.create_index([("id0", pymongo.ASCENDING),
                             ("id1", pymongo.ASCENDING),
                             ("relationship", pymongo.ASCENDING),
                             ("statusid", pymongo.ASCENDING)],
                            unique=True)
    # while True:
    ed_seed = profiles_check.seed_all_profile(stream_users, 5)
    length = len(ed_seed)
    if length == 0:
        print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'no seed users, finished!'
        # break
    else:
        print 'seed users: ', length
        lookup.trans_seed_to_poi(ed_seed, poi, mode)
        # continue
    level = 1
    while True:
        timelines.monitor_timeline(poi, timel, 1)
        timeline_network_miner.network_mining(poi, timel, bnet, level)
        for user in poi.find({'level': level}):
            neiblist = set()
            for relate in bnet.find({'id0': user['id'],
                                     'relationship': {'$in': ['retweet', 'reply-to', 'dmentioned']}}):
                neiblist.add(relate['id1'])
            neiblist = list(neiblist)
            list_size = len(neiblist)
            length = int(math.ceil(list_size/100.0))
            for index in xrange(length):
                index_begin = index*100
                index_end = min(list_size, index_begin+100)
                lookup.lookup_user_list(neiblist[index_begin:index_end], poi, level+1, mode)
        if poi.count() > 4000:
            break
        else:
            level += 1
            continue




def network_snowball(dbname, mode='N'):
    db = dbt.db_connect_no_auth(dbname)
    ed_poi = db['ccom']
    ed_net = db['cnet']
    stream_users = db['poi']
    # echelon = dbt.db_connect_no_auth('echelon')
    # echelon_poi = echelon['poi']

    ed_poi.create_index("id", unique=True)
    ed_poi.create_index([('level', pymongo.ASCENDING),
                         ('following_prelevel_node', pymongo.ASCENDING)],
                        unique=False)
    ed_poi.create_index([('level', pymongo.ASCENDING),
                         ('follower_prelevel_node', pymongo.ASCENDING)],
                        unique=False)
    ed_net.create_index([("user", pymongo.ASCENDING),
                        ("follower", pymongo.ASCENDING),
                         ("type", pymongo.ASCENDING)],
                                unique=True)

    while True:
        ed_seed = profiles_check.seed_all_profile(stream_users)
        length = len(ed_seed)
        if length==0:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'no seed users, finished!'
            break
        else:
            print 'seed users: ', length
            lookup.trans_seed_to_poi(ed_seed, ed_poi)
            continue

    statis = ''
    level = 1
    while level < 3:
        print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'Snowball followings of seeds for sample db', level
        following_flag = following.snowball_following(ed_poi, ed_net, level, mode)
        print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'Snowball followees of seeds for sample db', level
        follower_flag = follower.snowball_follower(ed_poi, ed_net, level, mode)
        # count = ed_poi.count()
        # try:
        #     # nsize, esize = nt.size_gaint_comp_net_db(ed_net)
        #     # s = 'Start_level: ' + str(level) + ' all_users: ' + \
        #     #           str(count) + ' size_gc:' + str(nsize) + ' ed_gc: ' + str(esize) + '\n'
        #     print s
        #     statis += s
        # except networkx.exception.NetworkXPointlessConcept:
        #     nsize = 0
        #     pass
        if (following_flag == False and follower_flag == False):
            return statis
        else:
            level += 1
            continue



# s = network_snowball('rd')
# print s
timeline_sampling('rd', 'N')
timeline_sampling('yg', 'YG')
# print s