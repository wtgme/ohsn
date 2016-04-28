# -*- coding: utf-8 -*-
"""
Created on 16:20, 16/02/16

@author: wt

This script is to use the mesures in 'GOSSIP identifying central individuals in a social network'

Type field in net collection cases duplicated records
"""

from ohsn.util import db_util as dbt
from ohsn.util import net_util
import pymongo
import networkx as nx
import ohsn.util.plot_util as plot
import math


def extract_friend_subnetwork(db_name, comname, fnetname, sfnetname):
    db = dbt.db_connect_no_auth(db_name)
    poi = db[comname]
    net = db[fnetname]
    tem = db[sfnetname]  # subset of friendship network
    tem.create_index([("user", pymongo.ASCENDING),
                    ("follower", pymongo.ASCENDING)],
                    unique=True)
    # index = 0
    userl1 = set([])
    for user in poi.find({}, ['id']):
        # print user['id']
        userl1.add(user['id'])
    for user in userl1:
        for rel in net.find({'user': user}):
            follower = rel['follower']
            if follower in userl1:
                try:
                    tem.insert(rel)
                except pymongo.errors.DuplicateKeyError:
                    pass


def extract_behavior_subnetwork(db_name, comname, bnetname, sbnetname, index=0):
    db = dbt.db_connect_no_auth(db_name)
    if index != 0:
        comname, bnetname, sbnetname = comname+'_t'+str(index), bnetname+'_t'+str(index), sbnetname+'_t'+str(index)
    poi = db[comname]
    net = db[bnetname]
    tem = db[sbnetname]  # subset of behavior network
    tem.create_index([("id0", pymongo.ASCENDING),
                     ("id1", pymongo.ASCENDING),
                     ("type", pymongo.ASCENDING),
                     ("statusid", pymongo.ASCENDING)],
                    unique=True)
    userl1 = set([])
    for user in poi.find({}, ['id']):
        userl1.add(user['id'])

    for user in userl1:
        for rel in net.find({'id0': user}):
            follower = rel['id1']
            if follower in userl1:
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


def tweet_ret_times(db_name, index=0):
    count_list = []
    db = dbt.db_connect_no_auth(db_name)
    colname = 'sbnet'
    if index != 0:
        colname += '_t'+str(index)
    bnet = db[colname]
    for tweet in bnet.distinct('statusid'):
        count = bnet.count({'statusid': tweet})
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


def centrality(dbname, scom, BDG, FDG, p, T):
    db = dbt.db_connect_no_auth(dbname)
    com = db[scom]

    length = nx.all_pairs_shortest_path_length(FDG, T)
    for node in BDG.nodes():
        dcv, ngv = 0.0, 0.0
        for hearer in BDG.successors(node):
            t = length.get(node, {hearer: -1}).get(hearer, -1)
            if t != -1 and t <= T:
                dcv += BDG[node][hearer]['weight']*math.pow(p, t)
        for sayer in BDG.predecessors(node):
            t = length.get(sayer, {node: -1}).get(node, -1)
            if t != -1 and t <= T:
                ngv += BDG[sayer][node]['weight']*math.pow(p, t)
        com.update_one({'id': node}, {'$set': {'dc': dcv, 'ng': ngv}}, upsert=False)
        # user = poi.find_one({'id': node}, ['screen_name'])
        # print str(node) + ',' + user['screen_name']+ ',' + str(dcv) + ',' + str(ngv)
        # print str(node) + ',' + str(dcv) + ',' + str(ngv)


if __name__ == '__main__':

    db_name = 'tyg'
    # tweet_ret_times('fed')
    # extract_friend_subnetwork(db_name, 'com_t1', 'net', 'snet_t1')
    # extract_friend_subnetwork(db_name, 'com_t2', 'net', 'snet_t2')
    # extract_friend_subnetwork(db_name, 'com_t3', 'net', 'snet_t3')
    # extract_friend_subnetwork(db_name, 'com_t4', 'net', 'snet_t4')
    # extract_friend_subnetwork(db_name, 'com_t5', 'net', 'snet_t5')
    extract_behavior_subnetwork(db_name, 'com', 'bnet', 'sbnet', 1)
    extract_behavior_subnetwork(db_name, 'com', 'bnet', 'sbnet', 2)
    extract_behavior_subnetwork(db_name, 'com', 'bnet', 'sbnet', 3)
    extract_behavior_subnetwork(db_name, 'com', 'bnet', 'sbnet', 4)
    extract_behavior_subnetwork(db_name, 'com', 'bnet', 'sbnet', 5)

    # print 'original network'
    # FDG = net_util.load_network(db_name, 'snet')
    # print FDG.number_of_edges()
    # print FDG.number_of_nodes()
    #
    # print 'get gaint_component of network'
    # FDG = net_util.get_gaint_comp(FDG)
    # print FDG.number_of_edges()
    # print FDG.number_of_nodes()
    # print nx.average_shortest_path_length(FDG)
    #
    # for index in range(1, 6):
    #     sbnet = 'sbnet_t'+str(index)
    #     scom = 'com_t'+str(index)
    #     print 'original network'
    #     BDG = net_util.load_behavior_network(db_name, sbnet)
    #     print BDG.number_of_edges()
    #     print BDG.number_of_nodes()
    #
    #     # print 'get gaint_component of network'
    #     # BDG = net_util.get_gaint_comp(BDG)
    #     # print BDG.number_of_edges()
    #     # print BDG.number_of_nodes()
    #
    #     print 'prune nodes not in friendship network'
    #     BDG = prune_bdg(BDG, FDG)
    #     print BDG.number_of_edges()
    #     print BDG.number_of_nodes()
    #     # print nx.average_shortest_path_length(BDG)
    #
    #     centrality(db_name, scom, BDG, FDG, 0.2, 3)