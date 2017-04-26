# -*- coding: utf-8 -*-
"""
Created on 9:13 PM, 8/11/16

@author: tw
"""

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import ohsn.util.db_util as dbt
import matplotlib
import ohsn.util.graph_util as gt
import ohsn.util.io_util as iot
import pickle
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import ohsn.util.plot_util as pll
import igraph as ig
from scipy import spatial
import networkx as nx
import random as rand
import pymongo
import pandas as pd

def pdf(data):
    pll.plot_pdf_mul_data([data], ['Edge Weight'], ['r'], ['o'], labels=['Edge Weight'],
                          linear_bins=False, central=False, fit=True, fitranges=[(1, 10000)])


def tag_record(dbname, colname, filename):
    g = gt.load_hashtag_coocurrent_network_undir(dbname, colname)
    gt.summary(g)
    g.write_graphml(filename+'_tag_undir.graphml')
    return g


def mixing_para(g):
    '''
    calculate mixing parameter: http://www.nature.com/articles/srep30750
    :param g:
    :return:
    '''
    ext = 0.0
    all = 0.0
    for idv, v in enumerate(g.vs):
        neighs = g.neighbors(idv) # input id or name return ids
        # print idv in neighs
        for n in neighs:
            # print '------------------'
            # print idv, n
            if g.vs[idv]['group'] != g.vs[n]['group']:
                eid = g.get_eid(idv, n)
                ext += g.es[eid]['weight']
                # ext += 1
            eid = g.get_eid(idv, n)
            # print g.es[eid].source, g.es[eid].target
            all += g.es[eid]['weight']
            # all += 1
    print ext/all


def hashtag_filter(filename):
    '''
    Get most related hashtag to recovery and proed
    :param filename:
    :return:
    '''
    g = gt.Graph.Read_GraphML(filename+'_tag_undir.graphml')
    rec_hash, ed_hash = {}, {}
    vw_sum = sum(g.vs["weight"])
    for edge in g.es:
        source_vertex_id = edge.source
        target_vertex_id = edge.target
        source_vertex = g.vs[source_vertex_id]
        target_vertex = g.vs[target_vertex_id]
        ew = edge['weight']
        # edge['pmi'] = np.log(float(ew*vw_sum)/(source_vertex['weight']*target_vertex['weight']))
        edge['pmi'] = float(ew/(source_vertex['weight']+target_vertex['weight']))
    tv = g.vs.find(name="proanamia")
    print tv
    for n in g.neighbors(tv):
        rec_hash[g.vs[n]['name']] = g.es[g.get_eid(tv, n)]['pmi']
    name_list = list(sorted(rec_hash, key=rec_hash.get, reverse=True))
    for n in name_list:
        print n, rec_hash[n]



def community_vis(filename, ctype):
    '''
    Load Network and output js to vis.js
    :param filename:
    :return:
    '''
    # load network
    # g = pickle.load(open('data/'+filename+'_tag_undir.pick', 'r'))
    # gt.net_stat(g)
    # # Filter network
    # nodes = g.vs.select(weight_gt=3)
    # print 'Filtered nodes: %d' %len(nodes)
    # g = g.subgraph(nodes)
    # nodes = g.vs.select(user_gt=3)
    # print 'Filtered nodes: %d' %len(nodes)
    # g = g.subgraph(nodes)
    g = gt.Graph.Read_GraphML(filename+'_tag_undir.graphml')

    gt.net_stat(g)
    # g = gt.giant_component(g)
    # Community detection
    if ctype == 'ml':
        com = g.community_multilevel(weights='weight', return_levels=False)
    else:
        com = g.community_infomap(edge_weights='weight', vertex_weights='weight')
    print com
    g.vs['group'] = com.membership
    # print g.vs['group']
    # gt.summary(g)
    mixing_para(g)

    # edges = g.es.select(weight_gt=50)
    # print 'Filtered edges: %d' %len(edges)
    # g = g.subgraph_edges(edges)
    # gt.net_stat(g)

    Coo={}
    for x in g.vs['group']:
        Coo[x]=(rand.randint(-600, 600), rand.randint(-600, 600))

    with open('data/' + ctype + '_' +filename+'_tag_undir.js', 'w') as fw:
        fw.write('var nodes = [\n')
        for idv, v in enumerate(g.vs):
            fw.write('{id: ' + str(idv+1) + ', '+
                     'label: \'' + g.vs[idv]['name'] +'\', ' +
                     'value: ' + str(g.vs[idv]['weight']) + ', ' +
                     'title: \' Tags: ' + g.vs[idv]['name'] + '<br> Occurrence: ' + str(g.vs[idv]['weight']) +
                     '<br> Group: ' + str(g.vs[idv]['group']) + '\', ' +
                     'x: ' + str(Coo[g.vs[idv]['group']][0]+rand.randint(0, 300)) + ', ' +
                     'y: ' + str(Coo[g.vs[idv]['group']][1]+rand.randint(0, 300)) + ', ' +
                     'group: ' + str(g.vs[idv]['group']) + '}, \n')
        fw.write('];\n var edges = [\n')
        for ide, e in enumerate(g.es):
            fw.write('{from: ' + str(e.source+1) + ', ' +
                     'to: ' + str(e.target+1) + ', ' +
                     'title: \' Tags: ' + g.vs[e.source]['name'] + ' ' + g.vs[e.target]['name'] + '<br> Co-occurrence: ' + str(g.es[ide]['weight']) + '\', ' +
                     'value: ' + str(g.es[ide]['weight']) +
                     '},\n')
        fw.write('];\n')


