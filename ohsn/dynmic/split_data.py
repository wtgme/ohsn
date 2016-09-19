# -*- coding: utf-8 -*-
"""
Created on 14:36, 13/09/16

@author: wt
"""

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
import ohsn.util.db_util as dbt
import pymongo
import ohsn.util.io_util as iot
import ohsn.util.plot_util as pt
import ohsn.util.graph_util as gt
import sys
import pickle
import numpy as np
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import scipy.stats as stats


def split_data(dbname, timename, newtimename):
    db = dbt.db_connect_no_auth(dbname)
    oldtime = db[timename]
    newtime = db[newtimename]
    newtime.create_index([('user.id', pymongo.ASCENDING),
                                  ('id', pymongo.DESCENDING)], unique=False)
    newtime.create_index([('id', pymongo.ASCENDING)], unique=True)

    datepoint = datetime(2016, 04, 06)
    for tweet in oldtime.find({'created_at': {"$gte": datepoint}}, no_cursor_timeout=True).sort([('id', -1)]):
        # print tweet
        try:
            newtime.insert(tweet)
        except pymongo.errors.DuplicateKeyError:
            print tweet['id']
            pass
        oldtime.delete_one({'id': tweet['id']})


def profile_change(dbname, colname, timename):
    # db = dbt.db_connect_no_auth(dbname)
    # com = db[colname]
    # time = db[timename]
    #
    # followee, follower, tweets, users, olddate, newdate, during = [], [], [], [], [], [], []
    # filter = {'liwc_anal.result.i':{'$exists':True}, 'new_liwc_anal.result.i':{'$exists':True}}
    #
    # for user in com.find(filter):
    #     newtweet = time.find({'user.id': user['id']}, no_cursor_timeout=True).sort([('id', -1)]).limit(1)[0]
    #     oldtweet = time.find({'user.id': user['id']}, no_cursor_timeout=True).sort([('id', 1)]).limit(1)[0]
    #     print user['id'], oldtweet['created_at'], newtweet['created_at'], \
    #         (newtweet['created_at'].date() - oldtweet['created_at'].date()).days+1
    #     users.append(user['id'])
    #     olddate.append(oldtweet['created_at'])
    #     newdate.append(newtweet['created_at'])
    #     during.append((newtweet['created_at'].date() - oldtweet['created_at'].date()).days + 1)
    #     follower.append(newtweet['user']['followers_count'] - oldtweet['user']['followers_count'])
    #     followee.append(newtweet['user']['friends_count']- oldtweet['user']['friends_count'])
    #     tweets.append(newtweet['user']['statuses_count']- oldtweet['user']['statuses_count'])
    # df =  pd.DataFrame({'User': users,
    #                     'OldDate': olddate,
    #                     'NewDate': newdate,
    #                     'Follower': follower,
    #                     'Followee': followee,
    #                     'Tweet': tweets,
    #                     'ActiveTime': during})
    # pickle.dump(df, open('data/df.pick', 'w'))
    df = pickle.load(open('data/df.pick', 'r'))
    pt.plot_config()
    df['Followee/Day']=(df.Followee/df.ActiveTime)
    df['Follower/Day']=(df.Follower/df.ActiveTime)
    df['Tweet/Day']=(df.Tweet/df.ActiveTime)
    sns.boxplot(data=df.loc[:, ['Followee', 'Follower', 'Tweet', 'ActiveTime']])
    # sns.boxplot(data=df.loc[:, ['Followee/Day', 'Follower/Day', 'Tweet/Day']])
    plt.ylim(-300, 400)
    plt.show()


