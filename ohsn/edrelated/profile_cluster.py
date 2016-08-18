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

tknzr = TweetTokenizer()


def read_profile(dbname, comname):
    db = dbt.db_connect_no_auth(dbname)
    col = db[comname]
    documents = []
    for user in col.find({}, ['id_str', 'description']):
        profile = user['description'].encode('utf8').lower()
        tokens = tknzr.tokenize(profile)
        if len(tokens) > 5:
            sentence = doc2vec.TaggedDocument(words=tokens, tags=[user['id_str']])
            documents.append(sentence)
    return documents


def cluster(documents):
    model = doc2vec.Doc2Vec(documents)
    model.save('prof2vec')


if __name__ == '__main__':
#    docs = read_profile('fed', 'com')
#    cluster(docs)
    model = doc2vec.Doc2Vec.load('prof2vec')
    print model.most_similar('2578594609')


