# -*- coding: utf-8 -*-
"""
Created on 14:45, 04/04/17

@author: wt
"""

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import pymongo
from ohsn.util import db_util as dbt
from datetime import datetime
import numpy as np
import pandas as pd
import ohsn.util.io_util as iot
from lifelines.utils import datetimes_to_durations

def diff_month(d1, d2):
    return (d1.year - d2.year)*12 + d1.month - d2.month


def diff_day(d2, d1):
    delta = d2 - d1
    return delta.days

def read_user_time():
    fields = iot.read_fields()
    trimed_fields = [field.split('.')[-1] for field in fields]
    data = []

    com = dbt.db_connect_col('fed', 'com')
    for user in com.find({'liwc_anal.result.WC': {'$exists': True}, 'level': 1}, no_cursor_timeout=True):
        if 'status' in user:
            created_at = datetime.strptime(user['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
            scraped_at = user['scrape_timeline_at']
            last_post = datetime.strptime(user['status']['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
            life_time = diff_day(last_post, created_at)
            average_time = float(life_time)/min(1, user['statuses_count'])
            longest_tweet_intervalb = user['longest_tweet_interval']

            observation_interval = diff_day(scraped_at, last_post)
            if (observation_interval-longest_tweet_intervalb) > 30:
                death = 1
            else:
                death = 0
            values = iot.get_fields_one_doc(user, fields)
            data.append([user['id_str'], created_at, last_post, scraped_at, average_time, longest_tweet_intervalb, observation_interval, 'ED',death]+values)

    com = dbt.db_connect_col('random', 'scom')
    for user in com.find({'liwc_anal.result.WC': {'$exists': True}}, no_cursor_timeout=True):
        if 'status' in user:
            created_at = datetime.strptime(user['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
            scraped_at = user['scrape_timeline_at']
            last_post = datetime.strptime(user['status']['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
            # life_time = diff_day(last_post, created_at)
            # average_time = float(life_time)/min(1, user['statuses_count'])
            longest_tweet_intervalb = user['longest_tweet_interval']
            observation_interval = diff_day(scraped_at, last_post)
            if (observation_interval-longest_tweet_intervalb) > 30:
                death = 1
            else:
                death = 0
            values = iot.get_fields_one_doc(user, fields)
            data.append([user['id_str'], created_at, last_post, scraped_at, average_time, longest_tweet_intervalb, observation_interval, 'RD',death]+values)


    com = dbt.db_connect_col('younger', 'scom')
    for user in com.find({'liwc_anal.result.WC': {'$exists': True}}, no_cursor_timeout=True):
        if 'status' in user:
            created_at = datetime.strptime(user['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
            scraped_at = user['scrape_timeline_at']
            last_post = datetime.strptime(user['status']['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
            # life_time = diff_day(last_post, created_at)
            # average_time = float(life_time)/min(1, user['statuses_count'])
            longest_tweet_intervalb = user['longest_tweet_interval']
            observation_interval = diff_day(scraped_at, last_post)
            if (observation_interval-longest_tweet_intervalb) > 30:
                death = 1
            else:
                death = 0
            values = iot.get_fields_one_doc(user, fields)
            data.append([user['id_str'], created_at, last_post, scraped_at, average_time, longest_tweet_intervalb, observation_interval, 'YG',death]+values)


    df = pd.DataFrame(data, columns=['uid', 'created_at', 'last_post', 'scraped_at', 'average_time', 'longest_time_interval', 'observation_interval', 'group', 'event']+trimed_fields)
    df.to_csv('user-durations.csv')


def count_longest_tweeting_period(dbname, timename, comname):
    # get users' latest 10 tweets, and calculate the largest posting interval, counted by days.
    com = dbt.db_connect_col(dbname, comname)
    time = dbt.db_connect_col(dbname, timename)
    for user in com.find({'liwc_anal.result.WC': {'$exists': True}}, no_cursor_timeout=True):
        user_id = user['id']
        datas = []
        for tweet in time.find({'user.id': user_id}, {'id': 1, 'created_at': 1}).sort([('id', -1)]).limit(10):  # sort: 1 = ascending, -1 = descending
            created_at = datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
            datas.append(created_at)
        # print user['id']
        # print datas
        diff = [((datas[i]-datas[i+1]).days) for i in xrange(len(datas)-1)]
        max_period = max(diff)
        # print max_period
        com.update({'id': user_id}, {'$set': {'longest_tweet_interval': max_period}}, upsert=False)


if __name__ == '__main__':

    # print diff_day(datetime(2010, 10,1), datetime(2010,9,1))
    # from lifelines.utils import k_fold_cross_validation
    count_longest_tweeting_period('fed', 'timeline', 'com')
    count_longest_tweeting_period('random', 'timeline', 'scom')
    count_longest_tweeting_period('younger', 'timeline', 'scom')
    read_user_time()

