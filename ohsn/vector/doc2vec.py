# -*- coding: utf-8 -*-
"""
Created on 4:52 PM, 5/2/16

@author: tw
"""
import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
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
        text = filter(lambda x: x in printable, text.lower())
        text = re.sub(r'\d+', '', text)
        tokens = tknzr.tokenize(text)
        words = []
        for token in tokens:
            if token in cachedStopWords:
                # print '========================='
                continue
            else:
                word = stemmer.stem(token)
                words.append(word)
        if len(words) >= 3:
            text = ' '.join(words)
            text += ' .'
            # print text
            return text
    else:
        return None


def topKFrequent(tokens, k):
    import collections
    c = collections.Counter(tokens)
    # print len(c)
    return [x[0] for x in c.most_common(k)]


# def read_document(dbname, colname, timecol, uset=None):
#     db = dbt.db_connect_no_auth(dbname)
#     col = db[colname]
#     timelines = db[timecol]
#     for user in col.find({'timeline_count': {'$gt': 0}}, ['id'], no_cursor_timeout=True):
#         uid = user['id']
#         textmass = ""
#         for tweet in timelines.find({'user.id': uid}, no_cursor_timeout=True).sort([('id', -1)]).limit(5):
#             if 'quoted_status' in tweet:
#                 continue
#             elif 'retweeted_status' in tweet:
#                 continue
#             else:
#                 text = process(tweet['text'])
#                 if text:
#                     # print user, time['id'], text, '<-------', time['text']
#                     textmass += text + ' '
#                 else:
#                     continue
#         tokens = textmass.split()
#         if len(tokens) > 50:
#             topk = topKFrequent(tokens, 300)
#             words = [token for token in tokens if token in topk]
#             print str(uid) + '\t' + ' '.join(words)


def read_document(dbname, colname, timecol, uset=None):
    db = dbt.db_connect_no_auth(dbname)
    col = db[colname]
    timelines = db[timecol]
    for user in col.find({'timeline_count': {'$gt': 0}}, ['id', 'description'], no_cursor_timeout=True):
        uid = user['id']
        text = process(user['description'])
        if text:
            print str(uid) + '\t' + ' '.join(text.split())
        else:
            textmass = ""
            for tweet in timelines.find({'user.id': uid}, no_cursor_timeout=True).sort([('id', -1)]).limit(5):
                text = process(tweet['text'])
                if text:
                    textmass += text + ' '
                else:
                    continue
            tokens = textmass.split()
            if len(tokens) >= 3:
                # topk = topKFrequent(tokens, 300)
                # words = [token for token in tokens if token in topk]
                print str(uid) + '\t' + ' '.join(tokens)
            else:
                continue


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


def doc_vect(filename):
    documents = []
    from gensim.models.doc2vec import TaggedDocument
    with open(filename, 'r') as fo:
        for line in fo.readlines():
            tokens = line.split('\t')
            sentence = TaggedDocument(tokens[1].split(), [tokens[0]])
            documents.append(sentence)
    print len(documents)
    from gensim.models.doc2vec import Doc2Vec
    model = Doc2Vec(documents, min_count=1, window=10, size=100, sample=1e-4, negative=5, workers=8)
    model.save('data/doc2vec.d2v')
    # pickle.dump(model, open('data/doc2vec.pick', 'w'))


def varify():
    from gensim.models.doc2vec import Doc2Vec
    model = Doc2Vec.load('data/doc2vec.d2v')
    documents = pickle.load(open('data/fedcorpus.pick', 'r'))
    for i in xrange(3):
        inferred_docvec = model.infer_vector(documents[i].words)
        print documents[i].tags
        print('%s:\n %s' % (model, model.docvecs.most_similar([inferred_docvec], topn=3)))


def profile(dbname, colname):
    db = dbt.db_connect_no_auth(dbname)
    com = db[colname]
    for user in com.find():
        pro = user['description'].split()
        print user['id'], ' '.join(pro).encode('utf-8')

if __name__ == '__main__':
    # '''Read Files'''
    documents = read_document('fed', 'com', 'timeline')

    '''Doc2Vec traing'''
    # doc_vect('data/fed.data')

    # for word in model.vocab:
    #     print word
    # print model.most_similar(positive=['ed', 'anorexic'], negative=['fitness', 'health'])
    '''Verify model'''
    # varify()

    # profile('fed', 'com')

    # s = '''Female//27yrs//BPD//EDNOS//Self Harm//SW: 145 LBS//CW: 100 LBS//UGW:85 LBS ~~I Will Not Die Fat~~Trigger Warning~~ Avi Is Me~~'''
    # print process(s)