def compare_direct_undir():
    # Compare difference between directed and undirected networks
    from sklearn import metrics
    g = gt.Graph.Read_GraphML('ed_tag.graphml')
    gt.net_stat(g)
    gu = gt.Graph.Read_GraphML('ed_tag_undir.graphml')
    gt.net_stat(gu)
    com = g.community_infomap(edge_weights='weight', vertex_weights='weight')
    comu1 = gu.community_infomap(edge_weights='weight', vertex_weights='weight')
    comu2 = gu.community_infomap(edge_weights='weight', vertex_weights='weight')
    mem = com.membership
    memu1 = comu1.membership
    memu2 = comu2.membership
    print metrics.adjusted_rand_score(mem, memu1)
    print metrics.normalized_mutual_info_score(mem, memu1)
    print metrics.adjusted_rand_score(memu2, memu1)
    print metrics.normalized_mutual_info_score(memu2, memu1)



def transform(filename):
    # transform networt types
    g = gt.Graph.Read_GraphML(filename+'.graphml')
    g.vs['id'] = g.vs['name']
    g.write_pajek(filename+".net")


def plot_graph(g, filename):
    # Plot graph
    visual_style = {}
    layout = g.layout("fr")
    visual_style["vertex_size"] = np.log2(g.vs['weight'])*2
    visual_style["vertex_color"] = 'tomato'
    visual_style["vertex_label"] = ''
    # visual_style["edge_width"] = np.array(g.es['weight'])*10
    visual_style["edge_width"] = np.array(g.es['weight'])+1
    # visual_style["edge_color"] = 'slategrey'
    visual_style["layout"] = layout
    visual_style["margin"] = 10
    visual_style["bbox"] = (1024, 768)
    ig.plot(g, filename+'.pdf', **visual_style)


