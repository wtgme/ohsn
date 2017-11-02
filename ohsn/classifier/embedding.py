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


def read_tweets(dbname, colname, timecol):
    '''Read tweets, excluding retweets'''
    db = dbt.db_connect_no_auth(dbname)
    # col = db[colname]
    timelines = db[timecol]
    # documents = list()
    # ids = list()
    # for user in col.find({'timeline_count': {'$gt': 0}}, ['id'], no_cursor_timeout=True):
        # uid = user['id']
    for tweet in timelines.find({'retweeted_status': {'$exists': False}}, no_cursor_timeout=True):
        text = tweet['text'].encode('utf8')
        uid = tweet['user']['id']
        # replace RT, @, and Http://
        text = text.strip().lower()
        text = re.sub(r"(?:(rt\ ?@)|@|https?://)\S+", "", text) # replace RT @, @ and http:// keep hashtag but remove
        words = tokenizer.tokenize(text)
        # Any text with fewer than 50 words should be looked at with a certain degree of skepticism.
        if len(words) > 5:
            print ('%d\t%d\t%s') %(uid, tweet['id'], ' '.join(words))
    #             ids.append(uid)
    #             documents.append(words)
    # pickle.dump(ids, open('data/sen_ids.pick', 'w'))
    # pickle.dump(documents, open('data/sen.pick', 'w'))


if __name__ == '__main__':
    # follow_network('fed', 'net', 'data/fed_follow.txt')
    # behavior_network('fed', 'bnet', 'data/fed_')
    read_tweets('fed', 'com', 'timeline')

    # text = '''The reason why I'm always broke AF. 🙍🎨 #PerksOfBeingaArchiStudent https://t.co/qo2RQMyrgA'''
    # text = text.strip().lower()
    # text = re.sub(r"(?:(rt\ ?@)|@|https?://)\S+", "", text) # replace RT @, @ and http:// keep hashtag but remove
    # words = tokenizer.tokenize(text)
    # print words