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
    # print G.number_of_nodes()
    BG = nt.load_behavior_network(dbname, bnetname, 'retweet')
    close_cen = nt.closeness_centrality(G)
    between_cen = nt.betweenness_centrality(G)
    eigen_cen = nt.eigenvector_centrality_numpy(G)
    kt_cen = nt.katz_centrality_numpy(G)
    diff_cen = nt.diffusion_centrality(BG, G)

    indegree_all = sum(G.in_degree().values())
    outdegree_all = sum(G.out_degree().values())
    close_cen_all = sum(close_cen.values())
    between_cen_all = sum(between_cen.values())
    eigen_cen_all = sum(eigen_cen.values())
    kt_cen_all = sum(kt_cen.values())
    diff_cen_all = sum([diff_cen[item][0] for item in diff_cen])
    goss_all = sum([diff_cen[item][1] for item in diff_cen])

    for v in G.nodes():
        values = com.find_one({'id': v}, ['id', 'net_anal']).get('net_anal', {'mined': True})
        net_sta = {}
        net_sta['node_no'] = G.number_of_nodes()
        net_sta['indegree'] = G.in_degree(v)
        net_sta['indegree_all'] = indegree_all
        net_sta['outdegree'] = G.out_degree(v)
        net_sta['outdegree_all'] = outdegree_all
        net_sta['closeness_centrality'] = close_cen[v]
        net_sta['closeness_centrality_all'] = close_cen_all
        net_sta['betweenness_centrality'] = between_cen[v]
        net_sta['betweenness_centrality_all'] = between_cen_all
        net_sta['eigenvector_centrality'] = eigen_cen[v]
        net_sta['eigenvector_centrality_all'] = eigen_cen_all
        net_sta['katz_centrality'] = kt_cen[v]
        net_sta['katz_centrality_all'] = kt_cen_all
        net_sta['diffusion_centrality'] = diff_cen.get(v, [0.0, 0.0])[0]
        net_sta['diffusion_centrality_all'] = diff_cen_all
        net_sta['gossip'] = diff_cen.get(v, [0.0, 0.0])[1]
        net_sta['gossip_all'] = goss_all
        values['friendship_net'] = net_sta
        com.update_one({'id': v}, {'$set': {'net_anal': values}}, upsert=True)


def beh_net_stat(dbname, comname, bnetname, btype):
    db = dbt.db_connect_no_auth(dbname)
    com = db[comname]
    G = nt.load_behavior_network(dbname, bnetname, btype)

    close_cen = nt.closeness_centrality(G)
    between_cen = nt.betweenness_centrality(G)
    between_cen_weight = nt.betweenness_centrality(G, weight='weight')
    eigen_cen = nt.eigenvector_centrality_numpy(G)
    eigen_cen_weight = nt.eigenvector_centrality_numpy(G, weight='weight')
    kt_cen = nt.katz_centrality_numpy(G)
    kt_cen_weight = nt.katz_centrality_numpy(G, weight='weight')

    indegree_all = sum(G.in_degree().values())
    instrength_all = sum(G.in_degree(weight='weight').values())
    outdegree_all = sum(G.out_degree().values())
    outstrength_all = sum(G.out_degree(weight='weight').values())
    close_cen_all = sum(close_cen.values())
    between_cen_all = sum(between_cen.values())
    between_cen_weight_all = sum(between_cen_weight.values())
    eigen_cen_all = sum(eigen_cen.values())
    eigen_cen_weight_all = sum(eigen_cen_weight.values())
    kt_cen_all = sum(kt_cen.values())
    kt_cen_weight_all = sum(kt_cen_weight.values())

    for v in G.nodes():
        values = com.find_one({'id': v}, ['id', 'net_anal']).get('net_anal', {'mined': True})
        net_sta = {}
        net_sta['node_no'] = G.number_of_nodes()
        net_sta['indegree'] = G.in_degree(v)
        net_sta['instrength'] = G.in_degree(v, weight='weight')
        net_sta['indegree_all'] = indegree_all
        net_sta['instrength_all'] = instrength_all
        net_sta['outdegree'] = G.out_degree(v)
        net_sta['outstrength'] = G.out_degree(v, weight='weight')
        net_sta['outdegree_all'] = outdegree_all
        net_sta['outstrength_all'] = outstrength_all
        net_sta['closeness_centrality'] = close_cen[v]
        net_sta['closeness_centrality_all'] = close_cen_all
        net_sta['betweenness_centrality'] = between_cen[v]
        net_sta['betweenness_centrality_weighted'] = between_cen_weight[v]
        net_sta['betweenness_centrality_all'] = between_cen_all
        net_sta['betweenness_centrality_weighted_all'] = between_cen_weight_all
        net_sta['eigenvector_centrality'] = eigen_cen[v]
        net_sta['eigenvector_centrality_weighted'] = eigen_cen_weight[v]
        net_sta['eigenvector_centrality_all'] = eigen_cen_all
        net_sta['eigenvector_centrality_weighted_all'] = eigen_cen_weight_all
        net_sta['katz_centrality'] = kt_cen[v]
        net_sta['katz_centrality_all'] = kt_cen_all
        net_sta['katz_centrality_weighted'] = kt_cen_weight[v]
        net_sta['katz_centrality_weighted_all'] = kt_cen_weight_all

        values[btype+'_net'] = net_sta
        com.update_one({'id': v}, {'$set': {'net_anal': values}}, upsert=True)


if __name__ == '__main__':
    dbname = 'tyg'
    network_stat(dbname, 'scom', 'snet', 'sbnet')
    for btype in ['retweet', 'reply', 'mention', 'communication']:
        beh_net_stat(dbname, 'scom', 'sbnet', btype)
    # for i in range(1, 6):
    #     comname, bnetname, netname = 'com_t'+ str(i), 'sbnet_t'+str(i), 'snet_t'+str(i)
    #     print dbname, comname, bnetname, netname
    #     network_stat(dbname, comname, netname, bnetname)
    #     for btype in ['retweet', 'reply', 'mention', 'communication']:
    #         beh_net_stat(dbname, comname, bnetname, btype)