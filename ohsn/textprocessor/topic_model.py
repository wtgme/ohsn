# -*- coding: utf-8 -*-
"""
Created on 4:52 PM, 5/2/16

@author: tw
"""

from gensim import corpora, models
from ohsn.util import db_util as dbt
import re
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.stem.snowball import EnglishStemmer


def read_document(dbname, colname, timecol, uset=None):
    db = dbt.db_connect_no_auth(dbname)
    col = db[colname]
    timelines = db[timecol]

    rtgrex = re.compile(r'RT (?<=^|(?<=[^a-zA-Z0-9-\.]))@([A-Za-z0-9_]+):')  # for Retweet
    mgrex = re.compile(r'(?<=^|(?<=[^a-zA-Z0-9-\.]))@([A-Za-z0-9_]+)')  # for mention
    hgrex = re.compile(r'(?<=^|(?<=[^a-zA-Z0-9]))#([A-Za-z0-9_]+)')  # for hashtags
    # hgrex = re.compile(r'(?<=^|(?<=[^a-zA-Z0-9-\.]))#([A-Za-z0-9_]+)')  # for hashtags
    ugrex = re.compile(r'(https?://[^\s]+)')  # for url
    documents = list()

    for user in col.find({'timeline_count': {'$gt': 0}}, ['id']).limit(250):
        uid = user['id']
    # for uid in uset:
        textmass = ""
        for tweet in timelines.find({'user.id': uid}):
            text = tweet['text'].encode('utf8')
            # replace RT, @, # and Http://
            text = rtgrex.sub('', text)
            text = mgrex.sub('', text)
            text = hgrex.sub('', text)
            text = ugrex.sub('', text)
            text = text.strip()
            if not(text.endswith('.') or text.endswith('?') or text.endswith('!')):
                text += '.'
            textmass = textmass + " " + text.lower()
        documents.append(textmass)
    return documents

stopwds = stopwords.words('english')
stemmer = EnglishStemmer()


def pro_process_text(text):
    text = text.lower()
    tokenizer = RegexpTokenizer(r'\w+')
    tokens = tokenizer.tokenize(text)
    new_token = list()
    for token in tokens:
        if token not in stopwds:
            try:
                st = stemmer.stem(token)
            except UnicodeDecodeError:
                continue
            new_token.append(st)
    return new_token


def pre_process(documents):
    texts = [[word for word in pro_process_text(document)] for document in documents]
    from collections import defaultdict
    frequency = defaultdict(int)
    for text in texts:
        for token in text:
            frequency[token] += 1
    texts = [[token for token in text if frequency[token] > 1] for text in texts]
    dictionary = corpora.Dictionary(texts)
    # dictionary.save('/tmp/deerwester.dict') # store the dictionary, for future reference
    corpus = [dictionary.doc2bow(text) for text in texts]
    # corpora.MmCorpus.serialize('/tmp/deerwester.mm', corpus) # store to disk, for later use
    return (corpus, dictionary)


def topic_model(dbname, colname, timecol, uset=None):
    documents = read_document(dbname, colname, timecol, uset)
    print len(documents)
    corpus, dictionary = pre_process(documents)
    # from pprint import pprint
    # print (dictionary.token2id)
    # pprint(corpus)
    lda = models.ldamodel.LdaModel(corpus=corpus, id2word=dictionary, num_topics=20, update_every=1, chunksize=10000, passes=1)
    lda.print_topics(num_topics=20, num_words=20)

if __name__ == '__main__':
    # print pro_process_text('A survey of user opinion of computer system response time')
    topic_model('fed', 'scom', 'stimeline')