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


db = dbt.db_connect_no_auth('yg')

ed_poi = db['com']
ed_net = db['net']
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


# ed_seed = ['taylorswift13', 'ArianaGrande', 'Meghan_Trainor', 'selenagomez']
# following.trans_seed_to_poi(ed_seed, ed_poi)

# ed_seed = profiles_check.seed_all_profile(stream_users)
# following.trans_seed_to_poi(ed_seed, ed_poi)

while True:
    ed_seed = profiles_check.seed_all_profile(stream_users)
    length = len(ed_seed)
    if length==0:
        print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'no seed users, finished!'
        break
    else:
        print 'seed users: ', length
        following.trans_seed_to_poi(ed_seed, ed_poi)
        continue

level = 1
while True:
    print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'Snowball followings of seeds for sample db', level
    following_flag = following.snowball_following(ed_poi, ed_net, level, 'YG')
    print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'Snowball followees of seeds for sample db', level
    follower_flag = follower.snowball_follower(ed_poi, ed_net, level, 'YG')
    count = ed_poi.count()
    if (following_flag == False and follower_flag == False) or count>3393:
        break
    else:
        level += 1
        continue
