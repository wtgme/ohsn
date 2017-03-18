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

def cluster(file_path):
    '''
    community_multilevel and community_infomap cannot produce two clusters
    only community_leading_eigenvector and community_fastgreedy can produce two clusters
    label propagation with eigenvector has higher modularity than community_fastgreedy and community_leading_eigenvector alone
    Rand Index: 0.884, 0.974, 0.929 for communication network
                0.807, 0.915, 0.864 for retweet network
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

def

if __name__ == '__main__':
    cluster('rec-proed-communication-hashtag-refine.graphml')
    cluster('rec-proed-retweet-hashtag-refine.graphml')