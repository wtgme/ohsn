# -*- coding: utf-8 -*-
"""
Created on 20:05, 07/04/16

@author: wt
"""

from igraph import *
import db_util as dbt
from random import randint
import numpy as np
import powerlaw_fit


def load_network_ian(dbname, collection='None'):
    # load network from Ian' data
    # Edge: Follower ---------> Followee
    com = dbt.db_connect_col(dbname, collection)
    name_map, edges = {}, set()
    for row in com.find({}, no_cursor_timeout=True):
        ego = str(row['id'])
        # print ego
        egoid = name_map.get(ego, len(name_map))
        name_map[ego] = egoid
        if 'followData' in row:
            friends = row['followData']
            if 'friends' in friends:
                for followee in friends['friends']:
                    followee = str(followee)
                    followeeid = name_map.get(followee, len(name_map))
                    name_map[followee] = followeeid
                    edges.add((egoid, followeeid))
            if 'followers' in friends:
                for follower in friends['followers']:
                    follower = str(follower)
                    followerid = name_map.get(follower, len(name_map))
                    name_map[follower] = followerid
                    edges.add((followerid, egoid))
    # print len(name_map), len(edges)
    g = Graph(len(name_map), directed=True)
    g.vs["name"] = list(sorted(name_map, key=name_map.get))
    g.add_edges(list(edges))
    g.es["weight"] = 1
    return g


def load_network(db_name, collection='None'):
    '''
    Friendship network: directed network
    Edge: Follower ---------> Followee
    '''
    if collection is 'None':
        cols = db_name
    else:
        db = dbt.db_connect_no_auth(db_name)
        cols = db[collection]
    name_map, edges = {}, set()
    for row in cols.find({},no_cursor_timeout=True):
        n1 = str(row['follower'])
        n2 = str(row['user'])
        n1id = name_map.get(n1, len(name_map))
        name_map[n1] = n1id
        n2id = name_map.get(n2, len(name_map))
        name_map[n2] = n2id
        edges.add((n1id, n2id))
    g = Graph(len(name_map), directed=True)
    g.vs["name"] = list(sorted(name_map, key=name_map.get))
    g.add_edges(list(edges))
    g.es["weight"] = 1
    return g


def load_network_subset(db_name, collection='None', filter={}):
    '''
    Friendship network: directed network from a user list
    Edge: Follower---------> Followee
    '''
    if collection is 'None':
        cols = db_name
    else:
        db = dbt.db_connect_no_auth(db_name)
        cols = db[collection]
    name_map, edges = {}, set()
    # filter['user'] = {'$in': uset_list}
    # filter['follower'] = {'$in': uset_list}
    for row in cols.find(filter, no_cursor_timeout=True):
        n1 = str(row['follower'])
        n2 = str(row['user'])

        n1id = name_map.get(n1, len(name_map))
        name_map[n1] = n1id
        n2id = name_map.get(n2, len(name_map))
        name_map[n2] = n2id
        edges.add((n1id, n2id))
    g = Graph(len(name_map), directed=True)
    g.vs["name"] = list(sorted(name_map, key=name_map.get))
    g.add_edges(list(edges))
    g.es["weight"] = 1
    return g


def load_beh_network_filter(db_name, collection, btype, filter={}):
    '''
    only interaction among poi
    behavior network: directed weighted network
    Tweet: 0
    Retweet: 1;
    Reply: 2;
    Direct Mention: 3;
    undirect mention: 4
    Reply and mention Edge: u0 -----------> u1
    Retweet Edge: u1 ----------> u0
    '''
    btype_dic = {'retweet': [1],
                 'reply': [2],
                 'mention': [3],
                 'communication': [2, 3],
                 'all': [1, 2, 3]}
    if collection is 'None':
        cols = db_name
    else:
        db = dbt.db_connect_no_auth(db_name)
        cols = db[collection]
    name_map, edges = {}, {}
    filter['type'] = {'$in': btype_dic[btype]}
    for row in cols.find(filter, no_cursor_timeout=True):
        n1 = str(row['id0'])
        n2 = str(row['id1'])
        # print n1, n2
        if n1 != n2:
            n1id = name_map.get(n1, len(name_map))
            name_map[n1] = n1id
            n2id = name_map.get(n2, len(name_map))
            name_map[n2] = n2id
            wt = edges.get((n1id, n2id), 0)
            edges[(n1id, n2id)] = wt + 1
    g = Graph(len(name_map), directed=True)
    g.vs["name"] = list(sorted(name_map, key=name_map.get))
    # If items(), keys(), values(), iteritems(), iterkeys(), and itervalues() are called with no intervening modifications to the dictionary, the lists will directly correspond.
    # http://stackoverflow.com/questions/835092/python-dictionary-are-keys-and-values-always-the-same-order
    g.add_edges(edges.keys())
    g.es["weight"] = edges.values()
    return g



