# -*- coding: utf-8 -*-
"""
Created on 10:33 PM, 3/1/17

@author: tw

This is explore the community of ED and their common followees
who are they?
What are they talk about?

Tried: using sentiment on recovery to select pro-ed and pro-recoery users, NOT working.
"""
import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))


import ohsn.util.graph_util as gt
import ohsn.util.db_util as dbt
import ohsn.util.io_util as iot
import pymongo
import ohsn.api.profiles_check as pc
from nltk import FreqDist
from nltk.tree import Tree
from nltk import ne_chunk, pos_tag, word_tokenize
import RAKE
from nltk.tokenize import RegexpTokenizer
import numpy as np
from sklearn.cluster import AgglomerativeClustering
from gensim.models.doc2vec import Doc2Vec
import multiprocessing
from gensim.models.doc2vec import TaggedDocument
from gensim.test.test_doc2vec import ConcatenatedDoc2Vec
from sklearn import linear_model, metrics
from ohsn.edrelated import edrelatedcom
from igraph import *
import collections
import re
from pattern.en import sentiment
import seaborn as sns
import matplotlib.pyplot as plt
from afinn import Afinn
import pandas as pd

# Rake = RAKE.Rake('stoplist/SmartStoplist.txt')
tokenizer = RegexpTokenizer(r'\w+')

def keywords(text):
    # Extract keywords from user profile
    keywords = []
    keywordcandidates = Rake.run(text)
    # print keywordcandidates
    for keyword in keywordcandidates[0:3]:
        keywords.append(keyword[0])
    return keywords

def entity(text):
    # Identify named entities in profiles
    chunked = ne_chunk(pos_tag(word_tokenize(text)))
    prev = None
    continuous_chunk = []
    current_chunk = []
    for i in chunked:
        if type(i) == Tree:
            current_chunk.append(" ".join([token for token, pos in i.leaves()]))
        elif current_chunk:
            named_entity = " ".join(current_chunk)
            if named_entity not in continuous_chunk:
                continuous_chunk.append(named_entity)
                current_chunk = []
        else:
            continue
    return continuous_chunk


def ed_follow_net():
    # construct ED and their followee network
    g = gt.load_network('fed', 'follownet')
    g.vs['deg'] = g.indegree()
    users = set(iot.get_values_one_field('fed', 'scom', 'id'))
    nodes = []
    for v in g.vs:
        if int(v['name']) in users:
            nodes.append(v)
        elif v['deg'] > 5:
            nodes.append(v)
        else:
            pass
    print 'Filtered nodes: %d' %len(nodes)
    g = g.subgraph(nodes)
    gt.summary(g)
    g.write_graphml('ed-friend'+'.graphml')

    # sbnet have extended all interactions posted by ED users
    edusers = set(g.vs['name'])
    for btype in ['retweet', 'reply', 'mention']:
        gb = gt.load_beh_network('fed', 'sbnet', btype)
        gt.summary(gb)
        nodes = []
        for v in gb.vs:
            if v['name'] in edusers:
                nodes.append(v)
        gb = gb.subgraph(nodes)
        gt.summary(gb)
        gb.write_graphml('ed-'+btype+'-follow.graphml')


def recover_proed_community():
    # pro-recovery and pro-ed users, and their outlinked communities
    prorec = edrelatedcom.rec_user('fed', 'scom')
    proed = edrelatedcom.proed_users('fed', 'scom')
    cols = dbt.db_connect_col('fed', 'follownet')
    name_map, edges, set_map = {}, set(), {}
    for row in cols.find({},no_cursor_timeout=True):
        n1 = str(row['follower'])
        if n1 in prorec or n1 in proed:
            n2 = str(row['user'])
            n1id = name_map.get(n1, len(name_map))
            name_map[n1] = n1id
            n2id = name_map.get(n2, len(name_map))
            name_map[n2] = n2id
            edges.add((n1id, n2id))
    g = Graph(len(name_map), directed=True)
    g.vs["name"] = list(sorted(name_map, key=name_map.get)) # return keys ordered by values
    g.add_edges(list(edges))
    g.es["weight"] = 1
    g.vs["set"] = 0
    for v in g.vs:
        if v['name'] in prorec:
            v['set'] = 1
        elif v['name'] in proed:
            v['set'] = -1
    gt.summary(g)

    g.vs['deg'] = g.indegree()
    nodes = []
    for v in g.vs:
        if v['set'] == 1 or v['set'] == -1:
            nodes.append(v)
        elif v['deg'] > 3:
            nodes.append(v)
        else:
            pass
    print 'Filtered nodes: %d' %len(nodes)
    g = g.subgraph(nodes)
    gt.summary(g)
    g.write_graphml('rec-proed-follow.graphml')

    # sbnet have extended all interactions posted by ED users
    edusers = set(g.vs['name'])
    for btype in ['retweet', 'reply', 'mention']:
        gb = gt.load_beh_network('fed', 'sbnet', btype)
        gt.summary(gb)
        nodes = []
        for v in gb.vs:
            if v['name'] in edusers:
                nodes.append(v)
        gb = gb.subgraph(nodes)
        for v in gb.vs:
            v['set'] = g.vs.find(name=v['name'])['set']
        gt.summary(gb)
        gb.write_graphml('rec-proed-'+btype+'.graphml')


