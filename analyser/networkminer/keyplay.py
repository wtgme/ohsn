# -*- coding: utf-8 -*-
"""
Created on 16:20, 16/02/16

@author: wt

This script is to use the mesures in 'GOSSIP identifying central individuals in a social network'

Type field in net collection cases duplicated records
"""

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
import util.db_util as dbt
import netutil
import pymongo
import networkx as nx
import util.plot_util as plot
import math


def extract_friend_subnetwork(db_name):
    db = dbt.db_connect_no_auth(db_name)
    poi = db['com']
    net = db['net']
    tem = db['snet']  # subset of friendship network
    tem.create_index([("user", pymongo.ASCENDING),
                    ("follower", pymongo.ASCENDING)],
                            unique=True)
    # index = 0
    for user in poi.find({'level': 1}, ['id']):
        # index += 1
        # print index
        for rel in net.find({'user': user['id']}):
            follower = rel['follower']
            count = poi.count({'id': follower, 'level':1})
            if count > 0:
                try:
                    tem.insert(rel)
                except pymongo.errors.DuplicateKeyError:
                    pass


def extract_behavior_subnetwork(db_name, relationship=None):
    db = dbt.db_connect_no_auth(db_name)
    poi = db['com']
    net = db['bnet']
    tem = db['sbnet']  # subset of behavior network
    tem.create_index([("id0", pymongo.ASCENDING),
                             ("id1", pymongo.ASCENDING),
                             ("relationship", pymongo.ASCENDING),
                             ("statusid", pymongo.ASCENDING),
                             ('created_at', pymongo.ASCENDING)],
                            unique=True)
    # index = 0
    for user in poi.find({'level': 1}, ['id']):
        # index += 1
        # print index
        find_cri = {'id0': user['id']}
        if relationship != None:
            find_cri['relationship'] = relationship
        for rel in net.find(find_cri):
            follower = rel['id1']
            count = poi.count({'id': follower, 'level':1})
            if count > 0:
                try:
                    tem.insert(rel)
                except pymongo.errors.DuplicateKeyError:
                    pass


def get_retweeted_tweet(db_name):
    db = dbt.db_connect_no_auth(db_name)
    bnet = db['sbnet']
    timeline = db['timeline']
    for net in bnet.find({}):
        sid = net['statusid']
        orig = timeline.find_one({'id': sid}, ['retweeted_status'])
        oid = orig['retweeted_status']['id']
        bnet.update({'statusid': sid}, {'$set': {"ostatusid": oid}})


def tweet_ret_times(db_name):
    count_list = []
    db = dbt.db_connect_no_auth(db_name)
    bnet = db['sbnet']
    for tweet in bnet.distinct('ostatusid'):
        count = bnet.count({'ostatusid': tweet})
        count_list.append(count)
        # print tweet, count
    print min(count_list), max(count_list), len(count_list)
    plot.pdf_plot_one_data(count_list, 'NO.RT')


def prune_bdg(BDG, FDG):
    for node in BDG.nodes():
        if node not in FDG.nodes():
            # print node, BDG.successors(node), BDG.predecessors(node)
            BDG.remove_node(node)
    return BDG


def centrality(BDG, FDG, p, T):
    # db = dbt.db_connect_no_auth('fed')
    # poi = db['com']
    dic = {}
    length = nx.all_pairs_shortest_path_length(FDG, T)
    for node in BDG.nodes():
        dcv, ngv = 0.0, 0.0
        for hearer in BDG.successors(node):
            t = length.get(node, {hearer: -1}).get(hearer, -1)
            if t!=-1 and t<=T:
                dcv += BDG[node][hearer]['weight']*math.pow(p, t)
        for sayer in BDG.predecessors(node):
            t = length.get(sayer, {node: -1}).get(node, -1)
            if t!=-1 and t<=T:
                ngv += BDG[sayer][node]['weight']*math.pow(p, t)
        dic[node] = (dcv, ngv)
        # user = poi.find_one({'id': node}, ['screen_name'])
        # print str(node) + ',' + user['screen_name']+ ',' + str(dcv) + ',' + str(ngv)
        print str(node) + ',' + str(dcv) + ',' + str(ngv)
    return dic

db_name = 'young'
# tweet_ret_times('fed')
extract_friend_subnetwork(db_name)
extract_behavior_subnetwork(db_name)

print 'original network'
FDG = netutil.load_network(db_name, 'snet')
print FDG.number_of_edges()
print FDG.number_of_nodes()

print 'get gaint_component of network'
FDG = netutil.get_gaint_comp(FDG)
print FDG.number_of_edges()
print FDG.number_of_nodes()
print nx.average_shortest_path_length(FDG)

# print 'original network'
# BDG = netutil.load_behavior_network(db_name, 'sbnet')
# print BDG.number_of_edges()
# print BDG.number_of_nodes()
#
# print 'get gaint_component of network'
# BDG = netutil.get_gaint_comp(BDG)
# print BDG.number_of_edges()
# print BDG.number_of_nodes()

# print 'prune nodes not in friendship network'
# BDG = prune_bdg(BDG, FDG)
# print BDG.number_of_edges()
# print BDG.number_of_nodes()
# print nx.average_shortest_path_length(BDG)

# centrality(BDG, FDG, 0.2, 3)