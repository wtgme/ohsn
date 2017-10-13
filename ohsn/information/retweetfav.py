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
from ohsn.api import follower
from ohsn.api import following
import numpy as np
import pymongo
import re, string

rtgrex = re.compile(r'RT (?<=^|(?<=[^a-zA-Z0-9-\.]))@([A-Za-z0-9_]+):')  # for Retweet
mgrex = re.compile(r'(?<=^|(?<=[^a-zA-Z0-9-\.]))@([A-Za-z0-9_]+)')  # for mention
hgrex = re.compile(r'(?<=^|(?<=[^a-zA-Z0-9]))#([A-Za-z0-9_]+)')  # for hashtags
# hgrex = re.compile(r'(?<=^|(?<=[^a-zA-Z0-9-\.]))#([A-Za-z0-9_]+)')  # for hashtags
ugrex = re.compile(r'(https?://[^\s]+)')  # for url


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
    newstream.create_index("id", unique=True)
    i = 0
    ids = []
    for tweet in stream.find({'recollected': {'$exists': False},}, no_cursor_timeout=True):
        if i < 100:
            stream.update_one({'id': tweet['id']}, {'$set': {'recollected': True}}, upsert=False)
            ids.append(tweet['id'])
            i += 1
        else:
            print datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + str(len(ids))
            tweets = tlup.get_tweets_info(ids)
            for t in tweets:
                try:
                    newstream.insert(t)
                except pymongo.errors.DuplicateKeyError:
                    pass
            i = 0
            ids = []


def extract_user(dbname='ed', stream='restream', user='com'):
    # extract users from tweet stream, including author and retweeters.
    stream = dbt.db_connect_col(dbname, stream)
    com = dbt.db_connect_col(dbname, user)
    com.create_index("id", unique=True)
    for tweet in stream.find({'userextract': {'$exists': False},}, no_cursor_timeout=True):
        author = tweet['user']
        author['level'] = 1
        try:
            com.insert(author)
        except pymongo.errors.DuplicateKeyError:
            pass
        if 'retweeted_status' in tweet:
            retweetee = tweet['retweeted_status']['user']
            retweetee['level'] = 1
            try:
                com.insert(retweetee)
            except pymongo.errors.DuplicateKeyError:
                pass
        stream.update_one({'id': tweet['id']}, {'$set': {'userextract': True}}, upsert=False)


def follow_net(dbname='ed', username='com', netname='net'):
    # Collect follow network among users
    com = dbt.db_connect_col(dbname, username)
    net = dbt.db_connect_col(dbname, netname)
    net.create_index([("user", pymongo.ASCENDING),
                         ("follower", pymongo.ASCENDING)],
                        unique=True)
    level = 1
    while level < 2:
        # Each call of snowball_following and snowball_follower only process up to 200 users
        print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'Snowball followings of seeds for sample db', level
        following_flag = following.snowball_following(com, net, level, 'N')
        print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'Snowball followees of seeds for sample db', level
        follower_flag = follower.snowball_follower(com, net, level, 'N')
        if following_flag == False and follower_flag == False:
            level += 1
        continue


def unique_tweet(dbname, streamname, timename):
    # get unique tweets in the stream
    stream = dbt.db_connect_col(dbname, streamname)
    time = dbt.db_connect_col(dbname, timename)
    time.create_index("id", unique=True)
    for tweet in stream.find({}, no_cursor_timeout=True):
        if 'retweeted_status' in tweet:
            text = tweet['retweeted_status']['text']
        else:
            text = tweet['text']
        try:
            time.insert({'id': tweet['id'], 'text': text})
        except pymongo.errors.DuplicateKeyError:
            pass

def out_tweet_for_cluster(dbname, colname):
    # Output tweets for embedding and clustering
    time = dbt.db_connect_col(dbname, colname)
    replace_punctuation = string.maketrans(string.punctuation, ' '*len(string.punctuation))
    for tweet in time.find({}, no_cursor_timeout=True):
        text = tweet['text'].encode('utf-8')
        text = rtgrex.sub('', text) # retweet
        text = mgrex.sub('', text) # mention
        # text = hgrex.sub('', text) #hashtag
        text = ugrex.sub('', text) #url
        text = text.strip().lower()
        text = text.translate(replace_punctuation)
        print ' '.join(text.split())




if __name__ == '__main__':
    # tweet_stat('fed', 'scom', 'timeline')
    # noned_tweet_stat('random', 'timeline')
    # noned_tweet_stat('younger', 'timeline')
    # sample('data/rd-tweet.csv')
    # tweet_difference('younger')
    # plot_distribution(dbname='younger', comname='scom')
    recollect_ed()
    # extract_user()
    # follow_net()
    # unique_tweet('ed', 'stream', 'tweet')
    # out_tweet_for_cluster('ed', 'tweet')