def recover_proed_inter():
    # Compare difference between pro-ed and pro-recovery uses in social networking
    prorec, proed = edrelatedcom.rec_proed() ## based on profiles
    com = dbt.db_connect_col('fed', 'scom')
    g = gt.load_network('fed', 'snet')
    data = []

    for node in g.vs:
        uid = node['name']
        user = com.find_one({'id': int(uid)})
        followeecount = user['friends_count']
        followercount = user['followers_count']
        followees = set([g.vs[v]['name'] for v in g.successors(uid)])
        followers = set([g.vs[v]['name'] for v in g.predecessors(uid)])
        recc_followee, proc_followee, edc_followee = 0.0, 0.0, 0.0
        for u in followees:
            if u in prorec:
                recc_followee += 1
            elif u in proed:
                proc_followee += 1
            else:
                edc_followee += 1
        if followeecount != 0:
            recc_followee /= followeecount
            proc_followee /= followeecount
            edc_followee /= followeecount
        else:
            print 'Followee number is zero', uid
        otherc_followee = 1 - recc_followee - proc_followee - edc_followee

        recc_follower, proc_follower, edc_follower = 0.0, 0.0, 0.0
        for u in followers:
            if u in prorec:
                recc_follower += 1
            elif u in proed:
                proc_follower += 1
            else:
                edc_follower += 1
        if followercount != 0:
            recc_follower /= followercount
            proc_follower /= followercount
            edc_follower /= followercount
        else:
            print 'Follower number is zero', uid
        otherc_follower = 1 - recc_follower - proc_follower - edc_follower

        if uid in prorec:
            data.append(['Rec', recc_followee, 'Rec-Followees'])
            data.append(['Rec', proc_followee, 'Ped-Followees'])
            data.append(['Rec', edc_followee, 'ED-Followees'])
            data.append(['Rec', otherc_followee, 'Oth-Followees'])

            data.append(['Rec', recc_follower, 'Rec-Followers'])
            data.append(['Rec', proc_follower, 'Ped-Followers'])
            data.append(['Rec', edc_follower, 'ED-Followers'])
            data.append(['Rec', otherc_follower, 'Oth-Followers'])

        elif uid in proed:
            data.append(['Ped', proc_followee, 'Ped-Followees'])
            data.append(['Ped', recc_followee, 'Rec-Followees'])
            data.append(['Ped', edc_followee, 'ED-Followees'])
            data.append(['Ped', otherc_followee, 'Oth-Followees'])

            data.append(['Ped', proc_follower, 'Ped-Followers'])
            data.append(['Ped', recc_follower, 'Rec-Followers'])
            data.append(['Ped', edc_follower, 'ED-Followers'])
            data.append(['Ped', otherc_follower, 'Oth-Followers'])
        else:
            pass
    df = pd.DataFrame(data, columns=['Group', 'Proportion', 'Feature'])
    df.to_csv('inter.csv')
    sns.set(style="whitegrid", palette="pastel", color_codes=True)
    sns.boxplot(x="Feature", y="Proportion", hue="Group", data=df, palette="PRGn")
    sns.despine(offset=10, trim=True)
    # plt.ylim(0, 0.8)
    # sns.violinplot(x="Feature", y="Values", hue="Group", data=df, split=True,
    #            inner="quart", palette="PRGn")
    # sns.despine(left=True)
    plt.show()


