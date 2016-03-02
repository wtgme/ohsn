# -*- coding: utf-8 -*-
"""
Created on 16:25, 16/02/16

@author: wt
"""

from networkx import *
import util.db_util as dbt


def load_network(db_name, collection='None'):
    DG = DiGraph()
    if collection is 'None':
        cols = db_name
    else:
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


def load_behavior_network(db_name, collection='None'):
    DG = DiGraph()
    if collection is 'None':
        cols = db_name
    else:
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
    #If edges in both directions (u,v) and (v,u) exist in the graph,
    # attributes for the new undirected edge will be a combination of the
    # attributes of the directed edges.
    G = DG.to_undirected()
    print 'Network is connected:', (nx.is_connected(G))
    print 'The number of connected components:', (nx.number_connected_components(G))
    largest_cc = max(nx.connected_components(G), key=len)

    for node in DG.nodes():
        if node not in largest_cc:
            DG.remove_node(node)
    del G
    return DG


def size_gaint_comp_net(db_name, collection='None'):
    DG = load_network(db_name, collection)
    G = get_gaint_comp(DG)
    return size_net(G)


def size_net(DG):
    return (DG.number_of_nodes(), DG.number_of_edges())


def net_statis(DG):
    print 'Nodes in network:', DG.number_of_nodes()
    print 'Edges in network:', DG.number_of_edges()
    try:
        print 'Average shortest path length:', nx.average_shortest_path_length(DG)
    except Exception:
        pass