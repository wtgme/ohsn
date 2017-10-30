# -*- coding: utf-8 -*-
"""
Created on 13:18, 13/10/17

@author: wt

This is to study multilay network of pro-ED and pro-recovery users on discussions of different topics
"""


import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))


import ohsn.util.db_util as dbt
import ohsn.util.io_util as iot
import pymongo
import ohsn.util.graph_util as gt
import ohsn.networkminer.timeline_network_miner as timiner
import pickle
from collections import Counter




def constrcut_data(filename='data/communication-only-fed-filter-hashtag-cluster.graphml'):
    ## Categorize tweets into three classes: 0: no hashtag; -1: ED tag; 1: non-ED tag.
    # user_net = gt.Graph.Read_GraphML(filename)
    # uids = [int(uid) for uid in user_net.vs['name']]

    # get users who have more than 3 ED-related tweets
    all_uids = iot.get_values_one_field('fed', 'ed_tag', 'user.id')
    all_uids_count = Counter(all_uids)
    uids = [key for key in all_uids_count if all_uids_count[key] >= 3]
    print len(uids)
    edtags = set(iot.read_ed_hashtags())
    times = dbt.db_connect_col('fed', 'timeline')
    poi_time = dbt.db_connect_col('fed', 'pro_timeline')
    poi_time.create_index([('user.id', pymongo.ASCENDING),
                          ('id', pymongo.DESCENDING)])
    poi_time.create_index([('type', pymongo.ASCENDING)])
    poi_time.create_index([('id', pymongo.ASCENDING)], unique=True)

    for tweet in times.find({'user.id': {'$in': uids}}, no_cursor_timeout=True):
        hashtags = tweet['entities']['hashtags']
        tagset = set()
        for hash in hashtags:
            tag = hash['text'].encode('utf-8').lower().replace('_', '').replace('-', '')
            tagset.add(tag)
        if len(tagset) == 0:
            tweet['type'] = 0
        else:
            if len(tagset.intersection(edtags)) > 0:
                tweet['type'] = -1
            else:
                tweet['type'] = 1
        try:
            poi_time.insert(tweet)
        except pymongo.errors.DuplicateKeyError:
            pass

def extract_network(dbname, timename, bnetname, typename='ED'):
    # Extract different networks from different types of content
    # typemap = {'ED': -1,
    #            'Non-ED': 1,
    #            'Non-tag': 0}
    # type = typemap[typename]
    time = dbt.db_connect_col(dbname, timename)
    bnets = []
    for i in range(4):
        bnet = dbt.db_connect_col(dbname, bnetname+str(i))
        bnet.create_index([("id0", pymongo.ASCENDING),
                                     ("id1", pymongo.ASCENDING),
                                      ("type", pymongo.ASCENDING),
                                     ("statusid", pymongo.ASCENDING)],
                                    unique=True)
        bnets.append(bnet)

    filter = {'$where': 'this.entities.user_mentions.length>0',
                'topics': {'$exists': True},
              'retweeted_status': {'$exists': False}}
    count2 = 0
    for tweet in time.find(filter, no_cursor_timeout=True):
        if len(tweet['topics'] )> 1:
            count2 += 1
        if len(tweet['topics']) == 1:
            index = tweet['topics'][0]
            udmention_list = []
            if ('retweeted_status' in tweet) and len(tweet['retweeted_status']['entities']['user_mentions'])>0:
                for udmention in tweet['retweeted_status']['entities']['user_mentions']:
                    udmention_list.append(udmention['id'])
            for mention in tweet['entities']['user_mentions']:
                if ('in_reply_to_user_id' in tweet) and (mention['id'] == tweet['in_reply_to_user_id']): # reply
                    timiner.add_reply_edge(bnets[index], tweet['user']['id'], tweet['in_reply_to_user_id'], tweet['created_at'], tweet['id'])

                elif ('retweeted_status' in tweet) and (mention['id'] == tweet['retweeted_status']['user']['id']): # Retweet
                    timiner.add_retweet_edge(bnets[index], tweet['user']['id'], tweet['retweeted_status']['user']['id'], tweet['created_at'], tweet['id'])

                elif mention['id'] in udmention_list:  # mentions in Retweet content
                    timiner.add_undirect_mentions_edge(bnets[index], tweet['user']['id'], mention['id'], tweet['created_at'], tweet['id'])

                else:  # original mentions
                    timiner.add_direct_mentions_edge(bnets[index], tweet['user']['id'], mention['id'], tweet['created_at'], tweet['id'])
    print count2, 'more than 2 topics'

