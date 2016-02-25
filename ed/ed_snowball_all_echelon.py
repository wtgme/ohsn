# -*- coding: utf-8 -*-
"""
Created on 10:20, 02/02/16

@author: wt
1. Import seed users from stream
2. Snowball friends and followers of seed users
"""

from api import follower, following, profiles_check
import util.db_util as dbt
import datetime
import time
import pymongo


db = dbt.db_connect_no_auth('ed')

ed_poi = db['poi_ed_all']
ed_net = db['net_ed_all']
# stream_users = db['stream-users']
echelon = dbt.db_connect_no_auth('echelon')
echelon_poi = echelon['poi']

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
    try:
        ed_seed = profiles_check.seed_all_profile(echelon_poi)
        # print ed_seed
        following.trans_seed_to_poi(ed_seed, ed_poi)
        level = 1
        while True:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'Snowball followings of seeds for sample db', level
            following_flag = following.snowball_following(ed_poi, ed_net, level, 'ED')
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'Snowball followees of seeds for sample db', level
            follower_flag = follower.snowball_follower(ed_poi, ed_net, level, 'ED')
            if following_flag==False and follower_flag==False:
                break
            else:
                level += 1
                continue
        if level == 1:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'No new seed users, sleep 15 mins'
            time.sleep(15*60)
        continue
    except Exception as details:
        print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'exception stop, re-run'
        continue