def load_beh_network_subset(userlist, db_name, collection='None', btype='communication', tag=None):
    '''
    only interaction among poi
    behavior network: directed weighted network
    Tweet: 0
    Retweet: 1;
    Reply: 2;
    Direct Mention: 3;
    undirect mention: 4
    Reply and mention Edge: u0 -----------> u1
    Retweet Edge: u1 ----------> u0
    '''
    btype_dic = {'retweet': [1],
                 'reply': [2],
                 'mention': [3],
                 'communication': [2, 3],
                 'all': [1, 2, 3]}
    if collection is 'None':
        cols = db_name
    else:
        db = dbt.db_connect_no_auth(db_name)
        cols = db[collection]
    name_map, edges = {}, {}
    filter = {}
    filter['type'] = {'$in': btype_dic[btype]}
    filter['id0'] = {'$in': userlist}
    filter['id1'] = {'$in': userlist}
    if tag:
        filter['tags'] = {'$in': tag}
    # for row in cols.find({}):
    for row in cols.find(filter, no_cursor_timeout=True):
        n1 = str(row['id0'])
        n2 = str(row['id1'])
        if n1 != n2:
            n1id = name_map.get(n1, len(name_map))
            name_map[n1] = n1id
            n2id = name_map.get(n2, len(name_map))
            name_map[n2] = n2id
            wt = edges.get((n1id, n2id), 0)
            edges[(n1id, n2id)] = wt + 1
    g = Graph(len(name_map), directed=True)
    g.vs["name"] = list(sorted(name_map, key=name_map.get))
    # If items(), keys(), values(), iteritems(), iterkeys(), and itervalues() are called with no intervening modifications to the dictionary, the lists will directly correspond.
    # http://stackoverflow.com/questions/835092/python-dictionary-are-keys-and-values-always-the-same-order
    g.add_edges(edges.keys())
    g.es["weight"] = edges.values()
    return g


def load_beh_network(db_name, collection='None', btype='communication'):
    '''
    All interctions of a user
    behavior network: directed weighted network
    Tweet: 0
    Retweet: 1;
    Reply: 2;
    Direct Mention: 3;
    undirect mention: 4
    Reply and mention Edge: u0 -----------> u1
    Retweet Edge: u1 ----------> u0
    '''
    btype_dic = {'retweet': [1], 'reply': [2], 'mention': [3], 'communication': [2, 3]}
    if collection is 'None':
        cols = db_name
    else:
        db = dbt.db_connect_no_auth(db_name)
        cols = db[collection]
    name_map, edges = {}, {}
    # for row in cols.find({}):
    for row in cols.find({'type': {'$in': btype_dic[btype]}}, no_cursor_timeout=True):
        n1 = str(row['id0'])
        n2 = str(row['id1'])
        if n1 != n2:
            n1id = name_map.get(n1, len(name_map))
            name_map[n1] = n1id
            n2id = name_map.get(n2, len(name_map))
            name_map[n2] = n2id
            wt = edges.get((n1id, n2id), 0)
            edges[(n1id, n2id)] = wt + 1
    g = Graph(len(name_map), directed=True)
    g.vs["name"] = list(sorted(name_map, key=name_map.get))
    g.add_edges(edges.keys())
    g.es["weight"] = edges.values()
    return g


