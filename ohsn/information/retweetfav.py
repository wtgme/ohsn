# -*- coding: utf-8 -*-
"""
Created on 09:53, 03/10/17

@author: wt

Compare retweet and favorite counts of tweets between ED and non-ED users.
"""

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import ohsn.util.db_util as dbt
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
from ohsn.lexiconsmaster.lexicons.liwc import Liwc
import re
import ohsn.util.io_util as iot
import ohsn.util.plot_util as pt
import seaborn as sns
import ohsn.api.tweet_lookup as tlup
import numpy as np
import pymongo


def tweet_stat(dbname, comname, timename):
    # read tweets for one database and get the counts of retweet and favorite
    com = dbt.db_connect_col(dbname, comname)
    times = dbt.db_connect_col(dbname, timename)
    print ('uid \t tid \t rtc \t fvc \t date')
    for user in com.find({}, ['id']):
        uid = user['id']
        # Not counting retweets, because of duplicate
        for tweet in times.find({'user.id': uid, 'retweeted_status': {'$exists': False}}):
            retc = tweet['retweet_count']
            favc = tweet["favorite_count"]
            # # if the tweet is retweet, counting the stats for the original tweet
            # if "retweeted_status" in tweet:
            #     retc = tweet['retweeted_status']['retweet_count']
            #     favc = tweet['retweeted_status']["favorite_count"]
            creat = datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
            print ('%s \t %s \t %s \t %s \t %s') %(uid, tweet['id'], retc, favc, creat)


def noned_tweet_stat(dbname, timename):
    # read tweets for one database and get the counts of retweet and favorite (non-ED users)
    # get all tweets
    times = dbt.db_connect_col(dbname, timename)
    print ('uid \t tid \t rtc \t fvc \t date')
    # Not counting retweets, because of duplicate
    for tweet in times.find({'retweeted_status': {'$exists': False}}):
        uid = tweet['user']['id']
        retc = tweet['retweet_count']
        favc = tweet["favorite_count"]
        creat = datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
        print ('%s \t %s \t %s \t %s \t %s') %(uid, tweet['id'], retc, favc, creat)


def sample(filepath):
    # Data is too large, get a sample of data
    uset = set()
    with open(filepath, 'r') as fo:
        print fo.readline().strip()
        for line in fo.readlines()[1:]:
            line = line.strip()
            tokens = line.split('\t')
            uset.add(tokens[0])
            if len(uset) <= 3500:
                print line
            else:
                return


def tweet_difference(dbname='fed', comname='scom', timename='timeline'):
    # Calcuate the LIWC features of tweets that are retweeted or favorited
    com = dbt.db_connect_col(dbname, comname)
    times = dbt.db_connect_col(dbname, timename)
    '''Process the timelines of users in POI'''
    rtgrex = re.compile(r'RT (?<=^|(?<=[^a-zA-Z0-9-\.]))@([A-Za-z0-9_]+):')  # for Retweet
    mgrex = re.compile(r'(?<=^|(?<=[^a-zA-Z0-9-\.]))@([A-Za-z0-9_]+)')  # for mention
    hgrex = re.compile(r'(?<=^|(?<=[^a-zA-Z0-9]))#([A-Za-z0-9_]+)')  # for hashtags
    # hgrex = re.compile(r'(?<=^|(?<=[^a-zA-Z0-9-\.]))#([A-Za-z0-9_]+)')  # for hashtags
    ugrex = re.compile(r'(https?://[^\s]+)')  # for url
    liwc = Liwc()

    for user in com.find():
        print user['id']
        textmass_retweet = ''
        textmass_like = ''
        # textmass_equal = ''
        for tweet in times.find({'user.id': user['id'], 'retweeted_status': {'$exists': False}}):
            retc = tweet['retweet_count']
            favc = tweet["favorite_count"]
            text = tweet['text'].encode('utf8')
            text = rtgrex.sub('', text)
            text = mgrex.sub('', text)
            text = hgrex.sub('', text)
            text = ugrex.sub('', text)
            text = text.strip()
            if not(text.endswith('.') or text.endswith('?') or text.endswith('!')):
                text += '.'
            if retc > favc:
                textmass_retweet += " " + text.lower()
            if favc > retc:
                textmass_like += " " + text.lower()
            # else:
                # textmass_equal += " " + text.lower()
        textmass_retweet_words = textmass_retweet.split()
        textmass_like_words = textmass_like.split()
        # textmass_equal_words = textmass_equal.split()
        if len(textmass_retweet_words) > 50:
            liwc_result = liwc.summarize_document(' '.join(textmass_retweet_words))
            com.update_one({'id': user['id']}, {'$set': {'retweet_liwc.mined': True, 'retweet_liwc.result': liwc_result}}, upsert=False)
        if len(textmass_like_words) > 50:
            liwc_result = liwc.summarize_document(' '.join(textmass_like_words))
            com.update_one({'id': user['id']}, {'$set': {'like_liwc.mined': True, 'like_liwc.result': liwc_result}}, upsert=False)


def plot_distribution(dbname='fed', comname='scom'):
    # Plot difference between retweeted and liked tweets
    fields = iot.read_fields()
    for field in fields:
        tokens = field.split('.')
        retweet_key = field.replace('liwc_anal', 'retweet_liwc')
        like_key = field.replace('liwc_anal', 'like_liwc')
        retwets = iot.get_values_one_field(dbname, comname, retweet_key)
        likes = iot.get_values_one_field(dbname, comname, like_key)
        pt.plot_config()
        sns.distplot(retwets, hist=False, kde_kws={"color": "r", "lw": 2, "marker": 'o'},
                     label='RT ($\mu=%0.2f \pm %0.2f$)' % (np.mean(retwets), np.std(retwets)))
        sns.distplot(likes, hist=False, kde_kws={"color": "g", "lw": 2, "marker": 's'},
                     label='Like ($\mu=%0.2f \pm %0.2f$)' % (np.mean(likes), np.std(likes)))
        plt.legend(loc="best")
        plt.xlabel(tokens[-1])
        plt.ylabel('P')
        plt.savefig('data/' + tokens[-1] +'.pdf', bbox_inches='tight')
        plt.clf()



def recollect_ed(dbname='ed', colname='stream', newcol='restream'):
    # Recollect the stream data, to get the favorite and retweet counts
    stream = dbt.db_connect_col(dbname, colname)
    newstream = dbt.db_connect_col(dbname, newcol)
    i = 0
    ids = []
    for tweet in stream.find({}, ['id'], no_cursor_timeout=True):
        if i < 100:
            ids.append(tweet['id'])
            i += 1
        else:
            print len(ids)
            tweets = tlup.get_tweets_info(ids)
            for t in tweets:
                try:
                    newstream.insert(t)
                except pymongo.errors.DuplicateKeyError:
                    pass
            i = 0
            ids = []



if __name__ == '__main__':
    # tweet_stat('fed', 'scom', 'timeline')
    # noned_tweet_stat('random', 'timeline')
    # noned_tweet_stat('younger', 'timeline')
    # sample('data/rd-tweet.csv')
    # tweet_difference('younger')
    # plot_distribution(dbname='younger', comname='scom')
    recollect_ed()