def community_net(rec_g, ped_g):
    # construct community networks of two network based Jarcard similarities
    gc_rec_g = gt.giant_component(rec_g)
    com_rec_g = gc_rec_g.community_multilevel(weights='weight', return_levels=False)
    comclus_rec_g = com_rec_g.subgraphs()
    print 'Community stats: #communities, modularity', len(comclus_rec_g), com_rec_g.modularity

    gc_ped_g = gt.giant_component(ped_g)
    com_ped_g = gc_ped_g.community_multilevel(weights='weight', return_levels=False)
    comclus_ped_g = com_ped_g.subgraphs()
    print 'Community stats: #communities, modularity', len(comclus_ped_g), com_ped_g.modularity
    name_map, edges, node_weight = {}, {}, {}

    for i in xrange(len(comclus_rec_g)):
        comclu_rec_g = comclus_rec_g[i]
        rec_nodes = set([v['name'] for v in comclu_rec_g.vs])
        max_fre_rec = max(comclu_rec_g.vs['weight'])
        max_fre_rec_tag = comclu_rec_g.vs.find(weight_eq=max_fre_rec)['name']
        n1 = 'rec_'+str(i)+'_'+max_fre_rec_tag
        for j in xrange(len(comclus_ped_g)):
            comclu_ped_g = comclus_ped_g[j]
            max_fre = max(comclu_ped_g.vs['weight'])
            ed_nodes = set([v['name'] for v in comclu_ped_g.vs])
            max_fre_tag = comclu_ped_g.vs.find(weight_eq=max_fre)['name']
            n2 = 'ped_'+str(j)+'_'+max_fre_tag

            n1id = name_map.get(n1, len(name_map))
            name_map[n1] = n1id
            node_weight[n1id] = sum(comclu_rec_g.vs['weight'])

            n2id = name_map.get(n2, len(name_map))
            name_map[n2] = n2id
            node_weight[n2id] = sum(comclu_ped_g.vs['weight'])


            similarity = float(len(rec_nodes.intersection(ed_nodes)))
                         # /len(rec_nodes.union(ed_nodes))
            if similarity > 10:
                edges[(n1id, n2id)] = similarity
    g = gt.Graph(len(name_map), directed=False)
    g.vs["name"] = list(sorted(name_map, key=name_map.get))
    g.vs['weight'] = [node_weight[i] for i in xrange(len(node_weight))]
    g.add_edges(edges.keys())
    g.es["weight"] = edges.values()
    for v in g.vs:
        tokens = v['name'].split('_')
        v['set'] = tokens[0]
        v['tag'] = tokens[2]
    g.write_graphml('hashtag_inter_net.graphml')

    gc = gt.giant_component(g)
    tagets_communities = {}
    for v in gc.vs:
        tokens = v['name'].split('_')
        com_list = tagets_communities.get(tokens[0], [])
        com_list.append(int(tokens[1]))
        tagets_communities[tokens[0]] = com_list
    return tagets_communities


def community(g=None):
    '''
    Detect communities in the co-occurrence network of hashtag
    Use multilevel to detect communities
    Only select communities whose sizes are larger than a threshold
    :param g:
    :return:
    hash_com: {hashtag: community_index}
    com_size: {community_index: community_size}
    '''
    gt.summary(g)
    # vs = g.vs(weight_gt=3, user_gt=3)
    # g = g.subgraph(vs)
    gc = gt.giant_component(g)
    gt.summary(gc)
    # g.write_graphml('fed_tag_undir_over3.graphml')
    # com = gc.community_multilevel(weights='weight', return_levels=False)
    com = g.community_infomap(edge_weights='weight', vertex_weights='weight', trials=1)
    comclus = com.subgraphs()
    print 'Community stats: #communities, modularity', len(comclus), com.modularity
    index = 0
    nonsingle = 0
    hash_com = {}
    com_size = {}
    for comclu in comclus:
        print '---------- Community ', index, '-----------------'
        if comclu.vcount() > 1:
            nonsingle += 1
        tag_weight = {}
        for v in comclu.vs:
            if v['weight'] > 5:
                hash_com[v['name']] = index
            tag_weight[v['name']] = v['weight']
            count = com_size.get(index, 0)
            com_size[index] = v['weight'] + count
        sort_list = list(sorted(tag_weight, key=tag_weight.get, reverse=True))
        for key in sort_list[:min(len(sort_list), len(sort_list))]:
            print key, tag_weight[key]
        print '-------------Community size: ', com_size[index], '---------------------'
        print
        index += 1
    # print len(hash_com)
    # print len(set(hash_com.values()))
    # print set(hash_com.values())
    print '------------------all size:', sum(com_size.values()), '---------------------'
    print '------------------non single clusters:', nonsingle, '---------------------'

    return hash_com, com_size


def tag_jaccard(dbname, hash_time, gfilename):
    # Calculate the jaccard index of hashtag
    g = gt.Graph.Read_GraphML(gfilename+'_tag_undir.graphml')
    times = dbt.db_connect_col(dbname, hash_time)
    tag_tweets = {}
    for tweet in times.find({'$where': 'this.entities.hashtags.length>0'}):
        hashtags = tweet['entities']['hashtags']
        hash_set = set()
        for hash in hashtags:
            hash_set.add(hash['text'].encode('utf-8').lower().replace('_', '').replace('-', ''))
        for hash in hash_set:
            ids = tag_tweets.get(hash, set())
            ids.add(tweet['id'])
            tag_tweets[hash] = ids
    pickle.dump(tag_tweets, open(gfilename+'.pick', 'w'))

    g.es['jaccard'] = 0.0
    for edge in g.es:
        source_vertex_id = edge.source
        target_vertex_id = edge.target
        source_name = g.vs[source_vertex_id]['name']
        target_name = g.vs[target_vertex_id]['name']
        source_set, target_set = tag_tweets.get(source_name), tag_tweets.get(target_name)
        edge['jaccard'] = float(len(source_set.intersection(target_set)))/len(source_set.union(target_set))
    g.write_graphml(gfilename+'_tag_undir_jarccard.graphml')




