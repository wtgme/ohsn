# -*- coding: utf-8 -*-
"""
Created on 13:18, 13/10/17

@author: wt

This is to study multilay network of pro-ED and pro-recovery users on discussions of different topics
"""


import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))


from datetime import datetime
import ohsn.util.db_util as dbt
import ohsn.util.io_util as iot
import ohsn.api.tweet_lookup as tweetlook
import pymongo
import ohsn.util.graph_util as gt
import ohsn.networkminer.timeline_network_miner as timiner
import pickle
from collections import Counter

from igraph import *
import re
from nltk.tokenize import RegexpTokenizer
tokenizer = RegexpTokenizer(r'\w+')



def constrcut_data(filename='data/communication-only-fed-filter-hashtag-cluster.graphml'):
    ## Categorize tweets into three classes: 0: no hashtag; -1: ED tag; 1: non-ED tag.
    # user_net = gt.Graph.Read_GraphML(filename)
    # uids = [int(uid) for uid in user_net.vs['name']]

    # get users who have more than 3 ED-related tweets
    all_uids = iot.get_values_one_field('fed', 'ed_tag', 'user.id')
    # exist_uids = iot.get_values_one_field('fed', 'pro_timeline', 'user.id')
    # all_uids_count = Counter(all_uids)
    # uids = [key for key in all_uids_count if all_uids_count[key] < 3]
    # uids = list(set(all_uids)-set(exist_uids))
    uids = list(set(all_uids))
    print len(uids)
    pickle.dump(uids, open('ed-user.pick', 'w'))
    # edtags = set(iot.read_ed_hashtags())
    times = dbt.db_connect_col('fed', 'timeline')
    poi_time = dbt.db_connect_col('fed', 'pro_timeline')
    poi_time.create_index([('user.id', pymongo.ASCENDING),
                          ('id', pymongo.DESCENDING)])
    poi_time.create_index([('type', pymongo.ASCENDING)])
    poi_time.create_index([('id', pymongo.ASCENDING)], unique=True)

    for tweet in times.find({'user.id': {'$in': uids}}, no_cursor_timeout=True):
        # hashtags = tweet['entities']['hashtags']
        # tagset = set()
        # for hash in hashtags:
        #     tag = hash['text'].encode('utf-8').lower().replace('_', '').replace('-', '')
        #     tagset.add(tag)
        # if len(tagset) == 0:
        #     tweet['type'] = 0
        # else:
        #     if len(tagset.intersection(edtags)) > 0:
        #         tweet['type'] = -1
        #     else:
        #         tweet['type'] = 1
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
    tid_topicid = pickle.load(open('data/tid_topicid.pick', 'r'))
    time = dbt.db_connect_col(dbname, timename)
    bnet = dbt.db_connect_col(dbname, bnetname)
    bnet.create_index([("id0", pymongo.ASCENDING),
                       ("id1", pymongo.ASCENDING),
                       ("type", pymongo.ASCENDING),
                       ("tags", pymongo.ASCENDING),
                      ("statusid", pymongo.ASCENDING)],
                        unique=True)

    filter = {'$where': 'this.entities.user_mentions.length>0',
                # 'topics': {'$exists': True},
              'retweeted_status': {'$exists': False}}
    count2 = 0
    for tweet in time.find(filter, no_cursor_timeout=True):
        # if len(tweet['topics'] )> 1:
        #     count2 += 1
        # if len(tweet['topics']) == 1:
        # for index in tweet['topics']:
        #     # index = tweet['topics'][0]
        #     if index in [35, 3, 2, 14, 25]:
        tid = str(tweet['id'])
        topicid = tid_topicid.get(tid, -1)
        if topicid > 0:
            udmention_list = []
            if ('retweeted_status' in tweet) and len(tweet['retweeted_status']['entities']['user_mentions'])>0:
                for udmention in tweet['retweeted_status']['entities']['user_mentions']:
                    udmention_list.append(udmention['id'])
            for mention in tweet['entities']['user_mentions']:
                if ('in_reply_to_user_id' in tweet) and (mention['id'] == tweet['in_reply_to_user_id']): # reply
                    timiner.add_reply_edge(bnet, tweet['user']['id'], tweet['in_reply_to_user_id'], tweet['created_at'], tweet['id'], topicid)

                elif ('retweeted_status' in tweet) and (mention['id'] == tweet['retweeted_status']['user']['id']): # Retweet
                    timiner.add_retweet_edge(bnet, tweet['user']['id'], tweet['retweeted_status']['user']['id'], tweet['created_at'], tweet['id'], topicid)

                elif mention['id'] in udmention_list:  # mentions in Retweet content
                    timiner.add_undirect_mentions_edge(bnet, tweet['user']['id'], mention['id'], tweet['created_at'], tweet['id'], topicid)

                else:  # original mentions
                    timiner.add_direct_mentions_edge(bnet, tweet['user']['id'], mention['id'], tweet['created_at'], tweet['id'], topicid)
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


