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
import tag_network as tn


def cluster_test(file_path):
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
    # g = g.as_undirected(combine_edges=dict(weight="sum"))
    # g = gt.giant_component(g)
    # ---------treated as directed network
    seperations = []
    # modularity = []
    sizes = []
    for i in xrange(100):
        # eigen = g.community_leading_eigenvector(clusters=2, weights='weight')
        # label_pro = g.community_label_propagation(weights='weight', initial=eigen.membership)
        print i
        com = g.community_infomap(edge_weights='weight', vertex_weights='weight')
        seperations.append(com.membership)
        # modularity.append(com.modularity)
        print len(com)
        sizes.append(len(com))
    print '%.3f, %.3f, %.3f, %.3f' %(min(sizes), max(sizes), np.mean(sizes), np.std(sizes))
    aRI = []
    for i in xrange(100):
        for j in xrange(i+1, 100):
            aRI.append(metrics.adjusted_rand_score(seperations[i], seperations[j]))
    print len(aRI)
    # print '%.3f, %.3f, %.3f, %.3f' %(min(modularity), max(modularity), np.mean(modularity), np.std(modularity))
    print '%.3f, %.3f, %.3f, %.3f' %(min(aRI), max(aRI), np.mean(aRI), np.std(aRI))


def two_community(file_path):
    # get two community from networks
    g = gt.Graph.Read_GraphML(file_path)
    gt.summary(g)
    # g = g.as_undirected(combine_edges=dict(weight="sum"))
    g = gt.giant_component(g)
    gt.summary(g)
    # ml = g.community_multilevel(weights='weight', return_levels=True)
    # fast = g.community_fastgreedy(weights='weight')
    # fast_com = fast.as_clustering(n=2)
    # walk = g.community_walktrap(weights='weight')
    # walk_com = walk.as_clustering(n=2)
    infor = g.community_infomap(edge_weights='weight', vertex_weights=None, trials=2)
    # eigen = g.community_leading_eigenvector(clusters=2, weights='weight')
    # label_pro = g.community_label_propagation(weights='weight', initial=eigen.membership)
    # betweet = g.community_edge_betweenness(weights='weight')
    # bet_com = betweet.as_clustering(n=2)
    g.vs['community'] = infor.membership
    g.write_graphml('com-'+file_path)

    return infor.subgraphs()


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


def test_stable_infomap_kmean():
    # Test the stable for the whole process, from infomap clustering hashtag and k-means clustering users
    import tag_network
    core = gt.Graph.Read_GraphML('alled_tag_undir_filter.graphml')
    communication = gt.Graph.Read_GraphML('communication-only-fed-filter.graphml')
    gt.summary(communication)
    communication = gt.giant_component(communication)
    gt.summary(communication)
    users = [(v['name']) for v in communication.vs]
    print len(users)
    tag_network.user_hashtag_profile(core, users)


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
    rec_time = dbt.db_connect_col('fed', 'ed_tag')
    ped_time = dbt.db_connect_col('fed', 'proed_tag_refine')
    data = []

    for i in xrange(1):
        time = [rec_time, ped_time][i]
        name = ['ED', 'Pro-ED'][i]
        for tweet in time.find(no_cursor_timeout=True):
            ts = datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
            data.append([name, tweet['id'], tweet['user']['id'],
                        tweet['retweet_count'], tweet['favorite_count'],
                        ts])
    df = pd.DataFrame(data, columns=['set', 'id', 'user_id', 'retweet_count',
                                     'favorite_count', 'created_at'])
    df.to_csv('ed-tweet-stats.csv')


def ed_tweet_normal_tweet_count():
    user_ids = set(iot.get_values_one_field('fed', 'ed_tag', 'user.id'))
    print len(user_ids)
    com = dbt.db_connect_col('fed', 'com')
    tags = dbt.db_connect_col('fed', 'ed_tag')
    data = []
    for uid in user_ids:
        ed_count = tags.count({'user.id': uid})
        all_count = com.find_one({'id': uid})['timeline_count']
        data.append([uid, ed_count, all_count])
    df = pd.DataFrame(data, columns=['id', 'ed_tweet_count', 'all_tweet_count'])
    df.to_csv('user-ed-stats.csv')





def network_users(file_path):
    # get user list in a network
    g = gt.Graph.Read_GraphML(file_path)
    g = gt.giant_component(g)
    gt.summary(g)
    return g.vs['name']


