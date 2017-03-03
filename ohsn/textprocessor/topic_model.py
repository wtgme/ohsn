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
from nltk.corpus import stopwords
from nltk import pos_tag
from nltk.stem.snowball import EnglishStemmer
import numpy as np
import logging
import seaborn as sns
import matplotlib.pyplot as plt
import pymongo
import RAKE

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
stopwds = stopwords.words('english')
stemmer = EnglishStemmer()
tokenizer = RegexpTokenizer(r'\w+')

def read_hashtag(dbname, colname, timecol, uset=None):
    db = dbt.db_connect_no_auth(dbname)
    col = db[colname]
    timelines = db[timecol]

    hgrex = re.compile(r'(?<=^|(?<=[^a-zA-Z0-9]))#([A-Za-z0-9_]+)')  # for hashtags
    documents = list()
    ids = list()
    for user in col.find({'timeline_count': {'$gt': 0}}, ['id']):
        uid = user['id']
    # for uid in uset:
        tags = list()
        for tweet in timelines.find({'user.id': uid}):
            text = tweet['text'].encode('utf8').lower().strip()
            tags += re.findall(hgrex, text)
        if len(tags) > 10:
            ids.append(uid)
            documents.append(tags)
    pickle.dump(ids, open('data/hash_ids.pick', 'w'))
    return documents


def read_setence(dbname, colname, timecol, uset=None):
    db = dbt.db_connect_no_auth(dbname)
    col = db[colname]
    timelines = db[timecol]
    documents = list()
    ids = list()
    for user in col.find({'timeline_count': {'$gt': 0}}, ['id']):
        uid = user['id']
    # for uid in uset:
        for tweet in timelines.find({'user.id': uid}):
            text = tweet['text'].encode('utf8')
            # replace RT, @, # and Http://
            text = text.strip().lower()
            text = re.sub(r"(?:(rt\ ?@)|@|https?://)\S+", "", text) # replace RT @, @ and http://
            words = tokenizer.tokenize(text)
                # Any text with fewer than 50 words should be looked at with a certain degree of skepticism.
            if len(words) > 5:
                ids.append(uid)
                documents.append(words)
    pickle.dump(ids, open('data/sen_ids.pick', 'w'))
    return documents


def read_document(dbname, colname, timecol, uset=None):
    db = dbt.db_connect_no_auth(dbname)
    col = db[colname]
    timelines = db[timecol]

    rtgrex = re.compile(r'RT (?<=^|(?<=[^a-zA-Z0-9-\.]))@([A-Za-z0-9_]+):')  # for Retweet
    mgrex = re.compile(r'(?<=^|(?<=[^a-zA-Z0-9-\.]))@([A-Za-z0-9_]+)')  # for mention
    # hgrex = re.compile(r'(?<=^|(?<=[^a-zA-Z0-9]))#([A-Za-z0-9_]+)')  # for hashtags
    ugrex = re.compile(r'(https?://[^\s]+)')  # for url
    documents = list()
    ids = list()

    for user in col.find({'timeline_count': {'$gt': 0}}, ['id']):
        uid = user['id']
    # for uid in uset:
        textmass = ""
        for tweet in timelines.find({'user.id': uid}):
            text = tweet['text'].encode('utf8')
            # replace RT, @, # and Http://
            text = rtgrex.sub('', text)
            text = mgrex.sub('', text)
            # text = hgrex.sub('', text)
            text = ugrex.sub('', text)
            text = text.strip()
            if not(text.endswith('.') or text.endswith('?') or text.endswith('!')):
                text += '.'
            textmass = textmass + " " + text.lower()
        words = textmass.split()
            # Any text with fewer than 50 words should be looked at with a certain degree of skepticism.
        if len(words) > 50:
            ids.append(uid)
            documents.append(textmass)
    pickle.dump(ids, open('data/doc_ids.pick', 'w'))
    return documents


def pro_process_text(text):
    text = text.lower()
    tokens = tokenizer.tokenize(text)
    words = pos_tag(tokens)
    new_token = list()
    for (token, pos) in words:
        if pos in ['NN', 'JJ']:
            if token not in stopwds:
                try:
                    st = stemmer.stem(token)
                except UnicodeDecodeError:
                    continue
                new_token.append(st)
    return new_token