def load_user_hashtag_network(db_name, collection='None'):
    '''
    User-Hashtag network: weighted directed network
    Edge: user---------> hashtag
    '''
    if collection is 'None':
        cols = db_name
    else:
        db = dbt.db_connect_no_auth(db_name)
        cols = db[collection]
    name_map, edges = {}, {}
    for row in cols.find({'$where': "this.entities.hashtags.length>0"}, no_cursor_timeout=True):
        n1 = row['user']['id_str']
        hashtags = row['entities']['hashtags']
        hash_set = set()
        for hash in hashtags:
            # need no .encode('utf-8')
            hash_set.add(hash['text'].encode('utf-8').lower().replace('_', '').replace('-', ''))
        for n2 in hash_set:
            n1id = name_map.get(n1, len(name_map))
            name_map[n1] = n1id
            n2id = name_map.get(n2, len(name_map))
            name_map[n2] = n2id
            wt = edges.get((n1id, n2id), 0)
            edges[(n1id, n2id)] = wt + 1
    g = Graph(len(name_map), directed=True)
    #get key list of dict according to value ranking
    g.vs["name"] = list(sorted(name_map, key=name_map.get))
    g.add_edges(edges.keys())
    g.es["weight"] = edges.values()
    return g


def load_hashtag_coocurrent_network(db_name, collection='None', uids=[]):
    '''
    Hashtag Co-occurrence Network: weighted directed network
    Edge: Hashtag --------- Hashtag
    '''
    if collection is 'None':
        cols = db_name
    else:
        db = dbt.db_connect_no_auth(db_name)
        cols = db[collection]
    name_map, edges, node_weight = {}, {}, {}
    filter = {}
    tag_user = {}
    if len(uids) > 0:
        filter['user.id'] = {'$in': uids}
    filter['$where'] = 'this.entities.hashtags.length>0'
    for row in cols.find(filter, no_cursor_timeout=True):
        # if 'retweeted_status' in row:
        #     continue
        hashtags = row['entities']['hashtags']
        hash_set = set()
        for hash in hashtags:
            # need no .encode('utf-8')
            hash_set.add(hash['text'].encode('utf-8').lower().replace('_', '').replace('-', ''))
        hash_list = list(hash_set)
        # print hash_list
        for i in xrange(len(hash_list)):
            n1 = hash_list[i]
            n1id = name_map.get(n1, len(name_map))
            name_map[n1] = n1id
            w = node_weight.get(n1id, 0)
            node_weight[n1id] = w + 1

            user_set = tag_user.get(n1id, set())
            user_set.add(row['user']['id'])
            tag_user[n1id] = user_set

            for j in xrange(i+1, len(hash_list)):
                n2 = hash_list[j]
                if n1 != n2:
                    n2id = name_map.get(n2, len(name_map))
                    name_map[n2] = n2id
                    if n1id < n2id:
                        wt = edges.get((n1id, n2id), 0)
                        edges[(n1id, n2id)] = wt + 1
                    else:
                        wt = edges.get((n2id, n1id), 0)
                        edges[(n2id, n1id)] = wt + 1
    g = Graph(len(name_map), directed=True)
    #get key list of dict according to value ranking
    name_list = list(sorted(name_map, key=name_map.get))
    g.vs["name"] = name_list
    g.vs["weight"] = [node_weight[name_map[name]] for name in name_list]
    g.vs['user'] = [len(tag_user[name_map[name]]) for name in name_list]
    edges_list, edge_weights = [], []
    for (n1, n2) in edges.keys():
        edges_list.append((n1, n2))
        edges_list.append((n2, n1))
        # if float(edges[(n1, n2)])/node_weight[n1] > 1 or float(edges[(n1, n2)])/node_weight[n2]>1:
        #     print edges[(n1, n2)], node_weight[n1], node_weight[n2]
        edge_weights.append(float(edges[(n1, n2)])/node_weight[n1])
        edge_weights.append(float(edges[(n1, n2)])/node_weight[n2])
    # g.add_edges(edges.keys())
    g.add_edges(edges_list)
    g.es["weight"] = edge_weights
    return g