def cluseter_nodes(btype = 'communication'):
    # cluster users in networks
    g = gt.Graph.Read_GraphML('communication-only-fed-filter.graphml')
    g = gt.giant_component(g)
    gt.summary(g)

    cluters, ids = tn.user_cluster_hashtag('ed-'+btype+'.data')

    # ids = []
    # with open('ed-'+btype+'.data', 'r') as fo:
    #     for line in fo.readlines():
    #         ids.append(line.split(' ')[0])

    g.vs['cluster'] = -1
    for i in xrange(len(cluters)):
        id = ids[i]
        v = g.vs.find(name=id)
        v['cluster'] = cluters[i]
    g.write_graphml('communication-only-fed-filter-hashtag-cluster.graphml')


def count_pro_ratio(btype = 'communication'):
    g = gt.Graph.Read_GraphML('ed-'+btype+'-hashtag-fed-cluster.graphml')
    time = dbt.db_connect_col('fed', 'ed_tag')
    pro_ed_tag = set(iot.read_ed_pro_hashtags())
    pro_rec_tag = set(iot.read_ed_recovery_hashtags())
    for i in range(2):
        clusterset = g.vs.select(cluster=i)
        cluseter_size = len(clusterset)
        print cluseter_size
        pro_ed_count, pro_rec_count = 0.0, 0.0
        for v in clusterset:
            uid = int(v['name'])
            tags = set()
            for tweet in time.find({'user.id': uid}, no_cursor_timeout=True):
                if 'retweeted_status' in tweet:
                    continue
                elif 'quoted_status' in tweet:
                    continue
                else:
                    hashtags = tweet['entities']['hashtags']
                    for hash in hashtags:
                        value = hash['text'].encode('utf-8').lower().replace('_', '').replace('-', '')
                        tags.add(value)
            if len(tags.intersection(pro_ed_tag)) > 0:
                pro_ed_count += 1
            if len(tags.intersection(pro_rec_tag)) > 0:
                pro_rec_count += 1
        print pro_ed_count, pro_rec_count, cluseter_size, pro_ed_count/cluseter_size, pro_rec_count/cluseter_size



def test_clustering_stable(btype = 'communication'):
    # test the stable of clustering users
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score, calinski_harabaz_score
    from sklearn.datasets import load_svmlight_file
    from sklearn import preprocessing
    seperations = []
    modularity = []
    X, y = load_svmlight_file('ed-'+btype+'.data')
    X = X.toarray()
    scaler = preprocessing.StandardScaler().fit(X)
    X = scaler.transform(X)
    # X = load_iris().data
    # y = load_iris().target
    print X.shape
    clusterer = KMeans(n_clusters=2)

    for i in xrange(10):
        cluster_labels = clusterer.fit_predict(X)
        silhouette_avg = silhouette_score(X, cluster_labels)
        seperations.append(cluster_labels)
        modularity.append(silhouette_avg)
    aRI = []
    for i in xrange(10):
        for j in xrange(i+1, 10):
            aRI.append(metrics.adjusted_rand_score(seperations[i], seperations[j]))
    print len(modularity), len(aRI)
    print '%.3f, %.3f, %.3f' %(min(modularity), max(modularity), np.mean(modularity))
    print '%.3f, %.3f, %.3f' %(min(aRI), max(aRI), np.mean(aRI))