def user_hashtag_profile(tag_net, users):
    '''
    Map the hashtags that a user has used to communities of hashtag network
    Get the <commnity: proportion> vector for users' hashtag profiles
    :param dbname:
    :param hash_com:
    :return:
    '''

    # Cluster tag network
    gt.summary(tag_net)
    gc = gt.giant_component(tag_net)
    gt.summary(gc)
    com = gc.community_infomap(edge_weights='weight', vertex_weights='weight')
    comclus = com.subgraphs()
    print 'Community stats: #communities, modularity', len(comclus), com.modularity
    index = 0
    hash_com = {}
    for comclu in comclus:
        # filter single-node communities
        if len(comclu.vs) > 1:
            for v in comclu.vs:
                hash_com[v['name']] = index
            index += 1
    pickle.dump(hash_com, open('hash_com.pick', 'w'))

    hash_com = pickle.load(open('hash_com.pick', 'r'))
    com_length = len(set(hash_com.values()))
    print com_length
    # Count tag usages

    times = dbt.db_connect_col('fed', 'ed_tag')
    user_hash_profile = {}
    for uid in users:
        vector = [0.0]*com_length
        for tweet in times.find({'user.id': int(uid), '$where': 'this.entities.hashtags.length>0'}):
            hashtags = tweet['entities']['hashtags']
            for hash in hashtags:
                tag = hash['text'].encode('utf-8').lower().replace('_', '').replace('-', '')
                com_id = hash_com.get(tag, -1)
                if com_id > -1:
                    vector[com_id] += 1
        # print vector
        if sum(vector) == 0:
            user_hash_profile[uid] = np.array(vector)
        else:
            user_hash_profile[uid] = np.array(vector)/sum(vector)

    pickle.dump(user_hash_profile, open('data/user-hash-profile.pick', 'w'))


def label_ed_recovery(hash_com, com_size, idx=[18, 102]):
    # select users in prorec that have more ed-related hashtags
    times = dbt.db_connect_col('fed', 'prorec_tag')
    com = dbt.db_connect_col('fed', 'tag_com')
    threshold = float(sum([com_size[i] for i in idx]))/sum(com_size.values())
    print 'threshold: ', threshold
    users = list(set(iot.get_values_one_field('fed', 'prorec_tag', 'user.id')))
    for uid in users:
        taget_count, all_count = 0.0, 0.0
        for tweet in times.find({'user.id': uid}):
            hashtags = tweet['entities']['hashtags']
            hash_set = set()
            for hash in hashtags:
                # need no .encode('utf-8')
                hash_set.add(hash['text'].encode('utf-8').lower().replace('_', '').replace('-', ''))
            for tag in hash_set:
                com_id = hash_com.get(tag, -1)
                if com_id > -1:
                    all_count += 1
                    if com_id in idx:
                        taget_count += 1

        if all_count and taget_count/all_count > threshold:
            com.update({'id': uid}, {'$set': {'rec_tageted': True}}, upsert=False)


def refine_recovery_tweets(hash_com, tagcol, refine_tagcol, idx=[4, 58]): # without non-recovery: 18, 102, 4, 58, 88
    # select tweets have ed-related hashtags
    times = dbt.db_connect_col('fed', tagcol)
    rec_refine = dbt.db_connect_col('fed', refine_tagcol)
    rec_refine.create_index([('user.id', pymongo.ASCENDING),
                          ('id', pymongo.DESCENDING)])
    rec_refine.create_index([('id', pymongo.ASCENDING)], unique=True)
    for tweet in times.find():
        hashtags = tweet['entities']['hashtags']
        for hash in hashtags:
            # need no .encode('utf-8')
            tag = hash['text'].encode('utf-8').lower().replace('_', '').replace('-', '')
            com_id = hash_com.get(tag, -1)
            if com_id > -1:
                if com_id in idx:
                    try:
                        rec_refine.insert(tweet)
                    except pymongo.errors.DuplicateKeyError:
                        pass