def networks(dbname, bnet='all_pro_bnet'):
    # out networks to multiplex process
    # all_uids = iot.get_values_one_field('fed', 'ed_tag', 'user.id')
    # all_uids_count = Counter(all_uids)
    # uids = [key for key in all_uids_count]
    topics = [35, 3, 2, 14, 25] # [35, 3, 2, 14, 25]
    # g = gt.load_beh_network_filter(dbname, bnet, btype='communication')
    # g.write_graphml('pro_mentionall'+'.graphml')
    # for i, tag in enumerate(topics):
    #     g = gt.load_beh_network_filter(dbname, bnet, btype='communication', filter={'tags': tag})
    #     g.write_graphml('pro_mention'+str(tag)+'.graphml')

    gall = gt.Graph.Read_GraphML('pro_mentionall'+'.graphml')
    core = gall.k_core(27)
    core_name = core.vs['name']
    gs = []
    for i, tag in enumerate(topics):
        g = gt.Graph.Read_GraphML('pro_mention'+str(tag)+'.graphml')
        g = g.subgraph(g.vs.select(name_in=core_name))
        gs.append(g)
    uidlist = {}
    for i, g in enumerate(gs):
        uidlist = out_graph_edges(g, 'pro_mention'+str(topics[i])+'.edge', uidlist)
    with open('pro_mention.node', 'wb') as fw:
        fw.write('nodeID nodeLabel\n')
        for k in list(sorted(uidlist, key=uidlist.get)):
            fw.write(str(uidlist[k]) + ' N' + k + '\n')

    # g1 = gt.Graph.Read_GraphML('data/pro1.graphml')
    # g2 = gt.Graph.Read_GraphML('data/pro2.graphml')
    # g3 = gt.Graph.Read_GraphML('data/pro3.graphml')
    # g4 = gt.Graph.Read_GraphML('data/pro4.graphml')
    # gt.net_stat(g1)
    # gt.net_stat(g2)
    # gt.net_stat(g3)
    # gt.net_stat(g4)

    # g1 = gt.giant_component(g1, 'WEAK')
    # g2 = gt.giant_component(g2, 'WEAK')
    # g3 = gt.giant_component(g3, 'WEAK')
    # g4 = gt.giant_component(g4, 'WEAK')
    #
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

    # uidlist = out_graph_edges(g1, 'data/mu/pro1.edge')
    # uidlist = out_graph_edges(g2, 'data/mu/pro2.edge', uidlist)
    # uidlist = out_graph_edges(g3, 'data/mu/pro3.edge', uidlist)
    # uidlist = out_graph_edges(g4, 'data/mu/pro4.edge', uidlist)


    # with open('data/mu/pro.node', 'wb') as fw:
    #     fw.write('nodeID nodeLabel\n')
    #     for k in list(sorted(uidlist, key=uidlist.get)):
    #         fw.write(str(uidlist[k]) + ' N' + k + '\n')


