# -*- coding: utf-8 -*-
"""
Created on 14:38, 17/03/17

@author: wt

To study pro-ed and pro-recovery communities
"""

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import ohsn.util.graph_util as gt
import ohsn.util.db_util as dbt
import ohsn.util.io_util as iot
import pymongo
from sklearn import metrics
import numpy as np
import pandas as pd
from random import shuffle
import ohsn.time_series.time_series_split as tsplit
import matplotlib.pyplot as plt
# import matplotlib
# matplotlib.style.use('ggplot')
import pickle
import ohsn.util.plot_util as plu

def cluster(file_path):
    '''
    community_multilevel and community_infomap cannot produce two clusters
    only community_leading_eigenvector and community_fastgreedy can produce two clusters
    label propagation with eigenvector has higher modularity than community_fastgreedy and community_leading_eigenvector alone
    Rand Index: 0.884, 0.974, 0.929 for communication network
                0.807, 0.915, 0.864 for retweet network
    This methods is discarded

    '''
    g = gt.Graph.Read_GraphML(file_path)
    gt.summary(g)
    g = g.as_undirected(combine_edges=dict(weight="sum"))
    g = gt.giant_component(g)
    gt.summary(g)
    #----------------------test--------------
    '''
    # ml = g.community_multilevel(weights='weight', return_levels=True)
    # for m in ml:
    #     print len(m)
    #     print m.modularity
    # comclus = ml[-1].subgraphs()
    eigen = g.community_leading_eigenvector(clusters=2, weights='weight')
    print 'eigenvector:', eigen.modularity
    # label_pro = g.community_label_propagation(weights='weight')
    # print 'label propagation:', label_pro.modularity
    label_pro = g.community_label_propagation(weights='weight', initial=eigen.membership)
    print len(label_pro)
    print 'label propagation with eigenvector:',label_pro.modularity
    fast = g.community_fastgreedy(weights='weight')
    fast_com = fast.as_clustering(n=2)
    print len(fast_com)
    print 'Fast', fast_com.modularity


    fast2 = g.community_fastgreedy(weights='weight')
    fast2_com = fast2.as_clustering(n=2)
    print len(fast2_com)
    print 'Fast', fast2_com.modularity

    print metrics.adjusted_rand_score(fast_com.membership, label_pro.membership)
    print metrics.normalized_mutual_info_score(fast_com.membership, label_pro.membership)

    print metrics.adjusted_rand_score(fast_com.membership, fast2_com.membership)
    print metrics.normalized_mutual_info_score(fast_com.membership, fast2_com.membership)

    # between = g.community_edge_betweenness(clusters=2, directed=False, weights='weight')
    # print between.modularity

    # -----end choose eigenvector and label propogation to community detection-------------
    '''

    # ---------treated as directed network
    '''g = gt.giant_component(g)
    gt.summary(g)
    com = g.community_infomap(edge_weights='weight', trials=2)
    # com = g.community_leading_eigenvector(weights='weight')
    print com.modularity
    print len(com)'''

    seperations = []
    modularity = []
    for i in xrange(100):
        eigen = g.community_leading_eigenvector(clusters=2, weights='weight')
        label_pro = g.community_label_propagation(weights='weight', initial=eigen.membership)
        seperations.append(label_pro.membership)
        modularity.append(label_pro.modularity)
    aRI = []
    for i in xrange(100):
        for j in xrange(i+1, 100):
            aRI.append(metrics.adjusted_rand_score(seperations[i], seperations[j]))
    print len(modularity), len(aRI)
    print '%.3f, %.3f, %.3f' %(min(modularity), max(modularity), np.mean(modularity))
    print '%.3f, %.3f, %.3f' %(min(aRI), max(aRI), np.mean(aRI))