def remove_nan():
    user_hash_profile = pickle.load(open('data/user-hash-profile.pick', 'r'))
    for uid in user_hash_profile:
        prof = user_hash_profile[uid]
        prof[np.isnan(prof)] = 0.0
        user_hash_profile[uid] = prof
    pickle.dump(user_hash_profile, open('data/user-hash-profile.pick', 'w'))


def user_cluster_hashtag(filepath):
    '''
    Cluster users based on the profiles of hashtag preference
    :return:
    '''
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score, calinski_harabaz_score
    from sklearn.datasets import load_svmlight_file
    from sklearn import preprocessing
    # from sklearn.datasets import load_iris
    # Based on hashtag community proportation profiles
    user_hash_profile = pickle.load(open('data/user-hash-profile.pick', 'r'))
    X = np.array(user_hash_profile.values())
    # Based on LIWC feature
    # X, y = load_svmlight_file(filepath)
    # X = X.toarray()[:, 17:]
    # scaler = preprocessing.StandardScaler().fit(X)
    # X = scaler.transform(X)

    print X.shape
    print X

    '''Select the best K for K-means'''
    # range_n_clusters = range(2, 21)
    # data = []
    # for n_clusters in range_n_clusters:
    #     clusterer = KMeans(n_clusters=n_clusters)
    #     cluster_labels = clusterer.fit_predict(X)
    #     silhouette_avg = silhouette_score(X, cluster_labels)
    #     print("For n_clusters =", n_clusters, "The average silhouette_score is :", silhouette_avg)
    #     data.append([n_clusters, silhouette_avg])
    # df = pd.DataFrame(data, columns=['cluster', 'silhouette_avg'])
    # df.to_csv('user-kmeans-hashtag.csv')

    '''Single run kmeans'''
    clusterer = KMeans(n_clusters=2)
    cluster_labels = clusterer.fit_predict(X)
    return cluster_labels, user_hash_profile.keys()

    # dictionary = dict(zip(user_hash_profile.keys(), cluster_labels))

    # print 'Follow network'
    # net = gt.load_network('fed', 'snet')
    # gt.net_stat(net)
    # cluster_assort(dictionary, net)
    # print 'Retweet network'
    # net = gt.load_beh_network('fed', 'sbnet', 'retweet')
    # gt.net_stat(net)
    # cluster_assort(dictionary, net)
    # print 'Reply network'
    # net = gt.load_beh_network('fed', 'sbnet', 'reply')
    # gt.net_stat(net)
    # cluster_assort(dictionary, net)
    # print 'Mention network'
    # net = gt.load_beh_network('fed', 'sbnet', 'mention')
    # gt.net_stat(net)
    # cluster_assort(dictionary, net)



def cluster_assort(dictionary, net):
    for key in dictionary.keys():
        exist = True
        try:
            v = net.vs.find(name=str(key))
        except ValueError:
            exist = False
        if exist:
            v['cluster'] = dictionary[key]
    net.write_graphml('ed_follow_cluster.graphml')
    raw_assort = net.assortativity('cluster', 'cluster', directed=True)
    print '%.3f' %raw_assort


def friend_network_hashtag_weight(dbname, netname):
    '''
    Community detection on friendship network, weighted by hashtag similarity
    :param dbname:
    :param netname:
    :param user_hash_profile:
    :return:
    '''
    user_hash_profile = pickle.load(open('data/user-hash-profile.pick', 'r'))
    net = gt.load_network(dbname, netname)
    fields = iot.read_fields()
    com = dbt.db_connect_col(dbname, 'scom')
    for edge in net.es:
        source_vertex_id = edge.source
        target_vertex_id = edge.target
        source_uid = int(net.vs[source_vertex_id]['name'])
        target_uid = int(net.vs[target_vertex_id]['name'])
        source_user = com.find_one({'id':source_uid})
        target_user = com.find_one({'id':target_uid})
        source_user_liwc = iot.get_fields_one_doc(source_user, fields)
        target_user_liwc = iot.get_fields_one_doc(target_user, fields)
        source_user_liwc.extend(user_hash_profile[source_uid])
        target_user_liwc.extend(user_hash_profile[target_uid])
        print len(target_user_liwc)
        dis = spatial.distance.euclidean(source_user_liwc, target_user_liwc)
        edge['weight'] = 1.0/(1.0 + dis)
    net.write_graphml('ed_weighted_follow.graphml')