def compare_weights():
    #Compare distributions of CW and GW between pro-ed and pro-recovery users
    prorec, proed = edrelatedcom.rec_proed() ## based on profiles
    for users in [prorec, proed]:
        field = 'text_anal.cw.value'
        cw = iot.get_values_one_field('fed', 'scom', field, {'id_str': {'$in': users},
                                    field: {'$exists': True}})
        field = 'text_anal.gw.value'
        gw = iot.get_values_one_field('fed', 'scom', field, {'id_str': {'$in': users},
                                    field: {'$exists': True}})
        sns.distplot(cw, hist=False, label='CW')
        sns.distplot(gw, hist=False, label='GW')
        plt.show()
        # pol2 = iot.get_values_one_field('fed', 'recovery', "subjectivity")
        # sns.distplot(pol2)




def compare_opinion():
    # Compre pro-recovery and pro-ed users in terms of interventions
    prorec, proed = edrelatedcom.rec_proed() ## based on profiles
    rec_times = dbt.db_connect_col('fed', 'recover')
    # afinn = Afinn(emoticons=True)
    rec_sen, ed_sen = [], []
    for i in xrange(2):
        users = [prorec, proed][i]
        for uid in users:
            textmass = ''
            for tweet in rec_times.find({'user.id': int(uid)}):
                if 'retweeted_status' in tweet:
                    continue
                elif 'quoted_status' in tweet:
                    continue
                else:
                    text = tweet['text'].encode('utf8')
                    text = text.strip().lower()
                    text = re.sub(r"(?:(rt\ ?@)|@|https?://)\S+", "", text) # replace RT @, @ and http://
                    textmass += " " + text
            # sent = afinn.score(textmass)
            sent = sentiment(textmass)[0]
            if sent>50:
                print uid
            [rec_sen, ed_sen][i].append(sent)
    sns.distplot(rec_sen, hist=False, label='Pro-recovery')
    sns.distplot(ed_sen, hist=False, label='Pro-ED')
    plt.show()



def recovery_hashtag():
    dbname = 'fed'
    # select recovery users based on hashtags
    # Store in the databases
    # com = dbt.db_connect_col('fed', 'com')
    times = dbt.db_connect_col(dbname, 'timeline')
    tagproed = dbt.db_connect_col(dbname, 'proed_tag')
    tagproed.create_index([('user.id', pymongo.ASCENDING),
                          ('id', pymongo.DESCENDING)])
    tagproed.create_index([('id', pymongo.ASCENDING)], unique=True)

    tagprorec = dbt.db_connect_col(dbname, 'prorec_tag')
    tagprorec.create_index([('user.id', pymongo.ASCENDING),
                          ('id', pymongo.DESCENDING)])
    tagprorec.create_index([('id', pymongo.ASCENDING)], unique=True)

    # for user in com.find():
    # for tweet in times.find({'user.id': user['id'], '$where': 'this.entities.hashtags.length>0'}):
    for tweet in times.find({'$where': 'this.entities.hashtags.length>0'}, no_cursor_timeout=True):
        hashtags = tweet['entities']['hashtags']
        for hash in hashtags:
            value = hash['text'].encode('utf-8').lower().replace('_', '').replace('-', '')
            if 'recover' in value:
                try:
                    tagprorec.insert(tweet)
                except pymongo.errors.DuplicateKeyError:
                    pass
            if 'proed' in value or 'proana' in value \
                    or 'proanamia' in value or 'promia' in value:
                try:
                    tagproed.insert(tweet)
                except pymongo.errors.DuplicateKeyError:
                    pass

def combine_rec_ped_hashtags():
    # Move pro-recovery and proed tweets together
    pall_tag = dbt.db_connect_col('fed', 'pall_tag')
    pall_tag.create_index([('user.id', pymongo.ASCENDING),
                          ('id', pymongo.DESCENDING)])
    pall_tag.create_index([('id', pymongo.ASCENDING)], unique=True)

    ped = dbt.db_connect_col('fed', 'proed_tag')
    rec = dbt.db_connect_col('fed', 'prorec_tag')

    for col in [ped, rec]:
        for tweet in col.find():
            try:
                pall_tag.insert(tweet)
            except pymongo.errors.DuplicateKeyError:
                pass