def pro_process_sentence(sentence):
    sentence = sentence.lower()
    return tokenizer.tokenize(sentence)


def pro_process_documents(documents):
    texts = list()
    for document in documents:
        text = pro_process_text(document)
        if len(text) > 0:
            texts.append(text)
    return texts


def pre_process(texts):
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
    return corpus, dictionary


def word_vect(dbname, colname, timecol, uset=None):
    sentences = read_setence(dbname, colname, timecol, uset)
    print len(sentences)
    model = models.word2vec.Word2Vec(sentences, size=300, window=5, sg=1, workers=8, hs=1)
    model.save('data/word2vec')


def best_K(corpus, dictionary, mintopic=1, maxtopic=100, step=1):
    id_scores = {}
    for i in range(mintopic, maxtopic, step):
        lda = models.ldamodel.LdaModel(corpus=corpus, num_topics=i, id2word=dictionary)
        cohences = lda.top_topics(corpus, num_words=20)
        cosum = 0.0
        for t, coh in cohences:
            cosum += coh
        id_scores[i] = (cosum/len(cohences))
    print id_scores
    return max(id_scores.iterkeys(), key=lambda k: id_scores[k])


def topic_model(dbname, colname, timecol, uset=None, dtype='document'):
    if dtype == 'document':
        documents = read_document(dbname, colname, timecol, uset)
        # pickle.dump(documents, open('data/document.pick', 'w'))
        # documents = pickle.load(open('data/document.pick', 'r'))
        texts = pro_process_documents(documents)
    elif dtype == 'hashtag':
        texts = read_hashtag(dbname, colname, timecol, uset)
    corpus, dictionary = pre_process(texts)
    pickle.dump((corpus, dictionary), open('data/corups_'+dtype+'.pick', 'w'))
    best_k = best_K(corpus, dictionary)
    lda = models.ldamodel.LdaModel(corpus=corpus, num_topics=best_k, id2word=dictionary)
    # lda.print_topics(num_topics=20, num_words=100)
    pickle.dump(lda, open('data/lda_'+dtype+'.pick', 'w'))


def filter_ed_tweets():
    from ohsn.edrelated import edrelatedcom
    prorec = edrelatedcom.rec_user('fed', 'scom')
    proed = edrelatedcom.proed_users('fed', 'scom')

    # com = dbt.db_connect_col('fed', 'scom')
    times = dbt.db_connect_col('fed', 'timeline')
    ed_times = dbt.db_connect_col('fed', 'edtimeline2')
    ed_times.create_index([('user.id', pymongo.ASCENDING),
                              ('id', pymongo.DESCENDING)])
    ed_times.create_index([('id', pymongo.ASCENDING)], unique=True)
    ed_list = set(['bmi', 'cw', 'ugw', 'gw', 'lbs', 'hw', 'lw', 'kg', 'ed',
                   'eatingdisorder', 'anorexia', 'bulimia', 'anorexic',
                'ana', 'bulimic', 'anorexia', 'mia', 'thinspo',
                'bulemia', 'purge', 'bulimia', 'binge',  'selfharm',
                'ednos', 'edprobs', 'edprob', 'proana', 'anamia', 'promia',
                'askanamia', 'bonespo', 'legspo'])
    model = models.word2vec.Word2Vec.load('data/word2vec')
    # Rake = RAKE.Rake('/home/wt/Code/ohsn/ohsn/networkminer/stoplist/SmartStoplist.txt')
    import ohsn.api.profiles_check as pc
    print len(prorec+proed)
    for user in prorec+proed:
        for tweet in times.find({'user.id': int(user)}):
            text = tweet['text'].encode('utf8')
            # replace RT, @, # and Http://
            # text = text.strip().lower()
            # text = re.sub(r"(?:(rt\ ?@)|@|https?://)\S+", "", text) # replace RT @, @ and http://
            # keywords = Rake.run(text)
            keywords = pc.tokenizer_stoprm(text)
            sumsim = 0.0
            count = 0
            # for word in keywords:
            #     tokens = word[0].split()
            #     sima, ca = 0.0, 0.0
            #     for token in tokens:
            #         if token in model:
            #             for ed in ed_list:
            #                 sim = model.similarity(token, ed)
            #                 # if sim > maxsim:
            #                 sima += sim
            #                 ca += 1
            #     if ca != 0:
            #         sumsim += sima/ca
            #         count += 1
            for word in keywords:
                if word in model:
                    for ed in ed_list:
                        sim = model.similarity(word, ed)
                        sumsim += sim
                        count += 1
            if count != 0 and (sumsim/count) > 0.26: # the average similarity of ed words
                try:
                    ed_times.insert(tweet)
                except pymongo.errors.DuplicateKeyError:
                    pass

