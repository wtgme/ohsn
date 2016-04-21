# -*- coding: utf-8 -*-
"""
Created on 12:17 PM, 4/5/16

@author: tw

"""

from ohsn import util as dbutil
import ohsn.util.io_util as ioutil
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.stem.snowball import EnglishStemmer
import re
import os
import shutil


def compare_difference():
    ed_ids = ioutil.get_values_one_field('fed', 'com', 'id', {'level':1})
    rd_ids = ioutil.get_values_one_field('random', 'com', 'id', {'level':1})
    print list(set(ed_ids).intersection(rd_ids))


def tokenizer(dbname, poicol, timecol, foldername):
    rtgrex = re.compile(r'RT (?<=^|(?<=[^a-zA-Z0-9]))@([A-Za-z0-9_]+):')  # for Retweet
    mgrex = re.compile(r'(?<=^|(?<=[^a-zA-Z0-9]))@([A-Za-z0-9_]+)')  # for mention
    hgrex = re.compile(r'(?<=^|(?<=[^a-zA-Z0-9]))#([A-Za-z0-9_]+)')  # for hashtags
    # hgrex = re.compile(r'(?<=^|(?<=[^a-zA-Z0-9-\.]))#([A-Za-z0-9_]+)')  # for hashtags
    ugrex = re.compile(r'(https?://[^\s]+)')  # for url
    nums = re.compile(r'[\.0-9]')
    db = dbutil.db_connect_no_auth(dbname)
    poi = db[poicol]
    time = db[timecol]
    if os.path.exists(foldername):
        shutil.rmtree(foldername)
    else:
        os.makedirs(foldername)
    for user in poi.find({'level':1}, ['id']):
        textmass = ""
        for tweet in time.find({'user.id': user['id']}, ['text']):
            text = tweet['text'].encode('utf8')
            # replace RT, @, #, Http:// and numbers
            # print '-------------------'
            # print text
            text = rtgrex.sub('', text)
            text = mgrex.sub('', text)
            text = hgrex.sub('', text)
            text = ugrex.sub('', text)
            text = nums.sub('', text)
            # print text
            text = text.strip()
            if not(text.endswith('.') or text.endswith('?') or text.endswith('!')):
                text += '.'
            textmass = textmass + " " + text.lower()
        words = textmass.split()
        # Any text with fewer than 50 words should be looked at with a certain degree of skepticism.
        if len(words) > 50:
            tokens = text_process(textmass)
            if len(tokens) > 50:
                with open(foldername+'/'+str(user['id'])+'.data', 'w') as the_file:
                    the_file.write(' '.join(tokens))
                # print str(user['id']) + '\t'+ (' '.join(tokens))

stopwds = stopwords.words('english')
stemmer = EnglishStemmer()


def text_process(text):
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

# text_process('(step..) ) play.  flappy bird between rounds.')

def hashtags(dbname, poicol, timecol, foldername):
    hgrex = re.compile(r'(?<=^|(?<=[^a-zA-Z0-9]))#([A-Za-z0-9_]+)')  # for hashtags
    db = dbutil.db_connect_no_auth(dbname)
    poi = db[poicol]
    time = db[timecol]
    if os.path.exists(foldername):
        shutil.rmtree(foldername)
    else:
        os.makedirs(foldername)
    for user in poi.find({'level':1}, ['id']):
        tags = list()
        for tweet in time.find({'user.id': user['id']}, ['text']):
            text = tweet['text'].encode('utf8').lower()
            tags += re.findall(hgrex, text)
        if len(tags) > 10:
            with open(foldername+'/'+str(user['id'])+'.data', 'w') as the_file:
                    the_file.write(' '.join(tags))
            # print str(user['id']) + '\t'+ (' '.join(tags))




tokenizer('random', 'com', 'timeline', 'rdword')
tokenizer('fed', 'com', 'timeline', 'edword')

hashtags('random', 'com', 'timeline', 'rdtag')
hashtags('fed', 'com', 'timeline', 'edtag')