def out_graph_edges(g, edgePath, node_attrs = {}):
    # out edge list and node attribute list
    with open(edgePath, 'wb') as fw:
        for e in g.es:
            source_vertex_id = e.source
            target_vertex_id = e.target
            source_vertex = g.vs[source_vertex_id]
            target_vertex = g.vs[target_vertex_id]

            if source_vertex['name'] not in node_attrs:
                node_attrs[source_vertex['name']] = len(node_attrs) + 1
            if target_vertex['name'] not in node_attrs:
                node_attrs[target_vertex['name']] = len(node_attrs) + 1

            fw.write('%s %s %d\n' %('N'+source_vertex['name'],
                                     'N'+target_vertex['name'],
                                     e['weight']))


    return node_attrs


def networks(dbname):
    # out networks to multiplex process
    # all_uids = iot.get_values_one_field('fed', 'ed_tag', 'user.id')
    # all_uids_count = Counter(all_uids)
    # uids = [key for key in all_uids_count if all_uids_count[key] >= 3]
    # print len(uids)
    # g1 = gt.load_beh_network_subset(uids, dbname, 'pro_bnet0', btype='communication')
    # g2 = gt.load_beh_network_subset(uids, dbname, 'pro_bnet1', btype='communication')
    # g3 = gt.load_beh_network_subset(uids, dbname, 'pro_bnet2', btype='communication')
    # g4 = gt.load_beh_network_subset(uids, dbname, 'pro_bnet3', btype='communication')
    # g1.write_graphml('pro1.graphml')
    # g2.write_graphml('pro2.graphml')
    # g3.write_graphml('pro3.graphml')
    # g4.write_graphml('pro4.graphml')

    g1 = gt.Graph.Read_GraphML('pro1.graphml')
    g2 = gt.Graph.Read_GraphML('pro2.graphml')
    g3 = gt.Graph.Read_GraphML('pro3.graphml')
    g4 = gt.Graph.Read_GraphML('pro4.graphml')
    gt.net_stat(g1)
    gt.net_stat(g2)
    gt.net_stat(g3)
    gt.net_stat(g4)

    # g1 = gt.giant_component(g1, 'WEAK')
    # g2 = gt.giant_component(g2, 'WEAK')
    # g3 = gt.giant_component(g3, 'WEAK')
    # g4 = gt.giant_component(g4, 'WEAK')

    # gt.net_stat(g1)
    # gt.net_stat(g2)
    # gt.net_stat(g3)
    # gt.net_stat(g4)

    # common = set(g1.vs['name']).intersection(g2.vs['name'])
    # common = set(g3.vs['name']).intersection(common)
    # common = set(g4.vs['name']).intersection(common)
    # print len(common)
    # g1 = g1.subgraph(g1.vs.select(name_in=common))
    # g2 = g2.subgraph(g2.vs.select(name_in=common))
    # g3 = g3.subgraph(g3.vs.select(name_in=common))
    # g4 = g4.subgraph(g4.vs.select(name_in=common))
    # gt.net_stat(g1)
    # gt.net_stat(g2)
    # gt.net_stat(g3)
    # gt.net_stat(g4)

    # g1.write_graphml('pro1-comm.graphml')
    # g2.write_graphml('pro2-comm.graphml')
    # g3.write_graphml('pro3-comm.graphml')
    # g4.write_graphml('pro4-comm.graphml')

    uidlist = out_graph_edges(g1, 'data/pro1.edge')
    uidlist = out_graph_edges(g2, 'data/pro2.edge', uidlist)
    uidlist = out_graph_edges(g3, 'data/pro3.edge', uidlist)
    uidlist = out_graph_edges(g4, 'data/pro4.edge', uidlist)


    with open('data/pro.node', 'wb') as fw:
        fw.write('nodeID nodeLabel\n')
        for k in list(sorted(uidlist, key=uidlist.get)):
            fw.write(str(uidlist[k]) + ' N' + k + '\n')


