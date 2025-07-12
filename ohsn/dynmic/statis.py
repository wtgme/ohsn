# -*- coding: utf-8 -*-
"""
Created on 22:23, 05/09/16

@author: wt
This script is count statistics of changes
"""

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
import ohsn.util.db_util as dbt
import ohsn.util.plot_util as pt
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import pickle


def statis(dbname, colname, keys):
    db = dbt.db_connect_no_auth(dbname)
    col = db[colname]
    counts = {'ded': 3353, 'drd': 4625, 'dyg': 1945}
    netcount = {'ded': 52416, 'drd': 907692, 'dyg': 23126}
    data = {}
    date = set()
    for record in col.find().sort([('statis_index', 1)]):
        print record['statis_index']
        dataset = record['dataset']
        for key in keys:
            value = record.get(key, 0.0)

            feat_data = data.get(key, {})
            dataset_feat_data = feat_data.get(dataset, [])
            if key == 'net_changes':
                if len(dataset_feat_data) > 0:
                    value += dataset_feat_data[-1]
                else:
                    value += netcount[dataset]
            else:
                value = float(value)/counts[dataset]
            dataset_feat_data.append(value)
            feat_data[dataset] = dataset_feat_data
            data[key] = feat_data
        datev = datetime.strptime(record['statis_at'], '%a %b %d %H:%M:%S +0000 %Y')
        date.add(datetime(datev.year, datev.month, datev.day))
    print date
    date = sorted(list(date))
    print date
    for key in data.keys():
        feature_data = data[key]
        ED = feature_data['ded']
        RD = feature_data['drd']
        YG = feature_data['dyg']
        # print len(ED), len(RD), len(YG), len(date)
        df = pd.DataFrame({'ED': ED,
                           'RD': RD, 'YG': YG,
                           'Date': date}, index=date)
        df.plot()
        plt.legend(loc='best')
        # plt.show()
        plt.savefig(key+'-all.pdf')
        plt.clf()


def active_user(dbname, comname, timename):
    db = dbt.db_connect_no_auth(dbname)
    com = db[comname]
    time = db[timename]
    date = []
    for user in com.find({'timeline_count': {'$gt': 0}}):
        last_tweet = time.find({'user.id': user['id']},
                    {'id':1, 'user':1, 'created_at': 1}).sort([('id', -1)]).limit(1)[0]  # sort: 1 = ascending, -1 = descending
        datev = last_tweet['created_at']
        if isinstance(datev, basestring):
            datev = datetime.strptime(datev, '%a %b %d %H:%M:%S +0000 %Y')
        date.append(datetime(datev.year, datev.month, datev.day))
        # print user['screen_name'], datetime(datev.year, datev.month, datev.day)
    df = pd.DataFrame({'PED': date}, index=date)
    df.groupby([df.PED.dt.year, df.PED.dt.month]).count().plot(kind="bar")
    plt.xlabel('(Year, Month)')
    plt.ylabel('Count')
    plt.show()


def transform_date(dbname, comname):
    db = dbt.db_connect_no_auth(dbname)
    time = db[comname]
    for tweet in time.find({'created_at':{'$type': 2}}):
        datev = tweet['created_at']
        # if isinstance(datev, basestring):
        #     # print '--------------'
        #     # print datev
        datev = datetime.strptime(datev, '%a %b %d %H:%M:%S +0000 %Y')
        # print datev
        time.update_one({'id': tweet['id']}, {'$set': {'created_at': datev}}, upsert=False)


def active_user_list(dbname, comname, timename):
    db = dbt.db_connect_no_auth(dbname)
    time = db[timename]
    com = db[comname]
    date = []
    pred_users = pickle.load(open('data/ed-rel.pick', 'r'))
    for uid in pred_users:
        user = com.find_one({'id': int(uid)})
        if user['level'] != 1:
            last_tweet = time.find({'user.id': int(uid)},
                        {'id':1, 'user':1, 'created_at': 1}).sort([('id', -1)]).limit(1)[0]  # sort: 1 = ascending, -1 = descending
            datev = last_tweet['created_at']
            if isinstance(datev, basestring):
                datev = datetime.strptime(datev, '%a %b %d %H:%M:%S +0000 %Y')
            date.append(datetime(datev.year, datev.month, datev.day))
            # print user['screen_name'], datetime(datev.year, datev.month, datev.day)
    print len(date)
    df = pd.DataFrame({'PredictED_nonED': date}, index=date)
    df.groupby([df.PredictED_nonED.dt.year, df.PredictED_nonED.dt.month]).count().plot(kind="bar")
    plt.xlabel('(Year, Month)')
    plt.ylabel('Count')
    plt.show()



if __name__ == '__main__':
    """Statis Changes"""
    # keys = ['description', 'friends_count', 'friends_count_inc', 'friends_count_dec', 'followers_count', 'followers_count_inc', 'followers_count_dec',
    #         'statuses_count', 'statuses_count_inc', 'statuses_count_dec', 'net_changes']
    # statis('monitor', 'changes', keys)

    """Statis active users"""
    # active_user('fed', 'com', 'timeline')

    # active_user_list('fed', 'com', 'timeline')

    """Transform date format"""
    transform_date('ded', 'timeline')
    # transform_date('drd', 'timeline')
    # transform_date('dyg', 'timeline')
    # print sys.argv[1], sys.argv[2]
    # transform_date(sys.argv[1], sys.argv[2])