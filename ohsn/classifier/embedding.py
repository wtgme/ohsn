# -*- coding: utf-8 -*-
"""
Created on 9:45 PM, 10/26/17

@author: tw

Try to use network and word embeddings to classify users
"""

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))


import ohsn.util.io_util as iot
import ohsn.util.graph_util as gt
import ohsn.util.db_util as dbt
import re
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
import gensim, logging
import pandas as pd
import numpy as np
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
import pickle
tokenizer = RegexpTokenizer(r'\w+')

def follow_network(dbname, colname, filepath):
    '''out follow network'''
    g = gt.load_network(dbname, colname)
    with open(filepath, 'wb') as fw:
        for e in g.es:
            source_vertex_id = e.source
            target_vertex_id = e.target
            source_vertex = g.vs[source_vertex_id]
            target_vertex = g.vs[target_vertex_id]

            fw.write('%s\t%s\t%d\n' %('u'+source_vertex['name'],
                                     'u'+target_vertex['name'],
                                     e['weight']))


def behavior_network(dbname, colname, filepath):
    '''out retweet and communication network'''
    uids = iot.get_values_one_field(dbname, 'com', 'id')
    print len(uids)
    for beh in ['retweet', 'communication']:
        print beh
        g = gt.load_beh_network_subset(uids, dbname, colname, beh)
        with open(filepath+beh+'.txt', 'wb') as fw:
            for e in g.es:
                source_vertex_id = e.source
                target_vertex_id = e.target
                source_vertex = g.vs[source_vertex_id]
                target_vertex = g.vs[target_vertex_id]

                fw.write('%s\t%s\t%d\n' %('u'+source_vertex['name'],
                                         'u'+target_vertex['name'],
                                         e['weight']))


def read_tweets(dbname, timecol):
    '''Read tweets, excluding retweets'''
    db = dbt.db_connect_no_auth(dbname)
    # col = db[colname]
    timelines = db[timecol]
    # documents = list()
    # ids = list()
    # for user in col.find({'timeline_count': {'$gt': 0}}, ['id'], no_cursor_timeout=True):
        # uid = user['id']
    for tweet in timelines.find({'retweeted_status': {'$exists': False}}, no_cursor_timeout=True):
        hashtags = tweet['entities']['hashtags']
        hash_set = set()
        for hash in hashtags:
            hash_set.add(hash['text'].encode('utf-8').lower().replace('_', '').replace('-', ''))

        text = tweet['text'].encode('utf8')
        uid = tweet['user']['id']
        # replace RT, @, and Http://
        text = text.strip().lower()
        text = re.sub(r"(?:(rt\ ?@)|@|https?://)\S+", "", text) # replace RT @, @ and http:// keep hashtag but remove
        words = tokenizer.tokenize(text)
        # Any text with fewer than 50 words should be looked at with a certain degree of skepticism.
        if len(words) > 3:
            print ('%d\t%d\t%s\t%s') %(uid, tweet['id'], ' '.join(words), ' '.join(list(hash_set)))
    #             ids.append(uid)
    #             documents.append(words)
    # pickle.dump(ids, open('data/sen_ids.pick', 'w'))
    # pickle.dump(documents, open('data/sen.pick', 'w'))


def word2vec_tweets(dbname, colname, timecol):
    # load word2vec of tweets and represent each users as the vector of word2vec
    model = gensim.models.Word2Vec.load('word2vec/fed_w2v.model')
    db = dbt.db_connect_no_auth(dbname)
    col = db[colname]
    timelines = db[timecol]
    for user in col.find({'timeline_count': {'$gt': 0}}, ['id'], no_cursor_timeout=True):
        uid = user['id']
        user_vec = []
        for tweet in timelines.find({'user.id': uid}, no_cursor_timeout=True):
            text = tweet['text'].encode('utf8')
            # replace RT, @, and Http://
            text = text.strip().lower()
            text = re.sub(r"(?:(rt\ ?@)|@|https?://)\S+", "", text) # replace RT @, @ and http:// keep hashtag but remove
            words = tokenizer.tokenize(text)
            # Any text with fewer than 50 words should be looked at with a certain degree of skepticism.
            # if len(words) > 5:
            for word in words:
                if word in model:
                    user_vec.append(model[word])
        if len(user_vec) > 0:
            vector = np.array(user_vec).mean(axis=0)
            col.update_one({'id': uid}, {'$set': {'w2v.mined': True, 'w2v.result': vector.tolist()}}, upsert=False)


def out_word2vec(dbname, colname):
    # out word2vec for tweets
    db = dbt.db_connect_col(dbname, colname)
    for user in db.find({'w2v': {'$exists': True}}, no_cursor_timeout=True):
        print str(user['id']) + '\t' + ' '.join([str(i) for i in user['w2v']['result']])

def out_core_ed_id(dbname, colname):
    # get user ids for core ED users as positive users
    # uids = iot.get_values_one_field(dbname, colname, 'id_str')
    # names = iot.get_values_one_field(dbname, colname, 'screen_name')

    db = dbt.db_connect_col(dbname, colname)
    users = {}
    for user in db.find({}, ['id', 'screen_name'], no_cursor_timeout=True):
        users[user['id']] = user['screen_name']
    print len(users)
    pickle.dump(users, open('fed_users.pick', 'w'))


def out_bio():
    dbnames = ['fed', 'fed2', 'fed3', 'fed4']
    data = []
    for i, dbname in enumerate(dbnames):
        com = dbt.db_connect_col(dbname, 'com')
        for user in com.find({'text_anal.cbmi': {'$exists': True}}):
            # print user['id']
            data.append([user['id'], user['text_anal']['cbmi']['value'], i])
    df = pd.DataFrame(data, columns=['uid', 'cbmi', 'time'])
    df.to_csv('data/feds-cbmi.csv')


if __name__ == '__main__':
    # follow_network('fed', 'net', 'data/fed_follow.txt')
    # behavior_network('fed', 'bnet', 'data/fed_')
    # read_tweets('fed', 'timeline')
    # read_tweets('fed', 'core_mention_timeline')
    # read_tweets('younger', 'timeline')
    # word2vec_tweets('fed', 'com', 'timeline')

    # text = '''The reason why I'm always broke AF. 🙍🎨 #PerksOfBeingaArchiStudent https://t.co/qo2RQMyrgA'''
    # text = text.strip().lower()
    # text = re.sub(r"(?:(rt\ ?@)|@|https?://)\S+", "", text) # replace RT @, @ and http:// keep hashtag but remove
    # words = tokenizer.tokenize(text)
    # print words

    # out_word2vec('fed', 'com')
    # out_core_ed_id('fed', 'com')
    out_bio()