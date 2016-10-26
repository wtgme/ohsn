# -*- coding: utf-8 -*-
"""
Created on 2:30 PM, 10/26/16

@author: tw

This script split ED users' timeline in every 500 tweets.
For each bunch, perform LIWC analysis to see the changes of LIWC feature over time
"""

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))


from ohsn.util import db_util as dbt
import ohsn.lexiconsmaster.liwc_timeline_processor as liwcp
from datetime import datetime
import pandas as pd
import numpy as np


def bunch_user_tweets_panel(dbname, comname, timename, n=100):
    '''
    :param dbname: db name
    :param comname: user collection name
    :param timename: timeline collection name
    :param n: split tweets every n
    :return: pandas panel
    '''
    db = dbt.db_connect_no_auth(dbname)
    com = db[comname]
    times = db[timename]

    data = {}

    for user in com.find({'timeline_count': {'$gt': 500}}, ['id', 'id_str', 'created_at']):
        uid = user['id']
        cursor = times.find({'user.id': uid}).sort([("id", 1)])


        liwc_results = []
        indices = []
        user_create_time = []
        first_tweet_time = []
        last_tweet_time = []
        fields = []

        count = 0
        index = 0
        tweets = []

        while cursor.alive:
            if count < n:
                tweet = cursor.next()
                tweets.append(tweet)
                count += 1
            else:
                result = liwcp.process_tweet(tweets, Trim_rt=False)
                if result:
                    liwc_results.append([result[k] for k in result.keys()])
                    if len(fields) == 0:
                        fields = [k for k in result.keys()]
                    indices.append(index)
                    user_create_time.append(datetime.strptime(user['created_at'], '%a %b %d %H:%M:%S +0000 %Y'))
                    first_tweet_time.append(datetime.strptime(tweets[0]['created_at'], '%a %b %d %H:%M:%S +0000 %Y'))
                    last_tweet_time.append(datetime.strptime(tweets[-1]['created_at'], '%a %b %d %H:%M:%S +0000 %Y'))
                    # print index, count
                index += 1
                count = 0
                tweets = []
        liwc_results = np.array(liwc_results)
        size = len(user_create_time)
        user_create_time = np.reshape(user_create_time, (size, 1))
        first_tweet_time = np.reshape(first_tweet_time, (size, 1))
        last_tweet_time = np.reshape(last_tweet_time, (size, 1))
        liwc_results = np.append(liwc_results, user_create_time, axis=1)
        liwc_results = np.append(liwc_results, first_tweet_time, axis=1)
        liwc_results = np.append(liwc_results, last_tweet_time, axis=1)
        print liwc_results.shape


        df = pd.DataFrame(data=liwc_results,
                          columns=fields + ['user_created_time', 'first_tweet_time', 'last_tweet_time'],
                          index=indices)
        data[user['id_str']] = df
    pn = pd.Panel(data)
    pn.to_pickle('ed-liwc.panel')


def bunch_user_tweets_dataframe(dbname, comname, timename, n=100):
    '''
    :param dbname: db name
    :param comname: user collection name
    :param timename: timeline collection name
    :param n: split tweets every n
    :return: pandas dataframe
    '''
    db = dbt.db_connect_no_auth(dbname)
    com = db[comname]
    times = db[timename]

    liwc_results = []
    indices = []
    user_dis = []
    user_create_time = []
    first_tweet_time = []
    last_tweet_time = []
    fields = []

    for user in com.find({'timeline_count': {'$gt': 500}}, ['id', 'id_str', 'created_at']):
        uid = user['id']
        cursor = times.find({'user.id': uid}).sort([("id", 1)])

        count = 0
        index = 0
        tweets = []

        while cursor.alive:
            if count < n:
                tweet = cursor.next()
                tweets.append(tweet)
                count += 1
            else:
                result = liwcp.process_tweet(tweets, Trim_rt=False)
                if result:
                    liwc_results.append([result[k] for k in result.keys()])
                    if len(fields) == 0:
                        fields = [k for k in result.keys()]
                    user_dis.append(user['id_str'])
                    indices.append(index)
                    user_create_time.append(datetime.strptime(user['created_at'], '%a %b %d %H:%M:%S +0000 %Y'))
                    first_tweet_time.append(datetime.strptime(tweets[0]['created_at'], '%a %b %d %H:%M:%S +0000 %Y'))
                    last_tweet_time.append(datetime.strptime(tweets[-1]['created_at'], '%a %b %d %H:%M:%S +0000 %Y'))
                    print index, count
                index += 1
                count = 0
                tweets = []
    liwc_results = np.array(liwc_results)
    size = len(user_create_time)
    user_create_time = np.reshape(user_create_time, (size, 1))
    first_tweet_time = np.reshape(first_tweet_time, (size, 1))
    last_tweet_time = np.reshape(last_tweet_time, (size, 1))
    user_dis = np.reshape(user_dis, (size, 1))
    indices = np.reshape(indices, (size, 1))
    user_dis = np.append(user_dis, indices, axis=1)
    user_dis = np.append(user_dis, user_create_time, axis=1)
    user_dis = np.append(user_dis, first_tweet_time, axis=1)
    user_dis = np.append(user_dis, last_tweet_time, axis=1)
    liwc_results = np.append(user_dis, liwc_results, axis=1)
    print 'user matrix', liwc_results.shape


    df = pd.DataFrame(data=liwc_results,
                      columns= ['user_id', 'time_index', 'user_created_time', 'first_tweet_time', 'last_tweet_time'] + fields)
    df.to_csv('ed-liwc200.csv')

if __name__ == '__main__':
    bunch_user_tweets_dataframe('fed', 'scom', 'timeline', n=200)


