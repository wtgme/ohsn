# -*- coding: utf-8 -*-
"""
Created on 11:49, 31/08/16

@author: wt
This pre-process includes:
1. Remove URL, Hashtags, Username, RT@
2. Remove stopword and punctuation
3. Stemming

HERE:
we only process tweets without URLs, as ULRs may outside refereces
Today stats: One follower, 4 unfollowers via http://t.co/XIGJzw4Ds8
Today stats: 4 followers, 7 unfollowers via http://t.co/XIGJzvN2AA
Today stats: No new followers, 2 unfollowers via http://t.co/XIGJzw4Ds8
Today stats: One follower, 2 unfollowers via http://t.co/XIGJzw4Ds8
"""

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import re
from nltk.tokenize import RegexpTokenizer
from nltk import SnowballStemmer
import ohsn.util.db_util as dbt
import ohsn.util.io_util as iot
import string
import pickle
from nltk.corpus import stopwords

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
            text += ' .'
            return text
    else:
        return None


def process_tweet(dbname, comname, timename, label, filename):
    db = dbt.db_connect_no_auth(dbname)
    times = db[timename]
    user_list = iot.get_values_one_field(dbname, comname, 'id', {"timeline_count": {'$gt': 0}, 'lang': 'en'})
    target_users = []
    for user in user_list:
        context = ''
        for time in times.find({'user.id': user}).sort([('id', 1)]):
            # print time['created_at']
            if 'retweeted_status' in time:
                continue
            elif 'quoted_status' in time:
                continue
            else:
                text = process(time['text'])
                if text:
                    # print user, time['id'], text, '<-------', time['text']
                    context += text + ' '
                else:
                    continue
                    # print user, time['id'], 'None', '<-------', time['text']
        if len(context.split()) > 50:
            target_users.append(user)
            print '__label__'+label+' , ' + context
    pickle.dump(target_users, open('data/'+filename+'.pick', 'w'))

if __name__ == '__main__':
    process_tweet('fed', 'scom', 'stimeline', '1', 'ED')
    process_tweet('random', 'scom', 'timeline', '2', 'Random')

