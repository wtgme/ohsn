# -*- coding: utf-8 -*-
"""
Created on 16:53, 26/05/16

@author: wt
Analysis whether a user often retweet one person
"""

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import ohsn.util.graph_util as gt
import pickle
import ohsn.util.io_util as iot
import numpy as np


def bahavior_net(dbname, comname, bnetname, btype):
    userlist = iot.get_values_one_field(dbname, comname, 'id',
                                        {'timeline_count': {'$gt': 0}})
    return gt.load_all_beh_network(userlist, dbname, bnetname, btype)


def hashtag_net():
    dbnames = [('fed', 'stimeline'),
               ('random', 'timeline'),
               ('young', 'timeline')]
    for dbname, timename in dbnames:
        userlist = iot.get_values_one_field(dbname, 'scom', 'id_str',
                                        {'timeline_count': {'$gt': 0}})
        # g = gt.load_hashtag_network(dbname, timename)
        # pickle.dump(g, open('data/'+dbname+'_hashtag.pick', 'w'))
        g = pickle.load(open('data/'+dbname+'_hashtag.pick', 'r'))
        gnode = g.vs["name"]
        target_nodes = list(set(userlist).intersection(gnode))
        # print target_nodes
        divs = np.array(g.diversity(target_nodes, 'weight'))
        divs = divs[np.isfinite(divs)]
        # print divsersity, max(divsersity), min(divsersity)
        divs_mean = np.mean(divs)
        divs_std = np.std(divs)
        # print divsersity_mean, divsersity_std
        print dbname, 'hashtag', len(target_nodes), len(divs),\
            divs_mean, divs_std


def netstatis(g, userlist):
    g = g.as_undirected(combine_edges=dict(weight="sum"))

    node_n = g.vcount()
    edge_m = g.ecount()
    degree_mean = np.mean(g.indegree())
    degree_std = np.std(g.indegree())
    density = g.density()
    avg_path = g.average_path_length()
    components = g.clusters()
    comp_count = len(components)
    giant_comp = components.giant()
    giant_comp_r = float(giant_comp.vcount())/node_n
    cluster_co_global = g.transitivity_undirected()
    cluster_co_avg = g.transitivity_avglocal_undirected()
    assort = g.assortativity_degree(directed=False)

    gnode = g.vs["name"]
    target_nodes = list(set(userlist).intersection(gnode))
    # print target_nodes
    divs = np.array(g.diversity(target_nodes, 'weight'))
    divs = divs[np.isfinite(divs)]
    # print divsersity, max(divsersity), min(divsersity)
    divs_mean = np.mean(divs)
    divs_std = np.std(divs)
    # print divsersity_mean, divsersity_std

    print node_n, edge_m, round(degree_mean, 3), round(degree_std, 3), round(density, 3), \
        round(avg_path, 3), comp_count, round(giant_comp_r, 3), round(cluster_co_global, 3), \
        round(cluster_co_avg, 3), round(assort, 3), round(divs_mean, 3), round(divs_std, 3)

if __name__ == '__main__':

    dbnames = ['fed', 'random', 'young']
    behaviors = ['retweet', 'reply', 'mention', 'communication', 'all']
    for dbname in dbnames:
        userlist = iot.get_values_one_field(dbname, 'scom', 'id_str',
                                        {'timeline_count': {'$gt': 0}})
        for behavior in behaviors:
            # g = bahavior_net(dbname, 'scom', 'bnet', behavior)
            # pickle.dump(g, open('data/'+dbname+'_'+behavior+'.pick', 'w'))
            print dbname, behavior
            g = pickle.load(open('data/'+dbname+'_'+behavior+'.pick', 'r'))
            netstatis(g, userlist)

    ###do hashtag network###
    # hashtag_net()