def data_transf(sourcefile):
    # data to mammult packages
    g = gt.Graph.Read_GraphML(sourcefile)
    for e in g.es:
        source_vertex_id = e.source
        target_vertex_id = e.target
        source_vertex = g.vs[source_vertex_id]
        target_vertex = g.vs[target_vertex_id]
        print source_vertex['name'] + ' ' + target_vertex['name']


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
    g = gt.load_hashtag_coocurrent_network_undir(dbname, colname)
    gt.summary(g)
    g.write_graphml(filename+'_tag_undir.graphml')

    # Only frequent tags
    # g = gt.Graph.Read_GraphML(filename+'_tag_undir.graphml')
    # gt.summary(g)
    # nodes = g.vs.select(weight_gt=3)
    # print 'Filtered nodes: %d' %len(nodes)
    # g = g.subgraph(nodes)
    # nodes = g.vs.select(user_gt=3)
    # print 'Filtered nodes: %d' %len(nodes)
    # g = g.subgraph(nodes)
    # gt.summary(g)
    # g = gt.giant_component(g)
    # # g.write_graphml('data/'+filename+'_tag_undir_gc.graphml')


    # # g = gt.Graph.Read_GraphML('data/'+filename+'_tag_undir_gc.graphml')
    # gt.summary(g)
    # com = g.community_multilevel(weights='weight', return_levels=False)
    # # informap Community stats: #communities, modularity 2845 0.454023502108
    # # Louvain : Community stats: #communities, modularity 59 0.496836953082
    # comclus = com.subgraphs()
    # print 'Community stats: #communities, modularity', len(comclus), com.modularity
    # # csize = [comclu.vcount() for comclu in comclus]
    # # csize = [sum(comclu.vs['weight']) for comclu in comclus]
    # potag = []
    # for i in range(len(comclus)):
    #     tnet = comclus[i]
    #     potag.append(set(tnet.vs['name']))

    # times = dbt.db_connect_col(dbname, colname)
    # filter = {'$where': 'this.entities.hashtags.length>0',
    #           'retweeted_status': {'$exists': False}}
    # for tweet in times.find(filter, no_cursor_timeout=True):
    #     hashtags = tweet['entities']['hashtags']
    #     hash_set = set()
    #     for hash in hashtags:
    #         hash_set.add(hash['text'].encode('utf-8').lower().replace('_', '').replace('-', ''))
    #     topics = []
    #     for i, pot in enumerate(potag):
    #         if len(hash_set.intersection(pot)) > 0:
    #             topics.append(i)
    #     if len(topics) > 0:
    #         times.update_one({'id': tweet['id']}, {'$set': {'topics': topics}}, upsert=False)



def tag_activity(dbname, colname):
    # recording the activity of tag

    g = gt.Graph.Read_GraphML('allpro_tag_undir.graphml')
    vs = g.vs(weight_gt=3, user_gt=3)
    sg = g.subgraph(vs)
    gc = gt.giant_component(sg)
    tag_time = {}
    for v in gc.vs:
        tag_time[v['name']] = []


    time = dbt.db_connect_col(dbname, colname)
    filter = {}
    filter['$where'] = 'this.entities.hashtags.length>0'
    filter['retweeted_status'] = {'$exists': False}
    for tweet in time.find(filter, no_cursor_timeout=True):
        # if 'retweeted_status' in row:
        #     continue
        created_at = datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
        hashtags = tweet['entities']['hashtags']
        for hash in hashtags:
            # need no .encode('utf-8')
            tag = (hash['text'].encode('utf-8').lower().replace('_', '').replace('-', ''))
            if tag in tag_time:
                datelist = tag_time.get(tag, [])
                datelist.append(created_at)
                tag_time[tag] = datelist
    pickle.dump(tag_time, open('tag_activity.pick', 'w'))