def friend_community():
    net = gt.Graph.Read_GraphML('ed_weighted_follow.graphml')
    # net = gt.load_network('fed', 'snet')
    gt.net_stat(net)
    com = net.community_infomap(edge_weights='weight')
    comclus = com.subgraphs()
    print len(comclus), com.modularity
    com = dbt.db_connect_col('fed', 'scom')
    index = 0
    hash_com = {}
    for comclu in comclus:
        print '============================================================'
        # if comclu.vcount() > 10:
        for v in comclu.vs:
            user = com.find_one({'id': int(v['name'])})
            print v['name'], user['id'], user['screen_name'], ' '.join(user['description'].split()).encode('utf-8')
            hash_com[v['name']] = index
        index += 1

def insert_cluster_tweets(dbname, timename, cluster):
    # insert tweets of different clusters into two database collections
    time = dbt.db_connect_col(dbname, timename)
    time.create_index([('user.id', pymongo.ASCENDING),
                          ('id', pymongo.DESCENDING)])
    time.create_index([('id', pymongo.ASCENDING)], unique=True)

    ed_tweet = dbt.db_connect_col(dbname, 'ed_tag')
    for uid in cluster:
        for tweet in ed_tweet.find({'user.id':int(uid)}):
            try:
                time.insert(tweet)
            except pymongo.errors.DuplicateKeyError:
                pass

def tags_two_user_moduls():
    #load network from gephi output
    g = gt.Graph.Read_GraphML('communication-3-moduls.graphml')
    cluster0, cluster1, cluster2 = set(), set(), set()
    for v in g.vs:
        if v['Modularity Class'] == 0:
            cluster0.add(int(v['name']))
        elif v['Modularity Class'] == 1:
            cluster1.add(int(v['name']))
        elif v['Modularity Class'] == 2:
            cluster2.add(int(v['name']))
    g = gt.load_hashtag_coocurrent_network_undir('fed', 'ed_tag', list(cluster0))
    gt.summary(g)
    filename = 'communication_fed_cluster0'
    g.write_graphml(filename+'_tag_undir.graphml')

    g = gt.load_hashtag_coocurrent_network_undir('fed', 'ed_tag', list(cluster1))
    gt.summary(g)
    filename = 'communication__fed_cluster1'
    g.write_graphml(filename+'_tag_undir.graphml')

    g = gt.load_hashtag_coocurrent_network_undir('fed', 'ed_tag', list(cluster2))
    gt.summary(g)
    filename = 'communication_fed_cluster2'
    g.write_graphml(filename+'_tag_undir.graphml')


def tags_user_cluster(graph_file_path, filename):
    # put tweet of two cluster into two set
    g = gt.Graph.Read_GraphML(graph_file_path)
    # g_mention = gt.Graph.Read_GraphML('ed-communication'+'-hashtag-only-fed-cluster.graphml')
    gt.summary(g)
    # gt.summary(g_mention)

    # for i in range(2):
    #     g = [g_retweet, g_mention][i]
    cluster0, cluster1, cluster2 = set(), set(), set()
    for v in g.vs:
        if v['cluster'] == 0:
            cluster0.add(int(v['name']))
        elif v['cluster'] == 1:
            cluster1.add(int(v['name']))
        elif v['cluster'] == -1:
            cluster2.add(int(v['name']))
    print 'cluster size;', len(cluster0)
    g = gt.load_hashtag_coocurrent_network_undir('fed', 'timeline', list(cluster0))
    gt.summary(g)
    # filename = ['ed_retweet', 'ed_communication'][i] + '_fed_cluster0'
    vs = g.vs(weight_gt=3, user_gt=3)
    g = g.subgraph(vs)
    gt.summary(g)
    g.write_graphml(filename+'_alltag_undir_cluster0.graphml')

    print 'cluster size;', len(cluster1)
    g = gt.load_hashtag_coocurrent_network_undir('fed', 'timeline', list(cluster1))
    gt.summary(g)
    # filename = ['ed_retweet', 'ed_communication'][i] + '_fed_cluster1'
    vs = g.vs(weight_gt=3, user_gt=3)
    g = g.subgraph(vs)
    gt.summary(g)
    g.write_graphml(filename+'_alltag_undir_cluster1.graphml')

    print 'cluster size;', len(cluster2)
    g = gt.load_hashtag_coocurrent_network_undir('fed', 'timeline', list(cluster2))
    gt.summary(g)
    vs = g.vs(weight_gt=3, user_gt=3)
    g = g.subgraph(vs)
    gt.summary(g)
    # filename = ['ed_retweet', 'ed_communication'][i] + '_fed_cluster1'
    g.write_graphml(filename+'_alltag_undir_cluster2.graphml')

    # insert_cluster_tweets('fed', 'mention-cluster0', list(cluster0))
    # insert_cluster_tweets('fed', 'mention-cluster1', cluster1)


