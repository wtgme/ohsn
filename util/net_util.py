# -*- coding: utf-8 -*-
"""
Created on 16:25, 16/02/16

@author: wt
"""

import networkx as nx
import util.db_util as dbt


def load_network(db_name, collection='None'):
    DG = nx.DiGraph()
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


def load_beh_network(db_name, collection):
    DG = nx.Graph()
    db = dbt.db_connect_no_auth(db_name)
    cols = db[collection]
    for row in cols.find({'type': {'$in': [1, 2, 3]}}, no_cursor_timeout=True):
        n1 = row['id0']
        n2 = row['id1']
        weightv = 1
        if (DG.has_node(n1)) and (DG.has_node(n2)) and (DG.has_edge(n1, n2)):
            DG[n1][n2]['weight'] += weightv
        else:
            DG.add_edge(n1, n2, weight=weightv)
    return DG


def load_behavior_network(db_name, collection='None'):
    DG = nx.DiGraph()
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


def get_gaint_comp(G):
    #If edges in both directions (u,v) and (v,u) exist in the graph,
    # attributes for the new undirected edge will be a combination of the
    # attributes of the directed edges.
    # G = DG.to_undirected()
    print 'Getting Gaint Component.........................'
    print 'Network is connected:', (nx.is_connected(G))
    print 'The number of connected components:', (nx.number_connected_components(G))
    largest_cc = max(nx.connected_components(G), key=len)
    return G.subgraph(largest_cc)


def size_gaint_comp_net_db(db_name, collection='None'):
    DG = load_network(db_name, collection)
    return size_gaint_comp(DG)


def size_gaint_comp(DG):
    G = get_gaint_comp(DG)
    return size_net(G)


def size_net(DG):
    print 'Size of network:', DG.number_of_nodes(), DG.number_of_edges()
    return (DG.number_of_nodes(), DG.number_of_edges())


def net_statis(DG):
    print 'Nodes in network:', DG.number_of_nodes()
    print 'Edges in network:', DG.number_of_edges()
    try:
        print 'Average shortest path length:', nx.average_shortest_path_length(DG)
    except Exception:
        pass


def girvan_newman(G, weight=None):
    """Find communities in graph using Girvan–Newman method.

    Parameters
    ----------
    G : NetworkX graph

    weight : string, optional (default=None)
       Edge data key corresponding to the edge weight.

    Returns
    -------
    List of tuples which contains the clusters of nodes.

    Examples
    --------
    >>> G = nx.path_graph(10)
    >>> comp = girvan_newman(G)
    >>> comp[0]
    ([0, 1, 2, 3, 4], [8, 9, 5, 6, 7])

    Notes
    -----
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