def mention_tweets(dbname, comname, bnetname, mention_tweet_name):
    # all_fed = iot.get_values_one_field('fed', 'com', 'id')
    # core_ed_net = gt.load_beh_network(dbname, colname, btype='communication')
    # gt.net_stat(core_ed_net)
    # print len(set(all_fed).intersection(set([int(uid) for uid in core_ed_net.vs['name']])))
    # 46842, 123340, 0.000, 5.276, 63, 0.995, 0.008, 0.021, -0.106
    # 22874

    # core = iot.get_values_one_field(dbname, comname, 'user.id')
    bnet = dbt.db_connect_col(dbname, bnetname)
    # core = list(set(core))
    # print len(core)
    core = pickle.load(open('ed-user.pick', 'r'))

    myfilter = {'$and': [{'id0': {'$in': core}}, {'id1': {'$in': core}}]}
    # myfilter = {}
    # g = gt.load_beh_network_filter(dbname, colname, 'communication', myfilter)
    # gt.net_stat(g)
    # g.write_graphml('core-ed-in.graphml')
    btype_dic = {'retweet': [1],
                 'reply': [2],
                 'mention': [3],
                 'communication': [2, 3],
                 'all': [1, 2, 3]}
    myfilter['type'] = {'$in': btype_dic['communication']}


    poi_time = dbt.db_connect_col(dbname, mention_tweet_name)
    poi_time.create_index([('user.id', pymongo.ASCENDING),
                          ('id', pymongo.DESCENDING)])
    poi_time.create_index([('type', pymongo.ASCENDING)])
    poi_time.create_index([('id', pymongo.ASCENDING)], unique=True)

    times = dbt.db_connect_col(dbname, 'pro_timeline')
    for link in bnet.find(myfilter, no_cursor_timeout=True):
        # if (link['id0'] in core) and (link['id1'] in core):
        tweet = times.find_one({'id': link['statusid']})
        try:
            poi_time.insert(tweet)
        except pymongo.errors.DuplicateKeyError:
            pass


def conversation(dbname, timename, alltimename, filename):
    # # Build mention and reply converstation in the data
    # # userlist = iot.get_values_one_field(dbname, timename, 'user.id')
    # # userlist = list(set(userlist))
    # # print len(userlist)
    # # alltime = dbt.db_connect_col(dbname, alltimename)
    # alltime = dbt.db_connect_col(dbname, timename)
    # name_map, edges = {}, {}
    # # for tweet in alltime.find({'user.id': {'$in': userlist}}, no_cursor_timeout=True):
    # for tweet in alltime.find({}, no_cursor_timeout=True):
    #     n1 = str(tweet['id'])
    #     n1id = name_map.get(n1, len(name_map))
    #     name_map[n1] = n1id
    #     n2 = tweet['in_reply_to_status_id']
    #     if n2:
    #         n2 = str(n2)
    #         n2id = name_map.get(n2, len(name_map))
    #         name_map[n2] = n2id
    #         wt = edges.get((n1id, n2id), 0)
    #         edges[(n1id, n2id)] = wt + 1
    # g = gt.Graph(len(name_map), directed=True)
    # g.vs["name"] = list(sorted(name_map, key=name_map.get))
    # # If items(), keys(), values(), iteritems(), iterkeys(), and itervalues() are called with no intervening modifications to the dictionary, the lists will directly correspond.
    # # http://stackoverflow.com/questions/835092/python-dictionary-are-keys-and-values-always-the-same-order
    # g.add_edges(edges.keys())
    # g.es["weight"] = edges.values()
    # g.write_graphml(filename)
    alltime = dbt.db_connect_col(dbname, timename)
    for tweet in alltime.find({'retweeted_status': {'$exists': False}}, no_cursor_timeout=True):
        s = str(tweet['id'])
        n2 = tweet['in_reply_to_status_id']
        if n2:
            s += '\t' + str(n2)
        print s



def read_tweet(tweet):
    text = tweet['text'].encode('utf8')
    # replace RT, @, and Http://
    text = text.strip().lower()
    text = re.sub(r"(?:(rt\ ?@)|@|https?://)\S+", "", text) # replace RT @, @ and http:// keep hashtag but remove
    words = tokenizer.tokenize(text)
    return ' '.join(words)