def load_hashtag_coocurrent_network_undir(db_name, collection='None', uids=[]):
    '''
    Hashtag Co-occurrence Network: weighted undirected network
    Edge: Hashtag --------- Hashtag
    excluding retweets
    '''
    if collection is 'None':
        cols = db_name
    else:
        db = dbt.db_connect_no_auth(db_name)
        cols = db[collection]
    name_map, edges, node_weight = {}, {}, {}
    filter = {}
    tag_user = {}
    if len(uids) > 0:
        filter['user.id'] = {'$in': uids}
    filter['$where'] = 'this.entities.hashtags.length>0'
    filter['retweeted_status'] = {'$exists': False}
    for row in cols.find(filter, no_cursor_timeout=True):
        # if 'retweeted_status' in row:
        #     continue
        hashtags = row['entities']['hashtags']
        hash_set = set()
        for hash in hashtags:
            # need no .encode('utf-8')
            hash_set.add(hash['text'].encode('utf-8').lower().replace('_', '').replace('-', ''))
        hash_list = list(hash_set)
        # print hash_list
        for i in xrange(len(hash_list)):
            n1 = hash_list[i]
            n1id = name_map.get(n1, len(name_map))
            name_map[n1] = n1id
            w = node_weight.get(n1id, 0)
            node_weight[n1id] = w + 1

            user_set = tag_user.get(n1id, set())
            user_set.add(row['user']['id'])  ## for norm data
            # user_set.add(row['from_user_id']) ## for ian data
            tag_user[n1id] = user_set

            for j in xrange(i+1, len(hash_list)):
                n2 = hash_list[j]
                if n1 != n2:
                    n2id = name_map.get(n2, len(name_map))
                    name_map[n2] = n2id
                    if n1id < n2id:
                        wt = edges.get((n1id, n2id), 0)
                        edges[(n1id, n2id)] = wt + 1
                    else:
                        wt = edges.get((n2id, n1id), 0)
                        edges[(n2id, n1id)] = wt + 1
    g = Graph(len(name_map), directed=False)
    #get key list of dict according to value ranking
    name_list = list(sorted(name_map, key=name_map.get))
    g.vs["name"] = name_list
    g.vs["weight"] = [node_weight[name_map[name]] for name in name_list] ## numbers of occurrences
    g.vs['user'] = [len(tag_user[name_map[name]]) for name in name_list] ## numbers of users who use
    g.add_edges(edges.keys())
    g.es["weight"] = edges.values() ## numbers of co-occurrence
    return g


def add_attribute(g, att_name, dbname, colname, db_field_name):
    db = dbt.db_connect_no_auth(dbname)
    com = db[colname]
    defaultV = -1000000000.0
    g.vs[att_name] = defaultV
    for x in com.find({db_field_name: {'$exists': True}}, ['id', db_field_name]):
        uid = x['id']
        exist = True
        try:
            v = g.vs.find(name=str(uid))
        except ValueError:
            exist = False
        if exist:
            if '.' in db_field_name:
                levels = db_field_name.split('.')
                t = x.get(levels[0])
                for level in levels[1:]:
                    t = t.get(level)
                    # if t is None:
                    #     t = defaultV
                    #     break
                v[att_name] = t
            else:
                v[att_name] = x.get(db_field_name)
    return g


def add_attributes(g, att_names, dbname, colname, db_field_names):
    db = dbt.db_connect_no_auth(dbname)
    com = db[colname]
    for att_name in att_names:
        g.vs[att_name] = 0.0
    for x in com.find({}, ['id'] + db_field_names):
        uid = x['id']
        exist = True
        try:
            v = g.vs.find(name=str(uid))
        except ValueError:
            exist = False
        if exist:
            for db_field_name in db_field_names:
                if '.' in db_field_name:
                    levels = db_field_name.split('.')
                    t = x.get(levels[0])
                    for level in levels[1:]:
                        t = t.get(level)
                        if t is None:
                            break
                    v[att_name] = t
                else:
                    v[att_name] = x.get(db_field_name)
    return g


def giant_component(g, mode=WEAK):
    ###must be either STRONG or WEAK
    com = g.clusters(mode=mode)
    print 'The processed network has components:', len(com)
    return com.giant()


def betweenness_community(g):
    '''
    This supports directed and weighted graph
    '''
    return g.community_edge_betweenness(directed=True, weights='weight')


def optimal_community(g, weighted=False):
    '''
    :param g:
    :param weighted:
    :return:
    membership indexes from 0
    '''
    if weighted:
        return g.community_optimal_modularity(weights='weight')
    else:
        return g.community_optimal_modularity()


