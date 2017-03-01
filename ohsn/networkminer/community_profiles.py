# -*- coding: utf-8 -*-
"""
Created on 10:33 PM, 3/1/17

@author: tw

This is explore the community of ED and their common followees
who are they?
What are they talk about?
"""
import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))


import ohsn.util.graph_util as gt
import ohsn.util.db_util as dbt
import ohsn.util.io_util as iot
import pymongo

def ed_follow_net():
    # construct ED and their followee network
    g = gt.load_network('fed', 'follownet')
    g.vs['deg'] = g.indegree()
    users = set(iot.get_values_one_field('fed', 'scom', 'id'))
    nodes = []
    for v in g.vs:
        if int(v['name']) in users:
            nodes.append(v)
        elif v['deg'] > 5:
            nodes.append(v)
        else:
            pass
    print 'Filtered nodes: %d' %len(nodes)
    g = g.subgraph(nodes)
    gt.net_stat(g)
    g.write_graphml('ed-friend-follow'+'.graphml')


def ed_follow_community():
    g = gt.Graph.Read_GraphML('ed-friend-follow'+'.graphml')
    gt.summary(g)
    g = g.as_undirected(combine_edges=dict(weight="sum"))
    components = g.clusters()
    g = components.giant()
    gt.summary(g)

def ED_followee():
    # put all ED's followees in follownet
    net = dbt.db_connect_col('fed', 'net2')
    users = set(iot.get_values_one_field('fed', 'scom', 'id'))
    print len(users)
    tem = dbt.db_connect_col('fed', 'follownet')
    for re in net.find():
        if re['follower'] in users:
            try:
                tem.insert(re)
            except pymongo.errors.DuplicateKeyError:
                pass

def out_ed_follow_nets():

    for btype in ['retweet', 'reply', 'mention']:
        g = gt.load_beh_network('fed', 'sbnet', btype)
        g.write_graphml('ed-'+btype+'-follow.graphml')


if __name__ == '__main__':
    ED_followee()
    # ed_follow_net()
    # ed_follow_community()