def fed_all_tag_topic(filepath='data/fed_tag_undir.graphml'):
    # get topics of all hashtags posted by fed users
    # The results before are obatain using more than 3 tweets and 3 users
    # Then use the giant component.
    g = gt.Graph.Read_GraphML(filepath)
    gt.summary(g)
    vs = g.vs(weight_gt=10, user_gt=10)
    g = g.subgraph(vs)
    gt.summary(g)
    # g = gt.giant_component(g)
    com = g.community_infomap(edge_weights='weight', vertex_weights='weight')
    comclus = com.subgraphs()
    print len(comclus)
    pickle.dump(comclus, open('data/fed_tag_undir.communities'))


def tag_net(dbname, colname, filename):
    # All tags excluding retweets
    # g = gt.load_hashtag_coocurrent_network_undir(dbname, colname)
    # gt.summary(g)
    # g.write_graphml(filename+'_tag_undir.graphml')

    # Only frequent tags
    # g = gt.Graph.Read_GraphML('data/pro_tag_undir.graphml')
    # gt.summary(g)
    # nodes = g.vs.select(weight_gt=3)
    # print 'Filtered nodes: %d' %len(nodes)
    # g = g.subgraph(nodes)
    # nodes = g.vs.select(user_gt=3)
    # print 'Filtered nodes: %d' %len(nodes)
    # g = g.subgraph(nodes)
    # gt.summary(g)
    # g = gt.giant_component(g)
    # g.write_graphml('data/'+filename+'_tag_undir_gc.graphml')


    g = gt.Graph.Read_GraphML('data/'+filename+'_tag_undir_gc.graphml')
    gt.summary(g)
    com = g.community_multilevel(weights='weight', return_levels=False)
    # informap Community stats: #communities, modularity 2845 0.454023502108
    # Louvain : Community stats: #communities, modularity 59 0.496836953082
    comclus = com.subgraphs()
    print 'Community stats: #communities, modularity', len(comclus), com.modularity
    csize = [comclu.vcount() for comclu in comclus]
    # csize = [sum(comclu.vs['weight']) for comclu in comclus]
    potag = []
    for i in range(4):
        index = csize.index(max(csize))
        csize[index] = 0
        tnet = comclus[index]
        potag.append(set(tnet.vs['name']))

    times = dbt.db_connect_col(dbname, colname)
    filter = {'$where': 'this.entities.hashtags.length>0',
              'retweeted_status': {'$exists': False}}
    for tweet in times.find(filter, no_cursor_timeout=True):
        hashtags = tweet['entities']['hashtags']
        hash_set = set()
        for hash in hashtags:
            hash_set.add(hash['text'].encode('utf-8').lower().replace('_', '').replace('-', ''))
        topics = []
        for i, pot in enumerate(potag):
            if len(hash_set.intersection(pot)) > 0:
                topics.append(i)
        if len(topics) > 0:
            times.update_one({'id': tweet['id']}, {'$set': {'topics': topics}}, upsert=False)




if __name__ == '__main__':
    # constrcut_data()
    # extract_network('fed', 'pro_timeline', 'pro_bnet', 'ED')

    networks('fed')
    # fed_all_tag_topic()
    # tag_net('fed', 'pro_timeline', 'pro')

