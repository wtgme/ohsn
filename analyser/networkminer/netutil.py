# -*- coding: utf-8 -*-
"""
Created on 16:25, 16/02/16

@author: wt
"""

from networkx import *
import util.db_util as dbt


def load_network(db_name, collection):
    DG = DiGraph()
    db = dbt.db_connect_no_auth(db_name)
    cols = db[collection]
    for row in cols.find({}):
        n1 = row['user']
        n2 = row['follower']
        weightv = 1
        if (DG.has_node(n1)) and (DG.has_node(n2)) and (DG.has_edge(n1, n2)):
            DG[n1][n2]['weight'] += weightv
        else:
            DG.add_edge(n1, n2, weight=weightv)
    return DG


def load_behavior_network(db_name, collection):
    DG = DiGraph()
    db = dbt.db_connect_no_auth(db_name)
    cols = db[collection]
    for row in cols.find({}):
        n1 = row['id1']
        n2 = row['id0']
        weightv = 1
        if (DG.has_node(n1)) and (DG.has_node(n2)) and (DG.has_edge(n1, n2)):
            DG[n1][n2]['weight'] += weightv
        else:
            DG.add_edge(n1, n2, weight=weightv)
    return DG


def get_gaint_comp(DG):
    G = DG.to_undirected()
    print 'Network is connected:', (nx.is_connected(G))
    print 'The number of connected components:', (nx.number_connected_components(G))
    largest_cc = max(nx.connected_components(G), key=len)

    for node in DG.nodes():
        if node not in largest_cc:
            DG.remove_node(node)
    del G
    return DG