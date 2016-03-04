# -*- coding: utf-8 -*-
"""
Created on 10:20, 02/02/16

@author: wt
1. Import seed users from stream
2. Snowball friends and followers of seed users
"""

import sys
sys.path.append('..')
from api import following, lookup, profiles_check, follower
import util.db_util as dbt
import util.net_util as nt
import datetime
import pymongo
import networkx


def network_snowball(dbname, mode='N'):
    db = dbt.db_connect_no_auth(dbname)
    ed_poi = db['scom']
    ed_net = db['snet']
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
        ed_seed = profiles_check.seed_all_profile(stream_users)[1:2]
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
    while True:
        print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'Snowball followings of seeds for sample db', level
        following_flag = following.snowball_following(ed_poi, ed_net, level, mode)
        print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'Snowball followees of seeds for sample db', level
        follower_flag = follower.snowball_follower(ed_poi, ed_net, level, mode)
        count = ed_poi.count()
        try:
            nsize, esize = nt.size_gaint_comp_net_db(ed_net)
            s = 'Start_level: ' + str(level) + ' all_users: ' + \
                      str(count) + ' size_gc:' + str(nsize) + ' ed_gc: ' + str(esize) + '\n'
            print s
            statis += s
        except networkx.exception.NetworkXPointlessConcept:
            nsize = 0
            pass
        if (following_flag == False and follower_flag == False) or nsize>4000:
            return statis
        else:
            level += 1
            continue


# s = network_snowball('rd', 'RD')
# print s
s = network_snowball('yg', 'YG')
print s