if __name__ == '__main__':
    '''Topic Modeling'''
    # print pro_process_text('A survey of user opinion of computer system response time')
    # topic_model('fed', 'scom', 'stimeline', dtype='document')
    # topic_model('fed', 'scom', 'stimeline', dtype='hashtag')

    # dtype = 'hashtag'
    # lda = pickle.load(open('data/lda_'+dtype+'.pick', 'r'))
    # lda.print_topics(num_topics=20, num_words=100)

    '''Word2Vec testing'''
    # word_vect('fed', 'scom', 'timeline')
    # model = models.word2vec.Word2Vec.load('data/word2vec')
    # for word in model.vocab:
    #     print word
    # print model.most_similar(positive=['recover'], negative=[], topn=20)
    # print model.most_similar(positive=['ed'], negative=[], topn=20)
    # print model.most_similar(positive=['fat'], negative=[], topn=20)
    # print model.similarity('ana', 'depressed')
    # ed_bio_list = set(['bmi', 'cw', 'ugw', 'gw', 'lbs', 'hw', 'lw', 'kg'])
    # ed_keywords_list = set(['ed', 'eatingdisorder', 'anorexia', 'bulimia', 'anorexic',
    #             'ana', 'bulimic', 'anorexia', 'mia', 'thinspo',
    #             'bulemia', 'purge', 'bulimia', 'binge',  'selfharm',
    #             'ednos', 'edprobs', 'edprob', 'proana', 'anamia', 'promia',
    #             'askanamia', 'bonespo', 'legspo'])
    # for word in ed_bio_list.union(ed_keywords_list):
    #     tokens = word.split()
    #     print model.most_similar(positive=tokens)

    # wlist = list(ed_bio_list.union(ed_keywords_list))
    # simall, count = 0.0, 0.0
    # simis = []
    # max = len(wlist) #model.wv.vocab
    # for i in xrange(max):
    #     for j in xrange(i+1, max):
    #         # print model.wv.index2word[i]
    #         sim = model.similarity(wlist[i], wlist[j]) # model.wv.index2word[i]
    #         simall += sim
    #         count += 1
    #         simis.append(sim)
    # print simall/count
    # print len(simis)
    # sns.distplot(simis, hist=False)
    # plt.show()

    filter_ed_tweets()

'''Cluster Word based word2vec'''
    # print len(model.wv.vocab)
    # X = [model[model.wv.index2word[i]] for i in xrange(len(model.wv.vocab))]
    # X = np.asarray(X)
    # from sklearn.cluster import AgglomerativeClustering, KMeans
    # from sklearn.metrics import silhouette_score
    # clustering = AgglomerativeClustering(affinity='cosine', linkage='complete')
    # clustering.fit(X)
    # pickle.dump(clustering, open('data/clustering.pick', 'w'))
    # range_n_clusters = range(2, 21)
    # values = []
    # for n_clusters in range_n_clusters:
    #     clusterer = KMeans(n_clusters=n_clusters, random_state=10)
    #     cluster_labels = clusterer.fit_predict(X)
    #     silhouette_avg = silhouette_score(X, cluster_labels)
    #     print("For n_clusters =", n_clusters, "The average silhouette_score is :", silhouette_avg)
    #     values.append(silhouette_avg)
    # print values
    # print range_n_clusters