def hashtag_users():
    com = dbt.db_connect_col('fed', 'com')
    times_ped = list(set(iot.get_values_one_field('fed', 'proed_tag', 'user.id')))
    times_rec = list(set(iot.get_values_one_field('fed', 'prorec_tag', 'user.id')))
    newtime = dbt.db_connect_col('fed', 'tag_com')
    newtime.create_index([('id', pymongo.ASCENDING)], unique=True)

    for users in [times_ped, times_rec]:
        for uid in users:
            user = com.find_one({'id': uid})
            try:
                newtime.insert(user)
            except pymongo.errors.DuplicateKeyError:
                pass


def hashtag_users_label_proed():
    # label all of users who have proed hashtags as selected
    com = dbt.db_connect_col('fed', 'tag_com')
    times_ped = list(set(iot.get_values_one_field('fed', 'proed_tag', 'user.id')))

    for uid in times_ped:
        com.update({'id': uid}, {'$set': {'ped_tageted': True}}, upsert=False)



def network_pro_hashtags():
    # Extract interaction networks from proed and pro-recoveryed hashtaged tweeets
    # Select only recovery users who have hashtags from ED hashtag topics
    # rec_tag_users = set(iot.get_values_one_field('fed', 'tag_com', 'id', {'rec_tageted': True}))
    # ped_tag_users = set(iot.get_values_one_field('fed', 'tag_com', 'id', {'ped_tageted': True}))
    rec_tag_users = set(iot.get_values_one_field('fed', 'prorec_tag_refine', 'user.id'))
    ped_tag_users = set(iot.get_values_one_field('fed', 'proed_tag', 'user.id'))

    only_ped = ped_tag_users - rec_tag_users
    only_rec = rec_tag_users - ped_tag_users
    # all_users = list(rec_tag_users.union(ped_tag_users))
    for btype in ['retweet', 'communication']:
        gb = gt.load_beh_network('fed', 'bnet_tag_refine', btype)
        for v in gb.vs:
            if int(v['name']) in only_ped:
                v['set'] = -1
            elif int(v['name']) in only_rec:
                v['set'] = 1
            else:
                v['set'] = 0
        gt.summary(gb)
        gb.write_graphml('rec-proed-'+btype+'-hashtag-non-refine.graphml')






def pro_tag_user():
    # get users with pro-ed and pro-recovery hashtags
    proed = set(iot.get_values_one_field('fed', 'proed_tag', 'user.id'))
    prorec = set(iot.get_values_one_field('fed', 'prorec_tag', 'user.id'))
    print len(proed), len(prorec), len(proed.intersection(prorec))
    print len(proed-prorec), len(prorec-proed)
    print prorec-proed
    return ([str(i) for i in proed-prorec],
            [str(i) for i in prorec-proed],
            [str(i) for i in proed.intersection(prorec)])



def recover_proed_community_all_connection():
    '''
    First filter users: pro-recovery and pro-ed, as well as their followings.
    Construct interaction networks among these users, including the outlinks from followings to pro-* users
    :return:
    '''
    # Filtering users
    # prorec, proed = edrelatedcom.rec_proed() ## based on profiles
    # prorec, proed = filter_recovery_sentiment() # based on tweets' sentiment
    # users = iot.get_values_one_field('fed', 'recover', 'user.id') # based on tweet content
    # prorec = [str(i) for i in users]
    # cols = dbt.db_connect_col('fed', 'follownet')

    proed, prorec, proboth = pro_tag_user() # based on hashtags

    cols = dbt.db_connect_col('fed', 'snet')
    name_map, edges, set_map = {}, set(), {}
    for row in cols.find({}, no_cursor_timeout=True):
        n1 = str(row['follower'])
        # if n1 in prorec or n1 in proed:
        n2 = str(row['user'])
        n1id = name_map.get(n1, len(name_map))
        name_map[n1] = n1id
        n2id = name_map.get(n2, len(name_map))
        name_map[n2] = n2id
        edges.add((n1id, n2id))
    g = Graph(len(name_map), directed=True)
    g.vs["name"] = list(sorted(name_map, key=name_map.get)) # return keys ordered by values
    g.add_edges(list(edges))
    g.es["weight"] = 1
    g.vs["set"] = 0
    for v in g.vs:
        if v['name'] in prorec:
            v['set'] = 1
        elif v['name'] in proed:
            v['set'] = 2
        elif v['name'] in proboth:
            v['set'] = 3
    gt.summary(g)

    # g.vs['deg'] = g.indegree()
    # nodes = []
    # for v in g.vs:
    #     if v['set'] == 1 or v['set'] == -1:
    #         nodes.append(v)
    #     elif v['deg'] > 3:
    #         nodes.append(v)
    #     else:
    #         pass
    # print 'Filtered nodes: %d' %len(nodes)
    # g = g.subgraph(nodes)
    # gt.summary(g)

    g.write_graphml('rec-proed-follow-core-hashtag.graphml')


    # sbnet have extended all interactions posted by ED users
    edusers = [int(v['name']) for v in g.vs]
    # gf = gt.load_network_subset('fed', 'net')
    for btype in ['retweet', 'reply', 'mention']:
        gb = gt.load_beh_network_subset(edusers, 'fed', 'sbnet', btype)
        for v in gb.vs:
            v['set'] = g.vs.find(name=v['name'])['set']
        gt.summary(gb)
        gb.write_graphml('rec-proed-'+btype+'-core-hashtag.graphml')



