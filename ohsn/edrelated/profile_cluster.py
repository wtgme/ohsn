# -*- coding: utf-8 -*-
"""
Created on 17:43, 18/08/16

@author: wt
"""
import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

from nltk.tokenize import TweetTokenizer
import ohsn.util.db_util as dbt
from gensim.models import doc2vec
from sklearn.cluster import AffinityPropagation
from sklearn.semi_supervised import LabelSpreading
from sklearn import metrics
import ohsn.api.profiles_check as check
import numpy as np
from sklearn.datasets.samples_generator import make_blobs
import pickle

tknzr = TweetTokenizer()


def read_profile(dbname, comname):
    db = dbt.db_connect_no_auth(dbname)
    col = db[comname]
    documents = []
    uids = []
    label_uids = []
    for user in col.find({}, ['id_str', 'description']):
        profile = user['description'].encode('utf8').lower()
        tokens = tknzr.tokenize(profile)
        if len(tokens) > 5:
            sentence = doc2vec.TaggedDocument(words=tokens, tags=[user['id_str']])
            uids.append(user['id_str'])
            documents.append(sentence)
            if check.check_ed_profile(user['description']):
                label_uids.append(user['id_str'])
    return documents, uids, label_uids


def docvec(documents):
    model = doc2vec.Doc2Vec(documents)
    model.save('prof2vec')


def min_sim(model, ulist):
    mins = 1.0
    for i in xrange(len(ulist)):
        ui = ulist[i]
        for j in xrange(i+1, len(ulist)):
            uj = ulist[j]
            sim = model.docvecs.n_similarity([ui], [uj])
            if sim < mins:
                mins = sim
    return mins


def propogation(model, uids, labeled_ids):
    X, y1, y2 = [], [], []
    pool = []
    for uid in labeled_ids:
        X.append(model.docvecs[uid])
        y1.append(1)
    for uid in uids:
        if uid not in labeled_ids:
            X.append(model.docvecs[uid])
            y2.append(-1)
    label_prop_model = LabelSpreading(kernel='knn', alpha=1.0)
    y2 = np.array(y2)
    y2[0:(len(y1)-1)] = 0
    print len(y1) + len(y2)
    for i in xrange(5):
        np.random.shuffle(y2)
        label_prop_model.fit(X, y1 + y2.tolist())
        pool.append(label_prop_model.transduction_)
    pickle.dump(pool, open('data/propagation.pick', 'w'))
    pool = pickle.load(open('data/propagation.pick', 'r'))
    pool = np.array(pool)
    for column in pool.T:
        print column
        # counts = np.bincount(column)
        # print np.argmax(counts)


def cluster(model, uids):
    ##############################################################################
    # Generate sample data
    X = []
    for uid in uids:
        X.append(model.docvecs[uid])
    labels_true = uids

    ##############################################################################
    # Compute Affinity Propagation
    af = AffinityPropagation(preference=-50).fit(X)
    pickle.dump(af, open('data/af.pick', 'w'))
    cluster_centers_indices = af.cluster_centers_indices_
    labels = af.labels_

    n_clusters_ = len(cluster_centers_indices)

    print('Estimated number of clusters: %d' % n_clusters_)
    print("Homogeneity: %0.3f" % metrics.homogeneity_score(labels_true, labels))
    print("Completeness: %0.3f" % metrics.completeness_score(labels_true, labels))
    print("V-measure: %0.3f" % metrics.v_measure_score(labels_true, labels))
    print("Adjusted Rand Index: %0.3f"
          % metrics.adjusted_rand_score(labels_true, labels))
    print("Adjusted Mutual Information: %0.3f"
          % metrics.adjusted_mutual_info_score(labels_true, labels))
    print("Silhouette Coefficient: %0.3f"
          % metrics.silhouette_score(X, labels, metric='sqeuclidean'))

    ##############################################################################
    # Plot result
    # import matplotlib.pyplot as plt
    # from itertools import cycle
    #
    # plt.close('all')
    # plt.figure(1)
    # plt.clf()
    #
    # colors = cycle('bgrcmykbgrcmykbgrcmykbgrcmyk')
    # for k, col in zip(range(n_clusters_), colors):
    #     class_members = labels == k
    #     cluster_center = X[cluster_centers_indices[k]]
    #     plt.plot(X[class_members, 0], X[class_members, 1], col + '.')
    #     plt.plot(cluster_center[0], cluster_center[1], 'o', markerfacecolor=col,
    #              markeredgecolor='k', markersize=14)
    #     for x in X[class_members]:
    #         plt.plot([cluster_center[0], x[0]], [cluster_center[1], x[1]], col)
    #
    # plt.title('Estimated number of clusters: %d' % n_clusters_)
    # plt.show()
    ###############################################################################

if __name__ == '__main__':
    docs, uids, label_ids = read_profile('fed', 'com')
    pickle.dump(uids, open('data/uids.pick', 'w'))
    pickle.dump(label_ids, open('data/luids.pick', 'w'))
    docvec(docs)
    model = doc2vec.Doc2Vec.load('prof2vec')
    uids = pickle.load(open('data/uids.pick', 'r'))
    label_ids = pickle.load(open('data/luids.pick', 'r'))

    # print model.docvecs['4612122917']
    # print model.docvecs['3233608771']
    # mins = min_sim(model, uids)
    # print model.docvecs.most_similar('4612122917')
    # print model.docvecs.n_similarity(['4612122917'], ['630629210'])
    # print model.docvecs.n_similarity(['4612122917'], ['1295904486'])
    # print model.docvecs.n_similarity(['4612122917'], ['1344770388'])

    print len(uids)
    print len(label_ids)
    # cluster(model, uids)
    propogation(model, uids, label_ids)

