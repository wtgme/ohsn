# -*- coding: utf-8 -*-
"""
Created on 14:45, 04/04/17

@author: wt

Younger check again at: 2017-04-25 15:46:20+00:00
Random check again at: 2017-04-25 15:46:20+00:00
Fed check again at: 2016-09-29 14:57:39+00:00

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
import ohsn.util.graph_util as gt

def diff_month(d1, d2):
    return (d1.year - d2.year)*12 + d1.month - d2.month


def diff_day(d2, d1):
    delta = d2 - d1
    return delta.days


def read_user_time(filename):
    fields = iot.read_fields()
    trimed_fields = [field.split('.')[-1] for field in fields]
    groups = [
         ('ED', 'fed', 'com', {'liwc_anal.result.WC': {'$exists': True}, 'level': 1}),
         ('RD', 'random', 'scom', {'liwc_anal.result.WC': {'$exists': True}}),
         ('YG', 'younger', 'scom', {'liwc_anal.result.WC': {'$exists': True}})
    ]

    data = []
    for tag, dbname, comname, filter_values in groups:
        com = dbt.db_connect_col(dbname, comname)

        for user in com.find(filter_values, no_cursor_timeout=True):
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
                data.append([user['id_str'], created_at, last_post, scraped_at, average_time,
                             longest_tweet_intervalb, observation_interval, tag, death] + values)

    df = pd.DataFrame(data, columns=['uid', 'created_at', 'last_post', 'scraped_at', 'average_time',
                                     'longest_time_interval', 'observation_interval', 'group',
                                     'event'] + trimed_fields)
    df.to_csv(filename)

def active_days(user):
    # print user['id']
    ts = datetime.strptime(user['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
    try:
        tts = datetime.strptime(user['status']['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
    except KeyError:
        tts = ts
    delta = tts.date() - ts.date()
    days = delta.days+1
    status_count = abs(float(user['statuses_count']))
    friend_count = abs(float(user['friends_count']))
    follower_count = abs(float(user['followers_count']))
    friends_day = friend_count/days
    statuses_day = status_count/days
    followers_day = follower_count/days
    return[friend_count, status_count, follower_count,
           friends_day, statuses_day, followers_day,
           days]


def read_user_time_iv(filename):
    # fields = iot.read_fields()
    fields = ['liwc_anal.result.posemo',
              'liwc_anal.result.negemo',
              'liwc_anal.result.ingest',
              'liwc_anal.result.bio',
              'liwc_anal.result.body',
              'liwc_anal.result.health',
              'liwc_anal.result.death'
              # 'liwc_anal.result.anx',
              # 'liwc_anal.result.anger',
              # 'liwc_anal.result.sad'
              ]
    prof_names = ['friends_count', 'statuses_count', 'followers_count',
        'friends_day', 'statuses_day', 'followers_day', 'days']

    trimed_fields = [field.split('.')[-1] for field in fields]
    groups = [
         ('ED', 'fed', 'com', 'fed2', 'com', '2016-09-29 14:57:39+00:00', {'liwc_anal.result.WC': {'$exists': True}, 'level': 1}),
         ('RD', 'random', 'scom', 'random2', 'com_check', '2017-04-25 15:46:20+00:00', {'liwc_anal.result.WC': {'$exists': True}}),
         ('YG', 'younger', 'scom', 'younger2', 'com_check', '2017-04-25 15:46:20+00:00', {'liwc_anal.result.WC': {'$exists': True}})
    ]

    data = []
    for tag, dbname, comname, dbname2, comname2, second_time, filter_values in groups:
        com = dbt.db_connect_col(dbname, comname)
        com2 = dbt.db_connect_col(dbname2, comname2)
        network1 = gt.Graph.Read_GraphML(tag.lower()+'-net.graphml')
        gt.summary(network1)
        network1_gc = gt.giant_component(network1)
        gt.summary(network1_gc)
        '''Centralities Calculation'''
        eigen = network1_gc.eigenvector_centrality()

        nodes = [int(v['name']) for v in network1_gc.vs]
        eigen_map = dict(zip(nodes, eigen))
        print 'load liwc 2 batches: ' + tag.lower()+'-liwc2stage.csv'
        liwc_df = pd.read_pickle(tag.lower()+'-liwc2stage.csv'+'.pick')

        for user in com.find(filter_values, no_cursor_timeout=True):
            if 'status' in user:
                uid = user['id']
                u2 = com2.find_one({'id': uid})
                if (u2 is None): # protected or delete
                    drop = 1
                    second_scraped_at = datetime.strptime(second_time, '%Y-%m-%d %H:%M:%S+00:00')
                else:
                    second_scraped_at = u2['_id'].generation_time
                    if 'status' not in user and 'status' not in u2: # no tweeting
                        drop = 1
                    elif 'status' not in user and 'status' in u2: # start to post
                        drop = 0
                    elif 'status' in user and 'status' not in u2: # delete
                        drop = 0
                    elif u2['status']['id'] == user['status']['id']: # no new post
                        drop = 1
                    elif u2['status']['id'] != user['status']['id']: # new post
                        drop = 0




                created_at = datetime.strptime(user['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
                scraped_at = user['scrape_timeline_at']
                last_post = datetime.strptime(user['status']['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
                life_time = diff_day(last_post, created_at)
                average_time = float(life_time)/min(1, user['statuses_count'])
                longest_tweet_intervalb = user['longest_tweet_interval']
                u_timeline_count = user['timeline_count']

                observation_interval = diff_day(scraped_at, last_post)
                if (observation_interval-longest_tweet_intervalb) > 30:
                    death = 1
                else:
                    death = 0

                values = iot.get_fields_one_doc(user, fields)
                level = user['level']

                # set users liwc changes
                uvs = liwc_df[liwc_df.user_id == str(uid)].loc[:, trimed_fields]
                # print uvs
                if len(uvs) == 2:
                    changes, priors, posts = [], [], []
                    for name in trimed_fields:
                        old = uvs.iloc[0][name]
                        new = uvs.iloc[1][name]
                        priors.append(old)
                        posts.append(new)
                        changes.append(new - old)
                    liwc_changes = priors + posts + changes
                else:
                    liwc_changes = [None]*(len(trimed_fields)*3)
                u_centrality = eigen_map.get(user['id'], 0)
                values.extend(liwc_changes)
                values.extend(active_days(user))

                '''Get friends' profiles'''
                exist = True
                try:
                    v = network1.vs.find(name=str(uid))
                except ValueError:
                    exist = False
                if exist:
                    friends = set(network1.successors(str(uid)))
                    if len(friends) > 0:
                        friend_ids = [int(network1.vs[vi]['name']) for vi in friends] # return id
                        print uid in friend_ids
                        print len(friend_ids)
                        fatts = []
                        alive = 0
                        for fid in friend_ids:
                            fu = com.find_one({'id': fid, 'liwc_anal.result.WC':{'$exists':True}})
                            fu2 = com2.find_one({'id': fid})
                            if fu != None:
                                fatt = iot.get_fields_one_doc(fu, fields)
                                fatt.extend(active_days(fu))
                                fatt.extend([eigen_map.get(fu['id'], 0)])
                                fatts.append(fatt)

                                if (fu2 is None):
                                    alive += 0
                                else:
                                    if 'status' not in fu and 'status' not in fu2:
                                        alive += 0
                                    elif 'status' not in fu and 'status' in fu2:
                                        alive += 1
                                    elif 'status' in fu and 'status' not in fu2:
                                        alive += 1
                                    elif fu2['status']['id'] == fu['status']['id']:
                                        alive += 0
                                    elif fu2['status']['id'] != fu['status']['id']:
                                        alive += 1

                        # thredhold = user['friends_count']*0.5
                        if len(fatts) > 0:
                            fatts = np.array(fatts)
                            fmatts = np.mean(fatts, axis=0)
                            values.extend(fmatts)
                            paliv = float(alive)/len(fatts)
                            data.append([user['id_str'], level, drop, created_at, last_post, scraped_at, second_scraped_at, average_time,
                             longest_tweet_intervalb, observation_interval, tag, death, u_centrality, u_timeline_count] +
                                        values + [len(fatts), paliv])

    df = pd.DataFrame(data, columns=['uid', 'level', 'dropout', 'created_at', 'last_post', 'scraped_at', 'second_scraped_at',
                                     'average_time', 'longest_time_interval', 'observation_interval',
                                     'group', 'event', 'u_centrality', 'u_timeline_count'] +
                                    ['u_'+field for field in trimed_fields] +
                                    ['u_prior_'+field for field in trimed_fields] +
                                    ['u_post_'+field for field in trimed_fields] +
                                    ['u_change_'+field for field in trimed_fields] +
                                    ['u_'+field for field in prof_names] +
                                    ['f_'+tf for tf in trimed_fields] +
                                    ['f_'+field for field in prof_names] +
                                    ['f_centrality', 'f_num', 'f_palive'])
    df.to_csv(filename)


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

def user_statis():
    groups = [
         ('ED', 'fed', 'com', {'liwc_anal.result.WC': {'$exists': True}, 'level': 1}),
         ('RD', 'random', 'scom', {'liwc_anal.result.WC': {'$exists': True}, 'level': 1}),
         ('YG', 'younger', 'scom', {'liwc_anal.result.WC': {'$exists': True}, 'level': 1})
    ]

    data = []
    for tag, dbname, comname, filter_values in groups:
        com = dbt.db_connect_col(dbname, comname)
        network1 = gt.Graph.Read_GraphML(tag.lower()+'-net.graphml')
        gt.summary(network1)
        network1_gc = gt.giant_component(network1)
        gt.summary(network1_gc)

        users_time = iot.get_values_one_field(dbname, comname, 'id_str', filter_values)
        try:
            v = network1.vs.find(name=str(uid))
        except ValueError:
            exist = False
        if exist:
            friends = set(network1.successors(str(uid)))

def insert_timestamp(dbname, colname):
    com = dbt.db_connect_col(dbname, colname)
    for user in com.find():
        print user['_id'].generation_time


if __name__ == '__main__':

    # print diff_day(datetime(2010, 10,1), datetime(2010,9,1))
    # from lifelines.utils import k_fold_cross_validation
    # count_longest_tweeting_period('fed', 'timeline', 'com')
    # count_longest_tweeting_period('random', 'timeline', 'scom')
    # count_longest_tweeting_period('younger', 'timeline', 'scom')
    # read_user_time('user-durations-2.csv')
    read_user_time_iv('user-durations-iv-2.csv')

    # insert_timestamp('fed2', 'com')