def network_change(dbname, comname, netname):
    # filter = {'liwc_anal.result.i':{'$exists':True}, 'new_liwc_anal.result.i':{'$exists':True}}
    # users = iot.get_values_one_field(dbname, comname, 'id', filter)
    # g1 = gt.load_network_subset(users, dbname, netname, {'scraped_times': 2})
    # g2 = gt.load_network_subset(users, dbname, netname, {'scraped_times': 131})
    # pickle.dump(g1, open('data/g1.pick', 'w'))
    # pickle.dump(g2, open('data/g2.pick', 'w'))
    g1 = pickle.load(open('data/g1.pick', 'r'))
    g2 = pickle.load(open('data/g2.pick', 'r'))
    gt.summary(g1)
    gt.summary(g1)
    gt.net_stat(g1)
    gt.net_stat(g2)
    # pt.pdf_plot_one_data(g1.indegree(), 'indegree', linear_bins=False, fit_start=1, fit_end=100)
    pt.plot_pdf_mul_data([np.array(g1.indegree())+1, np.array(g2.indegree())+1],
                           'indegree', ['b', 'r'], ['o', '^'], ['G1', 'G2'],
                               linear_bins=False, central=False, fit=True, savefile='indegree.pdf')

    # g1.write_dot('g1.DOT')
    # g2.write_dot('g2.DOT')
    # pt.power_law_fit(g1.indegree())
    # plot(g1.indegree(), g2.indegree(), 'indegree')
    # plot(g1.outdegree(), g2.outdegree(), 'outdegree')



def plot(list1, list2, name):
    sns.distplot(list1, hist=False, label='G1')
    sns.distplot(list2, hist=False, label='G2')
    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel('k')
    plt.ylabel('PDF')
    plt.savefig(name+'.pdf')
    plt.clf()



def distribution_change(dbname, colname):
    features = [
        'liwc_anal.result.i',
        'liwc_anal.result.we',
        'liwc_anal.result.bio',
        'liwc_anal.result.body',
        'liwc_anal.result.health',
        'liwc_anal.result.posemo',
        'liwc_anal.result.negemo',
        'liwc_anal.result.ingest',
        'liwc_anal.result.anx',
        'liwc_anal.result.anger',
        'liwc_anal.result.sad'
                ]
    names = ['I', 'We', 'Bio', 'Body', 'Health', 'Posemo', 'Negemo', 'Ingest', 'Anx', 'Anger', 'Sad']
    df = pd.DataFrame()
    filter = {'liwc_anal.result.i':{'$exists':True}, 'new_liwc_anal.result.i':{'$exists':True}}

    for i in xrange(len(features)):
        feature = features[i]
        old_values = iot.get_values_one_field(dbname, colname, feature, filter)
        df1 = pd.DataFrame({'Feature': names[i], 'Time': 'Before', 'Values': old_values})
        new_values = iot.get_values_one_field(dbname, colname, 'new_'+feature, filter)
        df2 = pd.DataFrame({'Feature': names[i], 'Time': 'After', 'Values': new_values})
        df1 = df1.append(df2)
        if len(df) == 0:
            df = df1
        else:
            df = df.append(df1)
        '''Plot Individual'''
        # sns.distplot(old_values, hist=False, label='Before')
        # sns.distplot(new_values, hist=False, label='After')
        d, p = stats.ks_2samp(old_values, new_values)
        print ('%.3f(%.3f), %.3f(%.3f), %.3f(%.3f)' %((np.mean(old_values)), (np.std(old_values)),
                                                 (np.mean(new_values)), (np.std(new_values)), d, p))
        # plt.xlabel(feature)
        # plt.ylabel('PDF')
        # # plt.show()
        # plt.savefig(dbname+'_'+feature+'_time.pdf')
        # plt.clf()
    sns.set(style="whitegrid", palette="pastel", color_codes=True)
    # sns.violinplot(x="Feature", y="Values", hue="Time", data=df, split=True,
    #                inner="quart", palette={"Before": "b", "After": "y"})
    # sns.despine(left=True)
    sns.boxplot(x="Feature", y="Values", hue="Time", data=df, palette="PRGn")
    sns.despine(offset=10, trim=True)
    plt.show()

if __name__ == '__main__':
    """Split data in two time periods"""
    # split_data('ded', 'timeline', 'newtimeline')
    # split_data('drd', 'timeline', 'newtimeline')
    # split_data('dyg', 'timeline', 'newtimeline')
    # print sys.argv[1], sys.argv[2], sys.argv[3]
    # split_data(sys.argv[1], sys.argv[2], sys.argv[3])

    """Compare difference of LIWC features with times"""
    # distribution_change('dyg', 'com')

    '''Statistics of profile changes'''
    # profile_change('ded', 'com', 'newtimeline')

    '''Statistics of network changes'''
    network_change('ded', 'com', 'net')