def recover_proed_interaction():
    # interaction network of pro-recovery and pro-ed users
    prorec = edrelatedcom.rec_user('fed', 'scom')
    proed = edrelatedcom.proed_users('fed', 'scom')
    btype_dic = {'retweet': [1], 'reply': [2], 'mention': [3], 'communication': [2, 3]}
    for btype in ['retweet', 'reply', 'mention']:
        cols = dbt.db_connect_col('fed', 'sbnet')
        name_map, edges, set_map = {}, {}, {}
        for row in cols.find({'type': {'$in': btype_dic[btype]}}, no_cursor_timeout=True):
            n1 = str(row['id0'])
            n2 = str(row['id1'])
            if n1 in prorec or n1 in proed:
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
        g.vs["set"] = 0
        for v in g.vs:
            if v['name'] in prorec:
                v['set'] = 1
            elif v['name'] in proed:
                v['set'] = -1
        gt.summary(g)


        edges = g.es.select(weight_gt=3)
        edge_nodes = []
        for edge in edges:
            source_vertex_id = edge.source
            target_vertex_id = edge.target
            source_vertex = g.vs[source_vertex_id]
            target_vertex = g.vs[target_vertex_id]
            edge_nodes.append(source_vertex['name'])
            edge_nodes.append(target_vertex['name'])

        nodes = []
        for v in g.vs:
            if v['set'] == 1 or v['set'] == -1:
                nodes.append(v)
            elif v['name'] in edge_nodes:
                nodes.append(v)
            else:
                pass
        print 'Filtered nodes: %d' %len(nodes)
        g = g.subgraph(nodes)
        gt.summary(g)
        g.write_graphml('rec-proed-'+btype+'.graphml')


def ed_follow_community(file_path):
    # inspect keywords of user profiles in different communities
    g = gt.Graph.Read_GraphML(file_path)
    gt.summary(g)
    g = g.as_undirected(combine_edges=dict(weight="sum"))
    components = g.clusters()
    g = components.giant()
    gt.summary(g)

    com = dbt.db_connect_col('fed', 'com')
    ml = g.community_fastgreedy(weights='weight').as_clustering()
    # ml = g.community_multilevel(weights='weight')
    common_words = []
    fdist_all = FreqDist()
    for cluster in ml:
        print len(cluster)
        fdist = FreqDist()
        for uid in cluster:
            user = com.find_one({'id': int(g.vs[uid]['name'])}, ['description'])
            profile = user['description']
            if profile:
                # text = ' '.join(pc.tokenizer_stoprm(profile))
                tokens = pc.tokenizer_stoprm(profile)
                for word in tokens:
                    fdist[word] += 1
                    fdist_all[word] += 1
        common_words.append(fdist)
    for fd in common_words:
        w_tfidf = []
        # print fd.most_common(20)
        for (word, freq) in fd.most_common(20):
            allfreq = fdist_all[word]
            # print word, freq, allfreq
            w_tfidf.append((word, float(freq)/allfreq))
        sortedlist = sorted(w_tfidf, key=lambda x: x[1], reverse=True)
        print sortedlist