if __name__ == '__main__':
    # cluster('rec-proed-communication-hashtag-refine.graphml')
    # cluster('rec-proed-retweet-hashtag-refine.graphml')


    # two_community('ed-retweet-hashtag-fed.graphml')
    # two_community('ed-communication-hashtag-fed.graphml')
    # test_significant('rec-proed-communication-hashtag-refine.graphml')
    # test_significant('rec-proed-retweet-hashtag-refine.graphml')
    # compare_communities('rec-proed-communication-hashtag-refine.graphml')

    # rec_cs, ped_cs = compare_post_time()


    # ped_users = iot.get_values_one_field('fed', 'proed_tag_refine', 'user.id')
    # print len(set(ped_users))
    # rec_user = iot.get_values_one_field('fed', 'prorec_tag_refine', 'user.id')
    # print len(set(rec_user))

    # statis_dbs()



    # cluseter_nodes('communication')
    # cluseter_nodes('retweet')

    # test_clustering_stable('communication')
    # test_clustering_stable('retweet')

    # count_pro_ratio('communication')
    # count_pro_ratio('retweet')

    #-------------------------------Filter network by ed post counts---------------------------------------
    # ed_tweet_normal_tweet_count()
    # g = gt.Graph.Read_GraphML('communication-only-fed.graphml')
    # gt.summary(g)
    #
    # df = pd.read_csv('user-ed-stats.csv')
    # intest = df[df.ed_tweet_count > 2]
    # print (intest)
    # # intest = pickle.load(open('ed-positive-id-str.pick', 'r'))
    #
    # nodes = g.vs.select(name_in=[str(i) for i in intest['id']])
    # print len(nodes)
    # # nodes = g.vs.select(name_in=intest)
    # g = g.subgraph(nodes)
    # gt.summary(g)
    #
    # g.vs.select(_degree=0).delete()
    # gt.summary(g)
    #
    # g.write_graphml('communication-only-fed-filter.graphml')

    #----------------------------------------------------------------------

    #-----------------KMeans for user cluster-----------------------------------------------------
    cluseter_nodes()
    #----------------------------------------------------------------------


    #----------------test louvain lib----------------------------------------------------------
    # import louvain
    # g = gt.Graph.Read_GraphML('alled_tag_undir_filter_pmi.graphml')
    # gt.summary(g)
    # part = louvain.find_partition(g, method='Surprise', weight='pmi')
    # print len(set(part.membership)), part.modularity

    # part = louvain.find_partition(g, method='Modularity', weight='weight', resolution_parameter=1)
    # print len(set(part.membership)), part.modularity

    # for r in np.linspace(0, 1, 200):
    #     part = louvain.find_partition(g, method='RBConfiguration', weight='weight', resolution_parameter=r)
    #     print r, len(set(part.membership)), part.modularity

    # res_parts = louvain.bisect(g, method='RBConfiguration', resolution_range=[0, 1], weight='weight')
    # import pandas as pd
    # import matplotlib.pyplot as plt
    # res_df = pd.DataFrame({
    #          'resolution': res_parts.keys(),
    #          'bisect_value': [bisect.bisect_value for bisect in res_parts.values()],
    #          'cluster_number': [len(set(bisect.partition.membership)) for bisect in res_parts.values()]});
    # # plt.step(res_df['resolution'], res_df['bisect_value']);
    # plt.step(res_df['resolution'], res_df['cluster_number']);
    # # plt.xscale('log');
    # # plt.yscale('log')
    # plt.show()

    # print len(set(part.membership))
    # print part.modularity

    # infor = g.community_infomap(edge_weights='weight', trials=10)
    # print len(set(infor.membership))
    # print infor.modularity
    #
    # g = g.as_undirected(combine_edges=dict(weight="sum"))
    # ml = g.community_multilevel(weights='weight')
    # print len(set(ml.membership))
    # print ml.modularity



    # import louvain
    # G = gt.Graph.Erdos_Renyi(100, 0.1);
    # res_parts = louvain.bisect(G, method='CPM', resolution_range=[0,1]);
    # import pandas as pd
    # import matplotlib.pyplot as plt
    # res_df = pd.DataFrame({
    #          'resolution': res_parts.keys(),
    #          'bisect_value': [bisect.bisect_value for bisect in res_parts.values()]});
    # plt.step(res_df['resolution'], res_df['bisect_value']);
    # plt.xscale('log');
    # plt.show()
    #----------------test louvain lib----------------------------------------------------------

    #------------test hierachy structure--------------------------------------------
    # g = gt.Graph.Read_GraphML('communication-only-fed-filter.graphml')
    # gt.summary(g)
    # g = gt.giant_component(g)
    # gt.summary(g)
    # for edge in g.es:
    #     source_vertex_id = edge.source
    #     target_vertex_id = edge.target
    #     source_vertex = g.vs[source_vertex_id]
    #     target_vertex = g.vs[target_vertex_id]
    #     ew = edge['weight']
    #     print str(source_vertex_id) + ' ' + str(target_vertex_id) + ' ' + str(ew)
    # # # clus = g.community_edge_betweenness(clusters=1, weights='weight')## too mixed, not working
    # # clus = g.community_walktrap(weights='weight')
    # # gt.plot(clus)
    # # plt.show()

    #------------networkx louvain--------------------------------------------
    '''Not support directed networks'''
    # import community
    # import networkx as nx
    # import matplotlib.pyplot as plt
    # G = nx.read_graphml('communication-only-fed-filter.graphml')
    # # giant = max(nx.connected_component_subgraphs(G), key=len)
    # partition = community.best_partition(G)
    # size = float(len(set(partition.values())))
    # pos = nx.spring_layout(G)
    # count = 0.
    # for com in set(partition.values()) :
    #     count = count + 1.
    #     list_nodes = [nodes for nodes in partition.keys()
    #                                 if partition[nodes] == com]
    #     nx.draw_networkx_nodes(G, pos, list_nodes, node_size = 20,
    #                                 node_color = str(count / size))
    #
    #
    # nx.draw_networkx_edges(G,pos, alpha=0.5)
    # plt.show()
    #------------------------------------------------------------------


    cluster_test('alled_tag_undir_filter.graphml')