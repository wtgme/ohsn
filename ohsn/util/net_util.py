# -*- coding: utf-8 -*-
"""
Created on 16:25, 16/02/16

@author: wt
"""

from networkx import *
from ohsn.util import db_util as dbt
import math


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
        DG.add_edge(n1, n2)
    return DG


def load_behavior_network(db_name, collection='None', btype='communication'):
    '''Tweet: 0
    Retweet: 1;
    Reply: 2;
    Direct Mention: 3;
    undirect mention: 4 '''
    btype_dic = {'retweet': [1], 'reply': [2], 'mention': [3], 'communication': [2, 3]}
    DG = DiGraph()
    if collection is 'None':
        cols = db_name
    else:
        db = dbt.db_connect_no_auth(db_name)
        cols = db[collection]
    for row in cols.find({"type": {'$in': btype_dic[btype]}}):
        if btype is 'retweet':
            n2 = row['id0']
            n1 = row['id1']
        else:
            n1 = row['id0']
            n2 = row['id1']
        if n1 != n2:
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
    print 'Getting Gaint Component.........................'
    print 'Network is connected:', (nx.is_connected(G))
    print 'The number of connected components:', (nx.number_connected_components(G))
    largest_cc = max(nx.connected_components(G), key=len)
    return DG.subgraph(largest_cc)


def size_gaint_comp_net_db(db_name, collection='None'):
    DG = load_network(db_name, collection)
    return size_gaint_comp(DG)


def size_gaint_comp(DG):
    G = get_gaint_comp(DG)
    return size_net(G)


def size_net(DG):
    print 'Size of network:', DG.number_of_nodes(), DG.number_of_edges()
    return (DG.number_of_nodes(), DG.number_of_edges())


def diffusion_centrality(BDG, FDG, p=0.2, T=3):
    length = nx.all_pairs_shortest_path_length(FDG, T)
    dc_dict = {}
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
        dc_dict[node] = (dcv, ngv)
    return dc_dict


def net_statis(DG):
    print 'Nodes in network:', DG.number_of_nodes()
    print 'Edges in network:', DG.number_of_edges()
    try:
        print 'Average shortest path length:', nx.average_shortest_path_length(DG)
    except Exception:
        pass


def girvan_newman(G, weight=None):
    """
    The Girvan–Newman algorithm detects communities by progressively removing
    edges from the original graph. Algorithm removes edge with the highest
    betweenness centrality at each step. As the graph breaks down into pieces,
    the tightly knit community structure is exposed and result can be depicted
    as a dendrogram.
    """
    # The copy of G here must include the edge weight data.
    g = G.copy().to_undirected()
    components = []
    while g.number_of_edges() > 0:
        _remove_max_edge(g, weight)
        components.append(tuple(list(H)
                                for H in nx.connected_component_subgraphs(g)))
    return components


def _remove_max_edge(G, weight=None):
    """
    Removes edge with the highest value on betweenness centrality.

    Repeat this step until more connected components than the connected
    components of the original graph are detected.

    It is part of Girvan–Newman algorithm.

    :param G: NetworkX graph
    :param weight: string, optional (default=None) Edge data key corresponding
    to the edge weight.
    """
    number_components = nx.number_connected_components(G)
    while nx.number_connected_components(G) <= number_components:
        betweenness = nx.edge_betweenness_centrality(G, weight=weight)
        max_value = max(betweenness.values())
        # Use a list of edges because G is changed in the loop
        for edge in list(G.edges()):
            if betweenness[edge] == max_value:
                G.remove_edge(*edge)


if __name__ == '__main__':
    g = load_behavior_network('fed', 'sbnet_t1', 'retweet')
    print (g.number_of_nodes()), g.number_of_edges()
    print g.in_degree()
    print g.out_degree()
    print g.in_degree(weight='weight')
    print sum(g.in_degree().values())
    print sum(g.in_degree(weight='weight').values())