def two_community(file_path):
    # get two community from networks
    g = gt.Graph.Read_GraphML(file_path)
    gt.summary(g)
    g = g.as_undirected(combine_edges=dict(weight="sum"))
    g = gt.giant_component(g)
    gt.summary(g)
    fast = g.community_fastgreedy(weights='weight')
    fast_com = fast.as_clustering(n=2)
    # walk = g.community_walktrap(weights='weight')
    # walk_com = walk.as_clustering(n=2)
    # infor = g.community_infomap(edge_weights='weight', vertex_weights=None, trials=2)
    # eigen = g.community_leading_eigenvector(clusters=2, weights='weight')
    # label_pro = g.community_label_propagation(weights='weight', initial=eigen.membership)
    # betweet = g.community_edge_betweenness(weights='weight')
    # bet_com = betweet.as_clustering(n=2)
    g.vs['community'] = fast_com.membership
    g.write_graphml('com-'+file_path)

    return fast_com.subgraphs()


def compare_communities(file_path):
    # compare the stats of communities of a network
    communities = two_community(file_path)
    for com in communities:
        gt.net_stat(com)


def test_significant(file_path):
    # random shuffle the weights of edges and test the segregate of networks
    g = gt.Graph.Read_GraphML(file_path)
    gt.summary(g)
    g = g.as_undirected(combine_edges=dict(weight="sum"))
    g = gt.giant_component(g)
    gt.summary(g)
    # print g.es['weight']
    fast = g.community_fastgreedy(weights='weight')
    fast_com = fast.as_clustering(n=2)
    orig_mod = fast_com.modularity
    mod_list = []

    for i in xrange(1000):
        weights = g.es["weight"]
        g.rewire()
        g.es["weight"] = weights
        # gt.net_stat(g)
        # print g.es['weight']
        fast = g.community_fastgreedy(weights='weight')
        fast_com = fast.as_clustering()
        mod_list.append(fast_com.modularity)


    amean, astd = np.mean(mod_list), np.std(mod_list)
    print 'simulated values: %.3f +- (%.3f)' %(amean, astd)
    # absobserved = abs(raw_assort)
    # pval = (np.sum(ass_list >= absobserved) +
    #         np.sum(ass_list <= -absobserved))/float(len(ass_list))
    zscore = (orig_mod-amean)/astd
    print 'z-score: %.3f' %zscore


def compare_post_time():
    prec = tsplit.timeline('fed', 'prorec_tag_refine')
    ped = tsplit.timeline('fed', 'proed_tag_refine')
    print len(prec), len(ped)
    fig, ax = plt.subplots()

    df = pd.DataFrame(prec, columns=['Recovery'])
    df.groupby([df["Recovery"].dt.year, df["Recovery"].dt.month]).count().plot(kind="line", ax=ax)
    df = pd.DataFrame(ped, columns=['Pro-ED'])
    df.groupby([df["Pro-ED"].dt.year, df["Pro-ED"].dt.month]).count().plot(kind="line", ax=ax)
    plt.show()


if __name__ == '__main__':
    # cluster('rec-proed-communication-hashtag-refine.graphml')
    # cluster('rec-proed-retweet-hashtag-refine.graphml')


    # two_community('rec-proed-communication-hashtag-refine.graphml')
    # two_community('rec-proed-retweet-hashtag-refine.graphml')
    # test_significant('rec-proed-communication-hashtag-refine.graphml')
    # test_significant('rec-proed-retweet-hashtag-refine.graphml')
    # compare_communities('rec-proed-communication-hashtag-refine.graphml')

    # compare_post_time()

    prec = tsplit.timeline('fed', 'prorec_tag_refine')
    ped = tsplit.timeline('fed', 'proed_tag_refine')
    pickle.dump((prec, ped), open('tweets_dates.pick', 'w'))

    # print len(prec), len(ped)
    #
    # fig, ax = plt.subplots()
    # plu.plot_config()
    #
    # df_rec = pd.DataFrame(prec, columns=['Recovery'])
    # rec_counts = df_rec.groupby([df_rec["Recovery"].dt.year, df_rec["Recovery"].dt.month]).count()
    # rec_counts.plot(kind="line", marker='s', ax=ax)
    # ax.legend(loc='best')
    #
    # df_ped = pd.DataFrame(ped, columns=['Pro-ED'])
    # ped_counts = df_ped.groupby([df_ped["Pro-ED"].dt.year, df_ped["Pro-ED"].dt.month]).count()
    # ped_counts.plot(kind="line", marker='o', ax=ax)
    # ax.legend(loc='best')
    # ax.set_ylabel('Number of tweets')
    # ax.set_xlabel('Year, Month')
    #
    # plt.show()
