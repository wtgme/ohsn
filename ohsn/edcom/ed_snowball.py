# -*- coding: utf-8 -*-
"""
Created on 10:20, 02/02/16

@author: wt
1. Import seed users from stream
2. Snowball friends and followers of seed users
"""

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import datetime
import pymongo
from ohsn.api import follower
from ohsn.api import following
from ohsn.api import lookup
from ohsn.api import profiles_check
from ohsn.util import db_util as dbt
import ohsn.util.io_util as iot
import math
from threading import Thread


def re_snowball_friends(olddbname, oldcomname, newdbname, newcomname):
    newdb = dbt.db_connect_no_auth(newdbname)
    newcom = newdb[newcomname]
    newnet = newdb['net2']
    newcom.create_index("id", unique=True)
    newcom.create_index([('level', pymongo.ASCENDING),
                         ('following_prelevel_node', pymongo.ASCENDING)],
                        unique=False)
    newcom.create_index([('level', pymongo.ASCENDING),
                         ('follower_prelevel_node', pymongo.ASCENDING)],
                        unique=False)
    newnet.create_index([("user", pymongo.ASCENDING),
                         ("follower", pymongo.ASCENDING)],
                        unique=True)

    '''Reteive ED core users'''
    # ed_users = iot.get_values_one_field(olddbname, oldcomname, 'id', {'level': 1})
    # list_size = len(ed_users)
    # length = int(math.ceil(list_size/100.0))
    # for index in xrange(length):
    #     index_begin = index*100
    #     index_end = min(list_size, index_begin+100)
    #     lookup.lookup_user_list(ed_users[index_begin:index_end], newcom, 1, 'N')


    '''Snowball sampling round'''
    level = 2
    while level < 3:
    #     # Each call of snowball_following and snowball_follower only process up to 200 users
        print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'Snowball followings of seeds for sample db', level
        following_flag = following.snowball_following(newcom, newnet, level, 'N')
    #     print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'Snowball followees of seeds for sample db', level
    #     follower_flag = follower.snowball_follower(newcom, newnet, level, 'N')
        if following_flag == False:
            level += 1
        continue

    # print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'START: Snowball friends of seeds for sample db', level
    # t1 = Thread(target=following.snowball_following, args=[newcom, newnet, level, 'N'])
    # t2 = Thread(target=follower.snowball_follower, args=[newcom, newnet, level, 'N'])
    # t1.start()
    # t2.start()
    # t1.join()
    # t2.join()
    # print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'FINISH: Snowball friends of seeds for sample db', level


def snowball_friends():
    db = dbt.db_connect_no_auth('ed')
    ed_poi = db['com']
    ed_net = db['net']
    # stream_users = db['poi']
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
    # while True:
    #     ed_seed = profiles_check.seed_all_profile(stream_users)
    #     if len(ed_seed)==0:
    #         print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'no seed users, finished!'
    #         break
    #     else:
    #         lookup.trans_seed_to_poi(ed_seed, ed_poi)
    #         continue
    level = 1
    while True:
        print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'Snowball followings of seeds for sample db', level
        following_flag = following.snowball_following(ed_poi, ed_net, level, 'ED')
        print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'Snowball followees of seeds for sample db', level
        follower_flag = follower.snowball_follower(ed_poi, ed_net, level, 'ED')
        if following_flag == False and follower_flag == False:
            break
        else:
            level = level + 1
            continue

if __name__ == '__main__':
    # snowball_friends()
    re_snowball_friends('random', 'com', 'random3', 'com') # random2 fed