def ED_followee():
    # put all ED's followees in follownet
    net = dbt.db_connect_col('fed', 'net2')
    users = set(iot.get_values_one_field('fed', 'scom', 'id'))
    print len(users)
    tem = dbt.db_connect_col('fed', 'follownet')
    for re in net.find():
        if re['follower'] in users:
            try:
                tem.insert(re)
            except pymongo.errors.DuplicateKeyError:
                pass


def profile_cluster(filepath):
    # Clustering user based on word2vec of user profiles
    g = gt.Graph.Read_GraphML(filepath)
    gt.summary(g)
    g = g.as_undirected(combine_edges=dict(weight="sum"))
    components = g.clusters()
    g = components.giant()
    gt.summary(g)

    com = dbt.db_connect_col('fed', 'com')
    data = {}
    for uid in g.vs['name']:
        user = com.find_one({'id': int(uid)}, ['description'])
        profile = user['description']
        if profile:
            tokens = pc.tokenizer_stoprm(profile)
            data[uid] = tokens
    import gensim
    # dictionary = gensim.corpora.Dictionary(data.values())
    # dictionary.save('lda.dict')
    # corpus = [dictionary.doc2bow(text) for text in data.values()]
    # lda = gensim.LdaModel(corpus, num_topics=100, id2word=dictionary)
    word2vec = gensim.models.Word2Vec(data.values(), size=300, sg=1)

    X, y = [], []
    for node in g.vs:
        k = node['name']
        v = data[k]
        vect = np.zeros(300)
        count = 0
        for word in v:
            if word in word2vec:
                vect += word2vec[word]
                count += 1
        X.append(vect/count)
        y.append(k)
    X = np.asarray(X)
    print X.shape
    print X
    matrix = g.get_adjacency()
    # clustering = AgglomerativeClustering(connectivity=matrix._get_data())
    clustering = AgglomerativeClustering()
    clustering.fit(X)

    members = clustering.labels_
    comm = gt.VertexClustering(g,  membership=members)
    layout = g.layout("fr")
    gt.plot(comm, layout=layout, vertex_size=5)


def get_scores( true_classes, pred_classes, average):
    # classification evaluation
    precision = metrics.precision_score( true_classes, pred_classes, average=average )
    recall = metrics.recall_score( true_classes, pred_classes, average=average )
    f1 = metrics.f1_score( true_classes, pred_classes, average=average )
    accuracy = metrics.accuracy_score( true_classes, pred_classes )
    return precision, recall, f1, accuracy


def recovery_users_tweet():
    # gather recovery/treat related tweets
    # When construct control group, if they have retweet treatment, delete them
    com = dbt.db_connect_col('fed', 'scom')
    times = dbt.db_connect_col('fed', 'timeline')
    newtime = dbt.db_connect_col('fed', 'recover')
    newtime.create_index([('user.id', pymongo.ASCENDING),
                          ('id', pymongo.DESCENDING)])
    newtime.create_index([('id', pymongo.ASCENDING)], unique=True)

    for user in com.find(no_cursor_timeout=True):
        uid = user['id']
        for tweet in times.find({'user.id': uid}):
            # if 'retweeted_status' in tweet:
            #     continue
            # elif 'quoted_status' in tweet:
            #     continue
            # else:
            text = tweet['text'].encode('utf8')
            text = re.sub(r"(?:(RT\ ?@)|@|https?://)\S+", "", text) # replace RT @, @ and http://
            # if ('I' in text or ' me ' in text):
            text = text.strip().lower()
            if 'recover' in text or 'treatment' in text or 'therap' in text \
                   or 'doctor' in text:
                    # or 'healing' in text or 'therapy' in text or 'doctor' in text or 'hospital' in text:
                # print ' '.join(tweet['text'].split())
                try:
                    newtime.insert(tweet)
                except pymongo.errors.DuplicateKeyError:
                    pass