def tfidf_tag_cluster(btype= 'retweet'):
    # Calculate the TFIDF of tags in two clusters
    cluster0 = gt.Graph.Read_GraphML('ed_'+btype+'_fed_cluster0_tag_undir.graphml')
    cluster1 = gt.Graph.Read_GraphML('ed_'+btype+'_fed_cluster1_tag_undir.graphml')

    gt.summary(cluster0)
    vs = cluster0.vs(weight_gt=3, user_gt=3)
    cluster0 = cluster0.subgraph(vs)
    cluster0 = gt.giant_component(cluster0)
    gt.summary(cluster0)

    gt.summary(cluster1)
    vs = cluster1.vs(weight_gt=3, user_gt=3)
    cluster1 = cluster1.subgraph(vs)
    cluster1 = gt.giant_component(cluster1)
    gt.summary(cluster1)

    for v in cluster0.vs:
        exist = True
        count_ov = 0.0
        try:
            ov = cluster1.vs.find(name=v['name'])
        except ValueError:
            exist = False
        if exist:
            count_ov = ov['weight']
        v['tfidf'] = float(v['weight'])/(v['weight']+count_ov)
    for v in cluster1.vs:
        exist = True
        count_ov = 0.0
        try:
            ov = cluster0.vs.find(name=v['name'])
        except ValueError:
            exist = False
        if exist:
            count_ov = ov['weight']
        v['tfidf'] = float(v['weight'])/(v['weight']+count_ov)
    cluster0.write_graphml('ed_'+btype+'_fed_cluster0_tfidf_tag_undir.graphml')
    cluster1.write_graphml('ed_'+btype+'_fed_cluster1_tfidf_tag_undir.graphml')




def pmi(g, filename=None):
    '''
    Calculate the PMI weight for edges
    :param g:
    :param filename:
    :return:
    '''
    # print g.is_loop()
    vw_sum = sum(g.vs["weight"])
    for edge in g.es:
        source_vertex_id = edge.source
        target_vertex_id = edge.target
        source_vertex = g.vs[source_vertex_id]
        target_vertex = g.vs[target_vertex_id]
        ew = edge['weight']
        edge['pmi'] = max(np.log2(float(ew*vw_sum)/(source_vertex['weight']*target_vertex['weight'])), 0)
    # pickle.dump(g, open('data/'+filename+'_pmi_tag.pick', 'w'))
    # g = pickle.load(open('data/'+filename+'_pmi_tag.pick', 'r'))
    # pdf(g.es['weight'])
    # plot_graph(g, 'ed-hashtag')
    g.write_graphml(filename+'_pmi.graphml')
    # g.es['weight'] = g.es['pmi']
    return g


# def plot_graph(filename):
#     g = gta.load_graph(filename)
#     age = g.vertex_properties["weight"]
#
#     pos = gta.sfdp_layout(g)
#     gta.graph_draw(g, pos, output_size=(1000, 1000), vertex_color=[1,1,1,0],
#                vertex_fill_color=age, vertex_size=1, edge_pen_width=1.2,
#                vcmap=matplotlib.cm.gist_heat_r, output="hashtag.pdf")

