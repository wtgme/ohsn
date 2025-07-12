# -*- coding: utf-8 -*-
"""
Created on 20:00, 29/09/16

@author: wt
Trim user objective in tweets
"""

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

from ohsn.util import db_util as dbt
import ohsn.util.io_util as iot
import pymongo
from bson.objectid import ObjectId

def trim_user(dbname, timename):
    db = dbt.db_connect_no_auth(dbname)
    time = db[timename]
    for tweet in time.find({'user.screen_name': {'$exists': True}}, no_cursor_timeout=True):
        user = tweet['user']
        # tweet['user'] = {'id': user['id']}
        # print tweet
        time.update_one({'id': tweet['id']}, {'$set':{"user": {'id': user['id']}}}, upsert=False)


def remove_random_users(dbname, comname, netname):
    com = dbt.db_connect_col(dbname, comname)
    users = iot.get_values_one_field(dbname, comname, 'id', {'level': 3})
    net = dbt.db_connect_col(dbname, netname)
    for row in net.find(no_cursor_timeout=True):
        uid = row['user']
        fid = row['follower']
        if uid in users or fid in users:
            net.delete_one({'_id': row['_id']})
    com.delete_many({'level': 3})
    # copy_net(dbname, comname, netname)


def copy_com(dbname, com_ori_name, com_des_name):
    com_ori = dbt.db_connect_col(dbname, com_ori_name)
    com_des = dbt.db_connect_col(dbname, com_des_name)
    com_des.create_index("id", unique=True)
    com_des.create_index([('level', pymongo.ASCENDING),
                         ('following_prelevel_node', pymongo.ASCENDING)],
                        unique=False)
    com_des.create_index([('level', pymongo.ASCENDING),
                         ('follower_prelevel_node', pymongo.ASCENDING)],
                        unique=False)
    for user in com_ori.find({'level': {'$lt': 3}},no_cursor_timeout=True):
        try:
            com_des.insert(user)
        except pymongo.errors.DuplicateKeyError:
            pass


def copy_net(dbname, comname, netname):
    # Move networks among two-level users in net2
    net = dbt.db_connect_col(dbname, netname)
    netn = dbt.db_connect_col(dbname, 'net')
    # netn.create_index([("user", pymongo.ASCENDING),
    #              ("follower", pymongo.ASCENDING),
    #              ("type", pymongo.ASCENDING)],
    #             unique=True)
    eduset_list = set(iot.get_values_one_field(dbname, comname, 'id', {'level': 1}))
    oneuser_list = set(iot.get_values_one_field(dbname, comname, 'id', {'level': 2}))
    print(len(eduset_list))
    for row in net.find(no_cursor_timeout=True):
        uid = row['user']
        fid = row['follower']
        if (uid in eduset_list and fid in oneuser_list) \
                or (uid in oneuser_list and fid in eduset_list) \
                or (uid in eduset_list and fid in eduset_list):
            try:
                netn.insert(row)
                net.delete_one({'_id': row['_id']})
            except pymongo.errors.DuplicateKeyError:
                pass





if __name__ == '__main__':
    remove_random_users('random3', 'com', 'net')
    # copy_net('fed', 'com', 'net2')
    # copy_com('fed', 'com', 'com2')
