# -*- coding: utf-8 -*-
"""
Created on 4:52 PM, 5/2/16

@author: tw
"""
import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
from gensim import corpora, models
from ohsn.util import db_util as dbt
import pickle
import re
from nltk.tokenize import RegexpTokenizer
from nltk import SnowballStemmer
import string
from nltk.corpus import stopwords
import logging

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
tknzr = RegexpTokenizer(r'\w+')
stemmer = SnowballStemmer("english")
rtgrex = re.compile(r'RT (?<=^|(?<=[^a-zA-Z0-9-\.]))@([A-Za-z0-9_]+):')  # for Retweet
mgrex = re.compile(r'(?<=^|(?<=[^a-zA-Z0-9-\.]))@([A-Za-z0-9_]+)')  # for mention
hgrex = re.compile(r'(?<=^|(?<=[^a-zA-Z0-9]))#([A-Za-z0-9_]+)')  # for hashtags
# hgrex = re.compile(r'(?<=^|(?<=[^a-zA-Z0-9-\.]))#([A-Za-z0-9_]+)')  # for hashtags
ugrex = re.compile(r'(https?://[^\s]+)')  # for url

cachedStopWords = stopwords.words("english")
printable = set(string.printable)


def process(text):
    text = text.encode('utf8')
    '''Ignore tweets with URLs'''
    if ugrex.search(text) is None:
        '''replace RT, @, # and Http://'''
        text = rtgrex.sub('', text)
        text = mgrex.sub('', text)
        # text = hgrex.sub('', text)
        # text = ugrex.sub('', text)

        '''Remove non-English chars'''
        text = filter(lambda x: x in printable, text)

        tokens = tknzr.tokenize(text)
        words = []
        for token in tokens:
            if token not in cachedStopWords:
                word = stemmer.stem(token)
                words.append(word)
        if len(words) >= 5:
            text = ' '.join(words)
            text += '.'
            # print text
            return text
    else:
        return None


def read_document(dbname, colname, timecol, uset=None):
    db = dbt.db_connect_no_auth(dbname)
    col = db[colname]
    timelines = db[timecol]
    documents = list()
    ids = list()
    for user in col.find({'timeline_count': {'$gt': 0}}, ['id'], no_cursor_timeout=True):
        uid = user['id']
        textmass = ""
        for tweet in timelines.find({'user.id': uid}, no_cursor_timeout=True).sort([('id', 1)]):
            if 'quoted_status' in tweet:
                continue
            # elif 'retweeted_status' in tweet:
            #     continue
            else:
                text = process(tweet['text'])
                if text:
                    # print user, time['id'], text, '<-------', time['text']
                    textmass += text + ' '
                else:
                    continue
        tokens = textmass.split()
        if len(tokens) > 50:
            ids.append(uid)
            
            documents.append(textmass)
    pickle.dump(ids, open('data/doc_ids.pick', 'w'))
    return documents


def pre_process(texts):
    from collections import defaultdict
    frequency = defaultdict(int)
    for text in texts:
        for token in text:
            frequency[token] += 1
    texts = [[token for token in text if frequency[token] > 1] for text in texts]
    return texts
    # dictionary = corpora.Dictionary(texts)
    # # dictionary.save('/tmp/deerwester.dict') # store the dictionary, for future reference
    # corpus = [dictionary.doc2bow(text) for text in texts]
    # # corpora.MmCorpus.serialize('/tmp/deerwester.mm', corpus) # store to disk, for later use
    # return corpus, dictionary


def doc_vect(dbname, colname, timecol, uset=None):
    documents = read_document(dbname, colname, timecol, uset)
    pickle.dump(documents, open('data/fedcorpus.pick', 'w'))
    model = models.doc2vec.Doc2Vec(documents, workers=8)
    pickle.dump(model, open('data/doc2vec.pick', 'w'))


if __name__ == '__main__':

    '''Doc2Vec testing'''
    doc_vect('fed', 'com', 'timeline')
    model = pickle.load(open('data/doc2vec.pick', 'r'))
    # for word in model.vocab:
    #     print word
    # print model.most_similar(positive=['ed', 'anorexic'], negative=['fitness', 'health'])



