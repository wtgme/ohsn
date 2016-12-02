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

def pdf(data):
    pll.plot_pdf_mul_data([data], ['Edge Weight'], ['r'], ['o'], labels=['Edge Weight'],
                          linear_bins=False, central=False, fit=True, fitranges=[(1, 10000)])

def tag_record(dbname, colname, filename):
    # ed_users = iot.get_values_one_field(dbname, 'scom', 'id')
    # print len(ed_users)
    # g = gt.load_hashtag_coocurrent_network(dbname, colname)
    # pickle.dump(g, open('data/'+filename+'_tag.pick', 'w'))
    g = pickle.load(open('data/'+filename+'_tag.pick', 'r'))
    gt.net_stat(g)
    g.write_graphml(filename+'_tag.graphml')
    nodes = g.vs.select(weight_gt=3)
    print 'Filtered nodes: %d' %len(nodes)
    g = g.subgraph(nodes)
    nodes = g.vs.select(user_gt=3)
    print 'Filtered nodes: %d' %len(nodes)
    g = g.subgraph(nodes)
    # gt.net_stat(g)
    # edges = g.es.select(weight_gt=3)
    # print 'Filtered edges: %d' %len(edges)
    # g = g.subgraph_edges(edges)
    # edges = g.es.select(weight_gt=1)
    # print len(edges)
    gt.net_stat(g)
    # g.write_graphml(filename+'_tag.graphml')
    # plot_graph(g, 'ed-hashtag')
    return g


def plot_graph(g, filename):
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


def community(g=None):
    '''
    Detect communities in the co-occurrence network of hashtag
    Use InfoMap to detect communities
    Only select communities whose sizes are larger than a threshold
    :param g:
    :return:
    '''
    g = gt.Graph.Read_GraphML('ed_tag.graphml')
    gc = gt.giant_component(g)
    com = gc.community_infomap(edge_weights='weight', vertex_weights='weight')
    comclus = com.subgraphs()
    print len(comclus), com.modularity
    index = 0
    hash_com = {}
    for comclu in comclus:
        if comclu.vcount() > 10:
        #     print 'Com', index, '==================================='
        # else:
        #     print '==================================='
            tag_weight = {}
            for v in comclu.vs:
                hash_com[v['name']] = index
                tag_weight[v['name']] = v['weight']
            index += 1
            sort_list = list(sorted(tag_weight, key=tag_weight.get, reverse=True))
            for key in sort_list:
                print key, tag_weight[key]
    print len(hash_com)
    print len(set(hash_com.values()))
    print set(hash_com.values())
    return hash_com


def user_hashtag_profile(dbname, hash_com):
    '''
    Map the hashtags that a user has used to communities of hashtag network
    Get the <commnity: proportion> vector for users' hashtag profiles
    :param dbname:
    :param hash_com:
    :return:
    '''
    ed_users = iot.get_values_one_field(dbname, 'scom', 'id')
    db = dbt.db_connect_no_auth(dbname)
    com_length = len(set(hash_com.values()))
    times = db['timeline']
    user_hash_profile = {}
    for uid in ed_users:
        counter = {}
        for tweet in times.find({'user.id': uid, '$where': 'this.entities.hashtags.length>0'}):
            hashtags = tweet['entities']['hashtags']
            hash_set = set()
            for hash in hashtags:
                hash_set.add(hash['text'].encode('utf-8').lower().replace('_', '').replace('-', ''))
            hash_list = list(hash_set)
            for hash in hash_list:
                v = counter.get(hash, 0)
                counter[hash] = v+1
        vector = [0.0]*com_length
        for hash in counter:
            if hash in hash_com:
                comid = hash_com[hash]
                vector[comid] += counter[hash]
        if sum(vector) == 0:
            user_hash_profile[uid] = np.array(vector)
        else:
            user_hash_profile[uid] = np.array(vector)/sum(vector)

    pickle.dump(user_hash_profile, open('data/user-hash-profile.pick', 'w'))


def remove_nan():
    user_hash_profile = pickle.load(open('data/user-hash-profile.pick', 'r'))
    for uid in user_hash_profile:
        prof = user_hash_profile[uid]
        prof[np.isnan(prof)] = 0.0
        user_hash_profile[uid] = prof
    pickle.dump(user_hash_profile, open('data/user-hash-profile.pick', 'w'))


def user_cluster_hashtag():
    '''
    Cluster users based on the profiles of hashtag preference
    :return:
    '''
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score
    user_hash_profile = pickle.load(open('data/user-hash-profile.pick', 'r'))
    X = np.array(user_hash_profile.values())
    print X.shape

    '''Select the best K for K-means'''
    # range_n_clusters = range(2, 21)
    # values = []
    # for n_clusters in range_n_clusters:
    #     clusterer = KMeans(n_clusters=n_clusters, random_state=10)
    #     cluster_labels = clusterer.fit_predict(X)
    #     silhouette_avg = silhouette_score(X, cluster_labels)
    #     print("For n_clusters =", n_clusters, "The average silhouette_score is :", silhouette_avg)
    #     values.append(silhouette_avg)
    # print values
    # print range_n_clusters

    clusterer = KMeans(n_clusters=2, random_state=10)
    cluster_labels = clusterer.fit_predict(X)
    dictionary = dict(zip(user_hash_profile.keys(), cluster_labels))

    print 'Follow network'
    net = gt.load_network('fed', 'snet')
    gt.net_stat(net)
    cluster_assort(dictionary, net)
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


def pmi(g, filename):
    '''
    Calculate the PMI weight for edges
    :param g:
    :param filename:
    :return:
    '''
    print g.is_loop()
    vw_sum = sum(g.vs["weight"])
    for edge in g.es:
        source_vertex_id = edge.source
        target_vertex_id = edge.target
        source_vertex = g.vs[source_vertex_id]
        target_vertex = g.vs[target_vertex_id]
        ew = edge['weight']
        edge['pmi'] = np.log(float(ew*vw_sum)/(source_vertex['weight']*target_vertex['weight']))
    # pickle.dump(g, open('data/'+filename+'_pmi_tag.pick', 'w'))
    # g = pickle.load(open('data/'+filename+'_pmi_tag.pick', 'r'))
    # pdf(g.es['weight'])
    # plot_graph(g, 'ed-hashtag')
    g.write_graphml(filename+'_pmi_tag.graphml')


# def plot_graph(filename):
#     g = gta.load_graph(filename)
#     age = g.vertex_properties["weight"]
#
#     pos = gta.sfdp_layout(g)
#     gta.graph_draw(g, pos, output_size=(1000, 1000), vertex_color=[1,1,1,0],
#                vertex_fill_color=age, vertex_size=1, edge_pen_width=1.2,
#                vcmap=matplotlib.cm.gist_heat_r, output="hashtag.pdf")

if __name__ == '__main__':
    g = tag_record('fed', 'timeline', 'ed')
    # hash_com = community()
    # user_hashtag_profile('fed', hash_com)
    # pmi(g, filename='ed')
    # friend_network_hashtag_weight('fed', 'snet')
    # friend_community()
    # plot_graph('ed_tag.graphml')

    # user_cluster_hashtag()
