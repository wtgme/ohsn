# -*- coding: utf-8 -*-
"""
Created on 10:33 PM, 3/1/17

@author: tw

This is explore the community of ED and their common followees
who are they?
What are they talk about?
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
import operator
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

Rake = RAKE.Rake('stoplist/SmartStoplist.txt')

def keywords(text):
    # Extract keywords from user profile
    keywords = []
    keywordcandidates = Rake.run(text)
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
            if n1 in prorec:
                set_map[n1id] = 1
                set_map[n2id] = 2
            else:
                set_map[n1id] = -1
                set_map[n2id] = -2
    g = Graph(len(name_map), directed=True)
    g.vs["name"] = list(sorted(name_map, key=name_map.get)) # return keys ordered by values
    g.add_edges(list(edges))
    g.es["weight"] = 1
    od = collections.OrderedDict(sorted(set_map.items()))
    # print od
    # print od.values()
    g.vs["set"] = od.values()
    gt.summary(g)

    g.vs['deg'] = g.indegree()
    nodes = []
    for v in g.vs:
        if v['set']==1 or v['set']==-1:
            nodes.append(v)
        elif v['deg'] > 3:
            nodes.append(v)
        else:
            pass
    print 'Filtered nodes: %d' %len(nodes)
    g = g.subgraph(nodes)
    gt.summary(g)


    g.write_graphml('rec-proed-follow.graphml')

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
    precision = metrics.precision_score( true_classes, pred_classes, average=average )
    recall = metrics.recall_score( true_classes, pred_classes, average=average )
    f1 = metrics.f1_score( true_classes, pred_classes, average=average )
    accuracy = metrics.accuracy_score( true_classes, pred_classes )
    return precision, recall, f1, accuracy


def classify_recovery_proed():
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




if __name__ == '__main__':
    # ED_followee()
    # ed_follow_net()
    # ed_follow_community('ed-retweet-follow'+'.graphml')
    # profile_cluster('ed-retweet'+'.graphml')

    # classify_recovery_proed()
    recover_proed_community()