def rebuild_converstation(dbname, timename, converstation_graph, converstationfile):
    # # re-build converstation for the mention connections
    # Too large, run on super computer
    # # g = gt.Graph.Read_GraphML(converstation_graph)
    # tids = set(iot.get_values_one_field(dbname, timename, 'id'))
    # pickle.dump(tids, open('core_mention_tweets_id.pick', 'w'))
    # # print len(tids)
    # # coms = g.clusters(mode=WEAK)
    # # tweetids = g.vs['name']
    # # members = coms.membership
    # # tid_mem = dict(zip(tweetids, members))
    # # maps = {}
    # # for i, key in enumerate(tweetids):
    # #     tidlist = maps.get(members[i], [])
    # #     tidlist.append(key)
    # #     maps[members[i]] = tidlist
    # # dumplicated = set()
    # # for tid in tids:
    # #     if tid not in dumplicated:
    # #         mem = tid_mem[tid]
    # #         others = maps[mem]
    # #         print ' '.join(others)
    # #         for other in others:
    # #             dumplicated.add(other)


    # retrive tweets into core-mention-timeline
    fr = open(converstationfile, 'r')
    times = dbt.db_connect_col(dbname, 'timeline')
    core_time = dbt.db_connect_col(dbname, timename)
    miss = []
    tids = set(iot.get_values_one_field(dbname, timename, 'id'))
    for line in fr.readlines():
        ids = line.strip().split()
        ids = [int(tid) for tid in ids]
        for tid in ids:
            if tid not in tids:
                # tweets = times.find_one({'id': tid})
                # if tweets:
                #     try:
                #         core_time.insert(tweets)
                #     except pymongo.errors.DuplicateKeyError:
                #         pass
                # else:
                miss.append(tid)
                if len(miss) == 100:
                    twes = tweetlook.retrive_tweets(miss)
                    for twe in twes:
                        try:
                            core_time.insert(twe)
                        except pymongo.errors.DuplicateKeyError:
                            pass
                    miss = []
    fr.close()



    fr = open(converstationfile, 'r')
    fw = open('pro-converstation-tweets-tags.txt', 'w')
    miss, all = 0, 0
    times = dbt.db_connect_col(dbname, timename)
    for line in fr.readlines():
        tids = line.strip().split()
        tids = [int(tid) for tid in tids]
        tids.sort()
        s = ''
        tag = []
        for tid in tids:
            all += 1
            tweets = times.find_one({'id': tid})
            if tweets:
                text = read_tweet(tweets)
                s += text + ' '
                hashtags = tweets['entities']['hashtags']
                hash_set = set()
                for hash in hashtags:
                    hash_set.add(hash['text'].encode('utf-8').lower().replace('_', '').replace('-', ''))
                tag.extend(list(hash_set))
            else:
                miss += 1
        fw.write(s + '\t' + ' '.join(tag) + '\n')
    print miss, all, miss*1.0/all
    fw.close()
    fr.close()


def out_tid_uid(dbname, timename):
    times = dbt.db_connect_col(dbname, timename)
    for tweet in times.find({}, no_cursor_timeout=True):
        print str(tweet['id']) + '\t' + str(tweet['user']['id'])


if __name__ == '__main__':
    # constrcut_data()
    # fed_all_tag_topic()
    # tag_net('fed', 'pro_timeline', 'allpro')
    # tag_net('fed', 'pro_timeline', 'data/allpro')
    # extract_network('fed', 'pro_timeline', 'all_pro_bnet', 'ED')

    # networks('fed')
    # data_transf('data/pro4.graphml')
    # tag_activity('fed', 'pro_timeline')

    '''Build conversations from users' mention_timeline, and extract network from these conversations
    All data extracted fro in_repy_to_ in pro_mention_timeline '''

    # mention_tweets(dbname='fed', comname='ed_tag', bnetname='all_pro_bnet', mention_tweet_name='pro_mention_timeline')
    # rebuild_converstation('fed', 'core_mention_timeline',
    #                       'core_mention_user_converstation.graphml')
    # tag_net('fed', 'pro_mention_timeline', 'data/pro_mention')
    # conversation('fed', 'pro_mention_timeline', 'timeline', 'core_mention_user_converstation.graphml')
    # rebuild_converstation('fed', 'pro_mention_timeline',
    #                       'data/pro_converstation.graphml', 'data/pro_converstation_tids.txt')

    # out_tid_uid('fed', 'pro_mention_timeline')
    # extract_network('fed', 'pro_mention_timeline', 'pro_mention_bnet', 'ED')
    networks('fed', 'pro_mention_bnet')





