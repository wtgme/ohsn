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
import pickle

tknzr = TweetTokenizer()


def read_profile(dbname, comname):
    db = dbt.db_connect_no_auth(dbname)
    col = db[comname]
    documents = []
    uids = []
    for user in col.find({}, ['id_str', 'description']):
        profile = user['description'].encode('utf8').lower()
        tokens = tknzr.tokenize(profile)
        if len(tokens) > 3:
            sentence = doc2vec.TaggedDocument(words=tokens, tags=[user['id_str']])
            uids.append(user['id_str'])
            documents.append(sentence)
    return documents, uids


def cluster(documents):
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



if __name__ == '__main__':
    # docs, uids = read_profile('fed', 'com')
    # cluster(docs)
    model = doc2vec.Doc2Vec.load('prof2vec')
    # print model.docvecs['4612122917']
    # print model.docvecs['3233608771']
    # mins = min_sim(model, uids)

    print model.docvecs.most_similar('4612122917')
    print model.docvecs.n_similarity(['4612122917'], ['1255478509'])
    print model.docvecs.n_similarity(['4612122917'], ['855558812'])
    print model.docvecs.n_similarity(['4612122917'], ['3063325095'])


