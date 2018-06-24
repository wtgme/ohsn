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
import ohsn.api.lookup as userlook
from ohsn.api import timelines
import pymongo
import math
import numpy as np
import pandas as pd
import ohsn.util.graph_util as gt
import ohsn.networkminer.timeline_network_miner as timiner
import pickle
from collections import Counter
from matplotlib import cm
import matplotlib.colors

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
    topic_tids = [int(uid) for uid in tid_topicid.keys()]
    filter = {'$where': 'this.entities.user_mentions.length>0',
                'id': {'$in': topic_tids},
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

            fw.write('%s %s %d\n' %(source_vertex['name'],
                                     target_vertex['name'],
                                     e['weight']))
    return node_attrs


def networks(dbname, bnet='all_pro_bnet'):
    # out networks to multiplex process
    # all_uids = iot.get_values_one_field('fed', 'ed_tag', 'user.id')
    # all_uids_count = Counter(all_uids)
    # uids = [key for key in all_uids_count]
    topics = [1, 3, 7, 15, 21] # [35, 3, 2, 14, 25]
    colrs = ["#fc8d62", "#8da0cb", "#e78ac3", '#a6d854', '#ffd92f', '#F2F2F2']
    names = ['Mental', 'Social', 'Fitness', 'Body', 'Thinspo', 'AGG.']
    # g = gt.load_beh_network_filter(dbname, bnet, btype='communication')
    # g.write_graphml('pro_mentionall'+'.graphml')
    # for i, tag in enumerate(topics):
    #     g = gt.load_beh_network_filter(dbname, bnet, btype='communication', filter={'tags': tag})
    #     g.write_graphml('pro_mention'+str(tag)+'.graphml')

    gall = gt.Graph.Read_GraphML('pro_mentionall'+'.graphml')
    core = gall.k_core(4)
    core_name = core.vs['name']

    # core_name = gall.vs['name']
    # for i, tag in enumerate(topics):
    #     g = gt.Graph.Read_GraphML('pro_mention'+str(tag)+'.graphml')
    #     core_name = set(core_name).intersection(set(g.vs['name']))
    # np.random.shuffle(core_name)
    # core_name = list(core_name)[:2000]
    print '------', len(core_name)
    gs = []
    for i, tag in enumerate(topics):
        g = gt.Graph.Read_GraphML('pro_mention'+str(tag)+'.graphml')
        g = g.subgraph(g.vs.select(name_in=core_name))
        for v in g.vs():
            v['name'] = str(1 + core_name.index(v['name']))
        gs.append(g)

    uidlist = {}
    name_coms = []
    for i, g in enumerate(gs):
        # g = g.as_undirected(mode="collapse", combine_edges='sum')
        # g = g.as_undirected()
        # com = g.community_infomap(edge_weights='weight')
        # com = udirg.community_multilevel(weights='weight', return_levels=False)
        # com = udirg.community_multilevel(return_levels=False)
        # name_com = dict(zip(g.vs['name'], com.membership))
        # print len(set(com.membership))
        # name_coms.append(name_com)
        uidlist = out_graph_edges(g, 'pro_mention'+str(topics[i])+'.edge', uidlist)

    with open('pro_mention.node', 'wb') as fw:
        fw.write('nodeID nodeLabel\n')
        for i, name in enumerate(core_name):
            fw.write(str(i+1) + ' ' + name + '\n')

    # https://matplotlib.org/examples/color/colormaps_reference.html
    with open('pro_mention.node.color.txt', 'wb') as fw:
        fw.write('nodeID layerID color size\n')
        for i, name_com in enumerate(name_coms):
            colrset = set(name_com.values())
            print len(colrset)
            cmap = cm.get_cmap('gist_rainbow', len(colrset))
            for key, value in name_com.items():
                rgb = cmap(value)[:3]
                fw.write(key + ' ' + str(i+1)  + ' "' + matplotlib.colors.rgb2hex(rgb) + '" 5\n')

    with open('pro_mention.edge.color.txt', 'wb') as fw:
        fw.write('nodeID.from layerID.from nodeID.to layerID.to color size\n')
        for i, top in enumerate(topics):
            fr = open('pro_mention'+str(top)+'.edge', 'r')
            for line in fr.readlines():
                n1, n2, we = line.split()
                fw.write(n1 + ' ' + str(i+1) + ' ' + n2 + ' ' + str(i+1) + ' "' + colrs[i] + '" 5\n')


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

    g = gt.Graph.Read_GraphML('data/pro_mention_tag_undir.graphml')
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



def out_tid_uid_hashtags(filename='feds.tags.txt'):
    fo = open(filename, 'w')
    fo.write(str('tid') + '\t' + str('uid') + '\t' + str('created_at') + '\t' + str('retweet')  + '\t' + str('dbindex') + '\t' + 'tags' + '\n')
    filter = {}
    filter['$where'] = 'this.entities.hashtags.length>0'
    for dbindex, dbname in enumerate(['fed', 'fed2', 'fed3', 'fed4']):
        time = dbt.db_connect_col(dbname, 'timeline')
        for tweet in time.find(filter, no_cursor_timeout=True):
            tid = tweet['id']
            uid = tweet['user']['id']
            retweet = 0
            if 'retweeted_status' in row:
                retweet = 1
            created_at = tweet['created_at']
            hashtags = tweet['entities']['hashtags']
            hash_set = set()
            for hash in hashtags:
            # need no .encode('utf-8')
                tag = (hash['text'].encode('utf-8').lower().replace('_', '').replace('-', ''))
                hash_set.add(tag)
            tags = ' '.join(list(hash_set))
            fo.write(str(tid) + '\t' + str(uid) + '\t' + str(created_at) + '\t' + str(retweet)  + '\t' + str(dbindex) + '\t' + tags + '\n')
    fo.flush()
    fo.close()



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

def user_profiles(dbname, comname, userfile='data/actor.uid'):
    # # get profile infor for regression
    uids = pickle.load(open(userfile))
    print len(uids)
    com = dbt.db_connect_col(dbname, comname)
    newcom = dbt.db_connect_col(dbname, 'pro_mention_miss_com')


    # newcom.create_index("id", unique=True)
    # # Collect miss data
    # missuids, taguids = [], []
    # for uid in uids:
    #     user = com.find_one({'id': int(uid)})
    #     if user is None:
    #         missuids.append(int(uid))
    #     else:
    #         taguids.append(int(uid))
    # list_size = len(missuids)
    # print '%d users to process' %list_size
    # length = int(math.ceil(list_size/100.0))
    # for index in xrange(length):
    #     index_begin = index*100
    #     index_end = min(list_size, index_begin+100)
    #     userlook.lookup_user_list(missuids[index_begin:index_end], newcom, 1, 'N')

    # # Collect tweets for missing users
    # converstream = dbt.db_connect_col(dbname, 'pro_mention_timeline')
    # most_recenty = converstream.find().sort([('id', -1)]).limit(1)
    # oldest = converstream.find().sort([('id', 1)]).limit(1)
    # max_id = most_recenty[0]['id']
    # since_id = oldest[0]['id']
    # print most_recenty[0]
    # print oldest[0]
    # com = dbt.db_connect_col(dbname, 'pro_mention_miss_com')
    # timeline = dbt.db_connect_col(dbname, 'pro_mention_miss_timeline')

    # com.create_index([('timeline_scraped_times', pymongo.ASCENDING)])
    # timeline.create_index([('user.id', pymongo.ASCENDING),
    #                       ('id', pymongo.DESCENDING)])
    # timeline.create_index([('id', pymongo.ASCENDING)], unique=True)

    # print datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "\t" + 'Connect Twitter.com'
    # timelines.retrieve_timeline(com, timeline, max_id)
    # print datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'finish timeline for sample users'


    data = []
    fields = iot.read_fields()
    miss_count = 0
    print fields
    for uid in uids:
        user = com.find_one({'id': int(uid)})
        if user is not None:
            row = iot.get_fields_one_doc(user, fields)
            data.append(row)
        else:
            user = newcom.find_one({'id': int(uid)})
            if user is not None:
                row = iot.get_fields_one_doc(user, fields)
                data.append(row)
            else:
                miss_count += 1
    print miss_count, miss_count*1.0/len(uids)
    df = pd.DataFrame(data= data, columns=['uid', 'posemo', 'negemo', 'senti'])
    df.to_csv('data/emotions.csv')


def out_network_temp(dbname='fed', bnet='pro_mention_bnet'):
    bnet = dbt.db_connect_col(dbname, bnet)
    for link in bnet.find({}, no_cursor_timeout=True):
        print str(link['id0']) +'\t' + str(link['id1']) + '\t' + str(link['tags']) + '\t' + link['created_at'] + '\t' + str(link['statusid'])

def calculate_picture_ratios(dbname, timename, bnetname):
    times = dbt.db_connect_col(dbname, timename)
    net = dbt.db_connect_col(dbname, bnetname)
    topics = [1, 3, 7, 15, 21] # [35, 3, 2, 14, 25]
    all_times, picture = [0.0]*5, [0.0]*5
    for b in net.find({}, no_cursor_timeout=True):
        tid = b['statusid']
        index = topics.index(b['tags'])
        tweet = times.find_one({'id': tid})
        if tweet:
            # print tweet
            if 'media' in tweet['entities']:
                picture[index] += 1
            all_times[index] += 1
    print all_times
    print picture
    print np.array(picture)/np.array(all_times)


def read_new_account():
    # how many users are new accounts
    com = dbt.db_connect_col('fed', 'com')
    misscom = dbt.db_connect_col('fed', 'pro_mention_miss_com')

    newaccounts = set()
    for db in [com, misscom]:
        for user in db.find():
            profile = user['description']
            if 'new account' in profile.lower():
                newaccounts.add(user['id'])
    print len(newaccounts)

    for i in [1,3,7,15,21]:
        g = gt.Graph.Read_GraphML('pro_mention'+str(i) + '.graphml')
        allc = len(g.vs)
        c = 0
        for v in g.vs['name']:
            uid = int(v)
            if uid in newaccounts:
                c += 1
        print i, allc, c, c*1.0/allc


if __name__ == '__main__':
    # constrcut_data()
    # fed_all_tag_topic()
    # tag_net('fed', 'pro_timeline', 'allpro')
    # tag_net('fed', 'pro_timeline', 'data/allpro')
    # extract_network('fed', 'pro_timeline', 'all_pro_bnet', 'ED')

    # networks('fed')
    # data_transf('data/pro4.graphml')
    # tag_activity('fed', 'pro_mention_timeline')

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
    # networks('fed', 'pro_mention_bnet')

    # user_profiles('fed', 'com')

    # out_network_temp()
    # calculate_picture_ratios('fed', 'pro_mention_timeline', 'pro_mention_bnet')

    read_new_account()