def recovery_user_treatment_tweet():
    # verify when 'treatment' in pro-recovery users timeline
    rec, proed = edrelatedcom.rec_proed() ## based on profiles
    times = dbt.db_connect_col('fed', 'timeline')
    count = 0
    for user in rec:
        flag = False
        for tweet in times.find({'user.id': int(user)}):
            if 'retweeted_status' in tweet:
                continue
            elif 'quoted_status' in tweet:
                continue
            else:
                text = tweet['text'].encode('utf8')
                text = re.sub(r"(?:(RT\ ?@)|@|https?://)\S+", "", text) # replace RT @, @ and http://
                text = text.strip().lower()
                if 'treatment' in text or 'therap' in text \
                       or 'doctor' in text:
                    print ' '.join(tweet['text'].split())
                    flag = True
        if flag:
            count += 1
            print user
    print len(rec), count


def recovery_sentiment():
    afinn = Afinn(emoticons=True)
    # analysis sentiments about recovery
    times = dbt.db_connect_col('fed', 'recovery')
    for tweet in times.find():

        text = tweet['text'].encode('utf8')
        text = text.strip().lower()
        text = re.sub(r"(?:(rt\ ?@)|@|https?://)\S+", "", text) # replace RT @, @ and http://
        sent = afinn.score(text)
        # sent = sentiment(text)
        times.update_one({'id': tweet['id']}, {'$set':{"polarity": sent[0]
            # , "subjectivity": sent[1]
                                                    }}, upsert=False)
    pol = iot.get_values_one_field('fed', 'recovery', "polarity")
    sns.distplot(pol)
    plt.show()
    # pol2 = iot.get_values_one_field('fed', 'recovery', "subjectivity")
    # sns.distplot(pol2)
    # plt.show()


def filter_recovery_sentiment():
    user_count, user_pol = {}, {}
    times = dbt.db_connect_col('fed', 'recovery')
    for tweet in times.find():
        uid = tweet['user']['id']
        pol = tweet['polarity']
        count = user_count.get(uid, 0.0)
        polv = user_pol.get(uid, 0.0)
        user_count[uid] = count + 1
        if pol > 0:
            print ' '.join(tweet['text'].split())
            user_pol[uid] = polv + 1
        elif pol < 0:
            user_pol[uid] = polv - 1
        else:
            user_pol[uid] = polv + 0
    user_list = [k for k, v in user_count.items() if v >= 3]
    print sum(user_pol[uid] > 0 for uid in user_list)
    print sum(user_pol[uid] < 0 for uid in user_list)
    rec, nonrec = [], []
    com = dbt.db_connect_col('fed', 'scom')
    for uid in user_list:
        if user_pol[uid] > 0:
            rec.append(str(uid))
            user = com.find_one({'id':uid})
            print 'Positive', user['id_str'], user['screen_name'], ' '.join(user['description'].split()).encode('utf-8')
        elif user_pol[uid] < 0:
            nonrec.append(str(uid))
            user = com.find_one({'id':uid})
            print 'Negative', user['id_str'], user['screen_name'], ' '.join(user['description'].split()).encode('utf-8')

    return rec, nonrec


def recovery_text(text):
    # identify recovery text
    sentences = re.split(r"\s*[;:`\"()?!{}]\s*|--+|\s*-\s+|''|\.\s|\.$|\.\.+|¡°|¡±", text)
    FLAG = False
    for sentence in sentences:
        if 'recover' in sentence:
            if 'not' not in sentence and 'don\'t' not in sentence and 'never' not in sentence \
                    and 'anti' not in sentence and 'non' not in sentence \
                    and 'relapse' not in sentence:
                FLAG = True
    return FLAG


def keywords_recovery_preed():
    # compare keywords in pro-recovery and pro-ed users' tweets
    prorec, proed = edrelatedcom.rec_proed()
    times = dbt.db_connect_col('fed', 'timeline')
    fdist_rec = FreqDist()
    fdist_ped = FreqDist()
    for user in prorec:
        for tweet in times.find({'user.id':int(user)}):
            text = tweet['text'].encode('utf8')
            # replace RT, @, # and Http://
            text = text.strip().lower()
            text = re.sub(r"(?:(rt\ ?@)|@|https?://)\S+", "", text) # replace RT @, @ and http://
            words = keywords(text)
            for word in words:
                fdist_rec[word] += 1
    for user in proed:
        for tweet in times.find({'user.id':int(user)}):
            text = tweet['text'].encode('utf8')
            # replace RT, @, # and Http://
            text = text.strip().lower()
            text = re.sub(r"(?:(rt\ ?@)|@|https?://)\S+", "", text) # replace RT @, @ and http://
            words = keywords(text)
            for word in words:
                fdist_ped[word] += 1
    print fdist_rec.most_common(50)
    print fdist_ped.most_common(50)