def fast_community(g, weighted=True):
    '''Only for Undirected graph'''
    if g.is_directed():
        if weighted:
            g = g.as_undirected(combine_edges=dict(weight="sum"))
        else:
            g = g.as_undirected()
    if weighted:
        return g.community_fastgreedy(weights='weight')
        # return g.community_edge_betweenness(weights='weight')
    else:
        return g.community_fastgreedy()
        # return g.community_edge_betweenness()


def comm_plot(g, clusters, lable, membership=None):
    '''
    See: http://stackoverflow.com/questions/23184306/draw-network-and-grouped-vertices-of-the-same-community-or-partition/23185529#23185529
    '''
    if membership is not None:
        gcopy = g.copy()
        edges = []
        edges_colors = []
        for edge in g.es():
            if membership[edge.tuple[0]] != membership[edge.tuple[1]]:
                edges.append(edge)
                edges_colors.append("gray")
            else:
                edges_colors.append("black")
        gcopy.delete_edges(edges)
        layout = gcopy.layout("fr")
        g.es["color"] = edges_colors
    else:
        layout = g.layout("fr")
        g.es["color"] = "black"
    shape_dict = {0: "circle", 1: "rectangle"}
    visual_style = {}
    visual_style["vertex_shape"] = [shape_dict[flag] for flag in g.vs["rec"]]
    visual_style["edge_color"] = g.es["color"]
    visual_style["vertex_size"] = 7
    visual_style["edge_arrow_size"] = 0.2
    visual_style["edge_arrow_width"] = 0.2
    visual_style["layout"] = layout
    visual_style["bbox"] = (1024, 768)
    visual_style["margin"] = 20
    if membership is not None:
        # colors = []
        # for i in range(0, max(membership)+1):
        #     colors.append('%06X' % randint(0, 0xFFFFFF))
        pal = ClusterColoringPalette(max(membership)+1)
        for vertex in g.vs():
            vertex["color"] = pal.get([membership[vertex.index]])
        visual_style["vertex_color"] = g.vs["color"]
    plot(clusters, lable, **visual_style)


def out_edgelist(dbname, netname, filename, ego, alter, filter={}):
    fo = open(filename, 'w')
    db = dbt.db_connect_col(dbname, netname)
    for b in db.find(filter, no_cursor_timeout=True):
        fo.write(str(b[ego]) + '\t' + str(b[alter]) + '\n')
    fo.flush()
    fo.close()

def net_stat(g):
    node_n = g.vcount()
    edge_m = g.ecount()
    degree_mean = np.mean(g.indegree())
    degree_std = np.std(g.indegree())
    density = g.density()
    avg_path = g.average_path_length(directed=True, unconn=True)
    # avg_path = 0
    components = g.clusters(mode=WEAK)
    comp_count = len(components)
    giant_comp = components.giant()
    giant_comp_r = float(giant_comp.vcount())/node_n
    cluster_co_global = g.transitivity_undirected()
    # cluster_co_avg = g.transitivity_avglocal_undirected()
    recip = g.reciprocity()
    assort = g.assortativity_degree(directed=True)
    print '#Node, #Edge, <k>, std()k, #Density, #Path, #Comp, %GCR, Cluster, Recip, Assort'
    print '%d, %d, %.3f, %.3f, %.3f, %.3f, %d, %.3f, %.3f, %.3f, %.3f ' % (node_n, edge_m, degree_mean, degree_std, density, avg_path, comp_count, giant_comp_r, cluster_co_global, recip, assort)


def most_pagerank(g, n=10, weight=None):
    ranks = g.pagerank(weights=weight)
    arr = np.array(ranks)
    # print (-arr).argsort()[:n]
    # print arr[(-arr).argsort()[:n]]
    return g.vs[(-arr).argsort()[:n].tolist()]['name']


def graph_plot(g):
    layout = g.layout("kk")
    plot(g, layout=layout, bbox=(1200, 900))

