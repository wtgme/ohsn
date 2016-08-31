# -*- coding: utf-8 -*-
"""
Created on 11:49, 31/08/16

@author: wt
This pre-process includes:
1. Remove URL, Hashtags, Username, RT@
2. Spell check and correction
3. Lemmatization
"""
import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import re
from nltk.tokenize import TweetTokenizer
from nltk import SnowballStemmer
import ohsn.util.db_util as dbt
import ohsn.util.io_util as iot
import string

tknzr = TweetTokenizer()
stemmer = SnowballStemmer("english")
rtgrex = re.compile(r'RT (?<=^|(?<=[^a-zA-Z0-9-\.]))@([A-Za-z0-9_]+):')  # for Retweet
mgrex = re.compile(r'(?<=^|(?<=[^a-zA-Z0-9-\.]))@([A-Za-z0-9_]+)')  # for mention
hgrex = re.compile(r'(?<=^|(?<=[^a-zA-Z0-9]))#([A-Za-z0-9_]+)')  # for hashtags
# hgrex = re.compile(r'(?<=^|(?<=[^a-zA-Z0-9-\.]))#([A-Za-z0-9_]+)')  # for hashtags
ugrex = re.compile(r'(https?://[^\s]+)')  # for url

printable = set(string.printable)



def process(text):
    text = text.encode('utf8')

    '''replace RT, @, # and Http://'''
    text = rtgrex.sub('', text)
    text = mgrex.sub('', text)
    # text = hgrex.sub('', text)
    text = ugrex.sub('', text)

    '''Remove non-English chars'''
    text = filter(lambda x: x in printable, text)

    tokens = tknzr.tokenize(text)
    words = []
    for token in tokens:
        word = stemmer.stem(token)
        words.append(word)
    if len(words) > 5:
        text = ' '.join(words)
        if not(text.endswith('.') or text.endswith('?') or text.endswith('!')):
            text += '.'
        return text
    else:
        return None

def process_tweet(dbname, comname, timename, label):
    db = dbt.db_connect_no_auth(dbname)
    times = db[timename]
    user_list = iot.get_values_one_field(dbname, comname, 'id', {"timeline_count": {'$gt': 0}, 'lang': 'en'})
    for user in user_list:
        context = ''
        # print '----------------------------------------'
        for time in times.find({'user.id': user}).sort([('id', 1)]):
            # print time['created_at']
            if 'retweeted_status' in time:
                continue
            elif 'quoted_status' in time:
                continue
            else:
                text = process(time['text'])
                if text:
                    print text
                    # context += text + ' '
                else:
                    print '----------------------------'

        # print '__label__'+label+' , ' + context

if __name__ == '__main__':
    process_tweet('fed', 'scom', 'stimeline', '1')
