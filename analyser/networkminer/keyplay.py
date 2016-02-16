# -*- coding: utf-8 -*-
"""
Created on 16:20, 16/02/16

@author: wt

This script is to use the mesures in 'GOSSIP identifying central individuals in a social network'

Type field in net collection cases duplicated records
"""
import util.db_util as dbt
import netutil
import pymongo

def extract_friend_subnetwork(db_name):
    db = dbt.db_connect_no_auth(db_name)
    poi = db['com']
    net = db['net']
    tem = db['tmpt']
    tem.create_index([("user", pymongo.ASCENDING),
                    ("follower", pymongo.ASCENDING)],
                            unique=True)
    index = 0
    for user in poi.find({'level': 1}, ['id']):
        index += 1
        print index
        for rel in net.find({'user': user['id']}):
            follower = rel['follower']
            count = poi.count({'id': follower, 'level':1})
            if count > 0:
                try:
                    tem.insert(rel)
                except pymongo.errors.DuplicateKeyError:
                    pass


def extract_behavior_subnetwork(db_name):
    db = dbt.db_connect_no_auth(db_name)
    poi = db['com']
    net = db['bnet']
    tem = db['sbnet']
    tem.create_index([("id0", pymongo.ASCENDING),
                             ("id1", pymongo.ASCENDING),
                             ("relationship", pymongo.ASCENDING),
                             ("statusid", pymongo.ASCENDING),
                             ('created_at', pymongo.ASCENDING)],
                            unique=True)
    index = 0
    for user in poi.find({'level': 1}, ['id']):
        index += 1
        print index
        for rel in net.find({'id0': user['id'], 'relationship': 'retweet'}):
            follower = rel['id1']
            count = poi.count({'id': follower, 'level':1})
            if count > 0:
                try:
                    tem.insert(rel)
                except pymongo.errors.DuplicateKeyError:
                    pass

# extract_friend_subnetwork('fed')
extract_behavior_subnetwork('fed')
DG = netutil.load_network('fed', 'sbnet')
print DG.number_of_edges()
print DG.number_of_nodes()

DG = netutil.get_gaint_comp(DG)
print DG.number_of_edges()
print DG.number_of_nodes()