if __name__ == '__main__':
    # g = load_beh_network('fed', 'sbnet', 'retweet')
    # summary(g)
    # pickle.dump(g, open('data/fg.pick', 'w'))
    # g = pickle.load(open('data/bg.pick', 'r'))
    # g = add_attribute(g, 'gbmi', 'fed', 'scom', 'text_anal.gbmi.value')
    # for v in g.vs:
    #     print v['name'], v['gbmi']

    '''to_undirected (mode="collapse")
    collapse: only keep one edge of multiple edges One undirected edge
    will be created for each pair of vertices which are connected with at
    least one directed edge, no multiple edges will be created.
    mutual: ONLY create one edge for nodes if they have multiple edges,
    One undirected edge will be created for each pair of mutual edges.
    Non-mutual edges are ignored. This mode might create multiple edges
    if there are more than one mutual edge pairs between the same pair of vertices.
    '''

    g = Graph([(0,1), (0,2), (2,0), (2,3), (3,4), (4,2), (2,5), (5,0), (6,3), (5,6)], directed=True)
    print g
    g.vs["name"] = ["Alice", "Bob", "Claire", "Dennis", "Esther", "Frank", "George"]
    # g.vs["age"] = [25, 31, 18, 47, 22, 23, 50]
    # g.vs["gender"] = ["f", "m", "f", "m", "f", "m", "m"]
    # g.es["is_formal"] = [False, False, True, True, True, False, True, False, False]
    # g.es['weight'] = 2.0
    g = g.as_undirected(mode="mutual") # collapse
    print g.clusters()
    print g.components()
    layout = g.layout("kk")
    plot(g, layout=layout)


    # print g.es[g.get_eid('480706562', '386203927')]
    # print g.es[g.get_eid('1092937046', '777200318')]
    # print g.es[g.get_eid('1129480146', '919267472')]
    # print g.es[g.get_eid('431013874', '518335800')]
    # print g.es[g.get_eid('249683957', '548884928')]
    # indegree = g.indegree()
    # outdegree = g.outdegree()
    # instrength = g.strength(mode='IN', weights='weight')
    # outstrenght = g.strength(mode='OUT', weights='weight')
    # print min(indegree), max(indegree)
    # splot.pdf_plot_one_data(indegree, 'Indegree')
    # splot.pdf_plot_one_data(outdegree, 'Outdegree')



    # g = load_network('fed', 'snet')
    # gc = giant_component(g, 'WEAK')
    # summary(gc)
    # coms = community(gc)
    # clus = coms.as_clustering()
    # summary(clus)
    # for clu in clus:
    #     summary(clu)
    #
    # DG = nt.load_network('fed', 'snet')
    # gc2 = nt.get_gaint_comp(DG)
    # print gc2.number_of_nodes(), gc2.number_of_edges()
    #
    # t0 = time()
    # g = load_network('fed', 'snet')
    # indegree1 = g.indegree()
    # outdegree1 = g.outdegree()
    # # plot.pdf_plot_one_data(indegree, 'indegree', min(indegree), max(indegree))
    # t1 = time()
    # DG = nt.load_network('fed', 'snet')
    # indegree2 = DG.in_degree().values()
    # outdegree2 = DG.out_degree().values()
    # # plot.pdf_plot_one_data(indegree, 'indegree', min(indegree), max(indegree))
    # t2 = time()
    # print list(set(indegree1) - set(indegree2))
    # print list(set(outdegree1) - set(outdegree2))
    # print 'function vers1 takes %f' %(t1-t0)
    # print 'function vers2 takes %f' %(t2-t1)
    #
    # for v in DG.nodes():
    #     ist1 = DG.in_degree(v)
    #     ist2 = g.indegree(str(v))
    #     if ist1 != ist2:
    #         print 'Fa'
    # print 'finished'
    #
    #
    # g = load_beh_network('fed', 'sbnet')
    # indegree1 = g.indegree()
    # outdegree1 = g.outdegree()
    # inst1 = g.strength(mode='IN')
    # outst1 = g.strength(mode='OUT')
    #
    # DG = nt.load_behavior_network('fed', 'sbnet')
    # indegree2 = DG.in_degree().values()
    # outdegree2 = DG.out_degree().values()
    # inst2 = DG.in_degree(weight='weight').values()
    # outst2 = DG.out_degree(weight='weight').values()
    #
    # print list(set(indegree1) - set(indegree2))
    # print list(set(outdegree1) - set(outdegree2))
    # print list(set(inst1) - set(inst2))
    # print list(set(outst1) - set(outst2))
    #
    # for v in DG.nodes():
    #     ist1 = DG.in_degree(v, weight='weight')
    #     ist2 = g.strength(str(v), mode='IN', weights='weight')
    #     if ist1 != ist2:
    #         print ist1, ist2
    #         # print 'Fa'
