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
from scipy import stats
from datetime import datetime

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
    # prec = tsplit.timeline('fed', 'prorec_tag_refine')
    # ped = tsplit.timeline('fed', 'proed_tag_refine')
    # pickle.dump((prec, ped), open('tweets_dates.pick', 'w'))
    prec, ped = pickle.load(open('tweets_dates.pick', 'r'))
    print len(prec), len(ped)

    '''Get index '''
    mind = min(min(prec), min(ped))
    maxd = max(max(prec), max(ped))
    print mind, maxd
    indeces = pd.date_range(mind, maxd, freq='M')

    plu.plot_config()
    fig, ax = plt.subplots()

    '''counting'''
    df_rec = pd.DataFrame(prec, columns=['Recovery'])
    df_rec['year'] = df_rec["Recovery"].dt.year
    df_rec['month'] = df_rec["Recovery"].dt.month
    rec_counts = df_rec.groupby([df_rec["year"], df_rec["month"]]).count()

    '''Get count per month'''
    rec_cs = [0.0]*len(indeces)
    for i in xrange(len(indeces)):
        year = indeces[i].year
        month = indeces[i].month
        count = rec_counts.loc[(rec_counts.index.get_level_values('year') == year) & (rec_counts.index.get_level_values('month') == month)]
        if not count.empty:
            rec_cs[i] = count.iloc[0, 1]
    '''Plot series'''
    rec_s = pd.Series(rec_cs, index=indeces, name='Pro-recovery')
    rec_s.plot(kind="line", marker='s', ax=ax)
    ax.legend(loc='best')

    df_ped = pd.DataFrame(ped, columns=['Pro-ED'])
    df_ped['year'] = df_ped['Pro-ED'].dt.year
    df_ped['month'] = df_ped['Pro-ED'].dt.month
    ped_counts = df_ped.groupby([df_ped["year"], df_ped["month"]]).count()

    ped_cs = [0.0]*len(indeces)
    for i in xrange(len(indeces)):
        year = indeces[i].year
        month = indeces[i].month
        count = ped_counts.loc[(ped_counts.index.get_level_values('year') == year) & (ped_counts.index.get_level_values('month') == month)]
        if not count.empty:
            ped_cs[i] = count.iloc[0, 1]

    ped_s = pd.Series(ped_cs, index=indeces, name='Pro-ED')
    ped_s.plot(kind="line", marker='o', ax=ax)
    ax.legend(loc='best')

    ax.set_ylabel('Number of tweets')
    ax.set_xlabel('Date')
    print len(rec_cs), len(ped_cs), len(indeces)
    s, p = stats.kendalltau(rec_cs, ped_cs)
    print s, p
    print ('kendalltau test: %.2f, p-value: %.5f' %(s, p))
    s, p = stats.spearmanr(rec_cs, ped_cs)
    print s, p
    print ('spearmanr test: %.2f, p-value: %.5f' %(s, p))
    plt.show()

    return rec_cs, ped_cs


def statis_dbs():
    '''Stats of proed and prorec tweets'''
    rec_time = dbt.db_connect_col('fed', 'prorec_tag_refine')
    ped_time = dbt.db_connect_col('fed', 'proed_tag_refine')
    data = []

    for i in xrange(2):
        time = [rec_time, ped_time][i]
        name = ['Pro-recovery', 'Pro-ED'][i]
        for tweet in time.find(no_cursor_timeout=True):
            ts = datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
            data.append([name, tweet['id'], tweet['user']['id'],
                        tweet['retweet_count'], tweet['favorite_count'],
                        ts])
    df = pd.DataFrame(data, columns=['set', 'id', 'user_id', 'retweet_count',
                                     'favorite_count', 'created_at'])
    df.to_csv('pro-tweet-stats-refine.csv')


if __name__ == '__main__':
    # cluster('rec-proed-communication-hashtag-refine.graphml')
    # cluster('rec-proed-retweet-hashtag-refine.graphml')


    two_community('ed-retweet-hashtag-rmspam.graphml')
    two_community('ed-communication-hashtag-rmspam.graphml')
    # test_significant('rec-proed-communication-hashtag-refine.graphml')
    # test_significant('rec-proed-retweet-hashtag-refine.graphml')
    # compare_communities('rec-proed-communication-hashtag-refine.graphml')

    # rec_cs, ped_cs = compare_post_time()


    # ped_users = iot.get_values_one_field('fed', 'proed_tag_refine', 'user.id')
    # print len(set(ped_users))
    # rec_user = iot.get_values_one_field('fed', 'prorec_tag_refine', 'user.id')
    # print len(set(rec_user))

    # statis_dbs()