if __name__ == '__main__':

    # # pall = tag_record('fed', 'pall_tag', 'pall')
    # # rec = tag_record('fed', 'prorec_tag', 'prorec')
    # # ped = tag_record('fed', 'proed_tag', 'proed')
    # # target_comms = community_net(rec, ped)
    # # print target_comms
    # # transform('ed_tag')
    core = gt.Graph.Read_GraphML('alled_tag_undir_filter.graphml')
    pmi(core, 'alled_tag_undir_filter')
    #
    # # communication = gt.Graph.Read_GraphML('communication-only-fed-filter.graphml')
    #
    # # # # hash_com_all, com_size_all = community(pall)
    # hash_com_rec, com_size_rec = community(core)
    # # # hash_com_ped, com_size_ped = community(ped)
    # # label_ed_recovery(hash_com_rec, com_size_rec)
    # # refine_recovery_tweets(hash_com_rec, 'prorec_tag', 'prorec_tag_refine', [4, 39, 58])
    # # refine_recovery_tweets(hash_com_ped, 'proed_tag', 'proed_tag_refine', [0, 1, 2])


    # tag_jaccard('fed', 'prorec_tag', 'prorec')
    # tag_jaccard('fed', 'proed_tag', 'proed')

    # #-----------------------Filter network-----------------------------------------------
    # # # users = iot.get_values_one_field('fed', 'scom', 'id')
    '''directed network'''
    # g = gt.load_hashtag_coocurrent_network('fed', 'ed_tag')
    # g.write_graphml('alled_tag.graphml')
    # # g = gt.Graph.Read_GraphML('core_ed_tag_undir.graphml')
    # gt.summary(g)
    # nodes = g.vs.select(weight_gt=3)
    # print 'Filtered nodes: %d' %len(nodes)
    # g = g.subgraph(nodes)
    # nodes = g.vs.select(user_gt=3)
    # print 'Filtered nodes: %d' %len(nodes)
    # g = g.subgraph(nodes)
    # # g = pmi(g)
    # g.write_graphml('alled_tag_filter.graphml')

    '''undirected network'''
    # g = gt.load_hashtag_coocurrent_network_undir('fed', 'ed_tag')
    # g.write_graphml('alled_tag_undir.graphml')
    # # g = gt.Graph.Read_GraphML('core_ed_tag_undir.graphml')
    # gt.summary(g)
    # nodes = g.vs.select(weight_gt=3)
    # print 'Filtered nodes: %d' %len(nodes)
    # g = g.subgraph(nodes)
    # nodes = g.vs.select(user_gt=3)
    # print 'Filtered nodes: %d' %len(nodes)
    # g = g.subgraph(nodes)
    # g.write_graphml('alled_tag_undir_filter.graphml')

    #-----------------------Filter network-----------------------------------------------

    #-----------------------Community detection-----------------------------------------------
    # g = gt.Graph.Read_GraphML('core_ed_hashtag_filter.graphml')
    # g = gt.giant_component(g)
    # gt.summary(g)
    # infor = g.community_infomap(edge_weights='weight', vertex_weights='weight')
    # print len(set(infor.membership))
    # print infor.modularity
    #
    # import louvain
    # part = louvain.find_partition(g, method='Modularity', weight='weight')
    # print len(set(part.membership)), part.modularity




    # pmi(g, filename='ed')
    # friend_network_hashtag_weight('fed', 'snet')
    # friend_community()
    # plot_graph('ed_tag.graphml')

    #-------------------------------------------------------------------------
    '''cluster user Kmeans'''
    # user_cluster_hashtag('ed-communication.data')

    #-------------------------------------------------------------------------


    #-------------------------------------------------------------------------
    '''hashtags network of differnet clusters'''
    # tags_user_cluster('communication-only-fed-filter-cluster.graphml', 'communication-only-fed-filter-cluster')
    #-------------------------------------------------------------------------

    # community_vis('ed', 'info')
    # community_vis('ed', 'ml')
    # compare_direct_undir()

    # hashtag_filter('ed')
    # g = gt.Graph.Read_GraphML('ed'+'_tag_undir.graphml')
    # com = g.community_multilevel(weights='weight', return_levels=False)
    # print com.modularity
    # com = g.community_infomap(edge_weights='weight', vertex_weights='weight')
    # print com.modularity

    # depress = tag_record('fed', 'timeline', 'fed')
    # hash_com_all, com_size_all = community(gt.Graph.Read_GraphML('alled_tag_undir.graphml'))
    #


    # tags_user_cluster()
    # tags_two_user_moduls()
    # tfidf_tag_cluster('retweet')
    # tfidf_tag_cluster('communication')



    # transform('communication-only-fed-filter')


    #----------------------------------------------------------------------------------------------
    '''User's hashtag profile'''

    # core = gt.Graph.Read_GraphML('alled_tag_filter.graphml')
    # gt.summary(core)
    # communication = gt.Graph.Read_GraphML('communication-only-fed-filter.graphml')
    # gt.summary(communication)
    # communication = gt.giant_component(communication)
    # gt.summary(communication)
    # users = [(v['name']) for v in communication.vs]
    # print len(users)
    # user_hashtag_profile(core, users)

    #----------------------------------------------------------------------------------------------
