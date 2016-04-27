# -*- coding: utf-8 -*-
"""
Created on 4:39 PM, 4/27/16

@author: tw
"""

import ohsn.util.db_util as dbt
import ohsn.util.graph_util as gt
import ohsn.util.net_util as nt


def network_stat(dbname, comname, fnetname, bnetname):
    db = dbt.db_connect_no_auth(dbname)
    com = db[comname]
    G = nt.load_network(dbname, fnetname)
    BG = nt.load_behavior_network(dbname, bnetname, 'retweet')
    close_cen = nt.closeness_centrality(G)
    between_cen = nt.closeness_centrality(G)
    eigen_cen = nt.eigenvector_centrality(G)
    kt_cen = nt.katz_centrality(G)
    diff_cen = nt.diffusion_centrality(BG, G)
    for v in G.nodes():
        values = com.find_one({'id': v}, ['id', 'net_anal'])['net_anal']
        net_sta = {}
        net_sta['indegree'] = G.in_degree(v)
        net_sta['outdegree'] = G.out_degree(v)
        net_sta['closeness_centrality'] = close_cen[v]
        net_sta['betweenness_centrality'] = between_cen[v]
        net_sta['eigenvector_centrality'] = eigen_cen[v]
        net_sta['katz_centrality'] = kt_cen[v]
        net_sta['diffusion_centrality'] = diff_cen[v][0]
        net_sta['gossip'] = diff_cen[v][1]
        values['friendship_net'] = net_sta
        com.update_one({'id': v}, {'$set': {'net_anal': values}}, upsert=True)