def classify_recovery_proed():
    # classification pro-recovery and pro-ed users
    prorec = edrelatedcom.rec_user('fed', 'scom')
    proed = edrelatedcom.proed_users('fed', 'scom')
    com = dbt.db_connect_col('fed', 'scom')
    documents = []
    for user in com.find():
        profile = user['description']
        if profile:
            tokens = pc.tokenizer_stoprm(profile)
            sentence = TaggedDocument(words=tokens, tags=[str(user['id'])])
            documents.append(sentence)
    cores = multiprocessing.cpu_count()
    size = 200
    window = 4
    simple_models = [
                # PV-DM w/concatenation - window=5 (both sides) approximates paper's 10-word total window size
                Doc2Vec(documents, dm=1, dm_concat=1, size=size, window=window, negative=5, hs=1, sample=1e-3, min_count=1, workers=cores),
                # PV-DBOW
                Doc2Vec(documents, dm=0, size=size, window=window, negative=5, hs=1, sample=1e-3, min_count=1, workers=cores),
                    ]
    model = ConcatenatedDoc2Vec([simple_models[1], simple_models[0]])
    X_train, y_train, X_test, y_test = [], [], [], []
    for doc in documents:
        tag = doc.tags[0]
        if (tag) in prorec:
            X_train.append(model.docvecs[tag])
            y_train.append(1)
        elif (tag) in proed:
            X_train.append(model.docvecs[tag])
            y_train.append(0)
        else:
            X_test.append(model.docvecs[tag])
            y_test.append(int(tag))
    print len(X_train)
    print len(X_test)
    print len(documents)
    logistic = linear_model.LogisticRegression(multi_class='multinomial', solver='newton-cg', n_jobs=multiprocessing.cpu_count())
    # svc_lin = SVC(kernel='linear', class_weight='balanced')
    logistic.fit(X_train, y_train)
    y_tlin = logistic.predict(X_train)
    y_lin = logistic.predict(X_test)
    for average in ['micro', 'macro']:
        train_precision, train_recall, train_f1, train_acc = get_scores(y_train, y_tlin, average)
        print "Train Prec (%s average): %.3f, recall: %.3f, F1: %.3f, Acc: %.3f" %( average,
                            train_precision, train_recall, train_f1, train_acc )

def test():
    # times = dbt.db_connect_col('fed', 'treat')
    # for tweet in times.find():
    #     print ' '.join(tweet['text'].split())

    #    text = """
 # The cause of eating disorders is not clear.[3] Both biological and environmental factors appear to play a role.[1][3] Cultural idealization of thinness is believed to contribute.[3] Eating disorders affect about 12 percent of dancers.[4] Those who have experienced sexual abuse are also more likely to develop eating disorders.[5] Some disorders such as pica and rumination disorder occur more often in people with intellectual disabilities. Only one eating disorder can be diagnosed at a given time.[2]
 #
 #               """
 #    print keywords(text)

    users = iot.get_values_one_field('fed', 'recover', 'user.id')
    prerec , proed = edrelatedcom.rec_proed()
    pusers = [str(i) for i in users]
    print len(pusers)
    print len(prerec)
    uoi = (set(pusers).intersection(set(prerec)))
    com = dbt.db_connect_col('fed', 'scom')
    for u in uoi:
        user = com.find_one({'id': int(u)})
        print user['screen_name']


if __name__ == '__main__':
    # ED_followee()
    # ed_follow_net()
    # ed_follow_community('ed-retweet-follow'+'.graphml')
    # profile_cluster('ed-retweet'+'.graphml')

    # classify_recovery_proed()
    # recover_proed_community()
    # recover_proed_community_all_connection()

 #    keywords_recovery_preed()
    # recover_proed_interaction()

    # recovery_users_tweet()
    # recovery_sentiment()
    # filter_recovery_sentiment()



    # recovery_user_treatment_tweet()
    # recovery_users_tweet()


    # recover_proed_inter()

    # compare_weights()

    # compare_opinion()
    recovery_hashtag()
    # pro_tag_user()

    # network_pro_hashtags()
    # combine_rec_ped_hashtags()
    # hashtag_users()
    # hashtag_users_label_proed()