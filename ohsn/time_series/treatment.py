# -*- coding: utf-8 -*-
"""
Created on 13:40, 10/03/17

@author: wt

This is analyze whether treatment is effective for pro-recovery users
"""

from os import path
import sys
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import ohsn.util.db_util as dbt
import ohsn.util.io_util as iot
import ohsn.util.graph_util as gt
from ohsn.edrelated import edrelatedcom
import pymongo
import re
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import ohsn.lexiconsmaster.liwc_timeline_processor as liwcp
import pandas as pd


def count_recovered_user():
    times = dbt.db_connect_col('fed', 'recover')
    users = list()
    for tweet in times.find():
        if 'recovered' in tweet:
            print ' '.join(tweet['text'].split())
            users.append(tweet['user']['id'])
    print len(set(users))


def control_users():
    com = dbt.db_connect_col('fed', 'scom')
    recovery_user = set(iot.get_values_one_field('fed', 'recover', 'user.id'))
    control_com = dbt.db_connect_col('fed', 'control_com')
    control_com.create_index("id", unique=True)
    for user in com.find():
        if user['id'] not in recovery_user:
            control_com.insert(user)

def split_control():
    ## the mean split point of treatment are 0.330912888352
    times = dbt.db_connect_col('fed', 'timeline')
    control = dbt.db_connect_col('fed', 'control_com')
    prior = dbt.db_connect_col('fed', 'prior_control')
    prior.create_index([('user.id', pymongo.ASCENDING),
                          ('id', pymongo.DESCENDING)])
    prior.create_index([('id', pymongo.ASCENDING)], unique=True)

    post = dbt.db_connect_col('fed', 'post_control')
    post.create_index([('user.id', pymongo.ASCENDING),
                          ('id', pymongo.DESCENDING)])
    post.create_index([('id', pymongo.ASCENDING)], unique=True)

    for user in control.find(no_cursor_timeout=True):
        timline_count = user['timeline_count']
        cut = int(timline_count * 0.33)
        count = 0
        for tweet in times.find({'user.id': user['id']}).sort([('id', 1)]):  # sort: 1 = ascending, -1 = descending
            if count < cut:
                try:
                    prior.insert(tweet)
                except pymongo.errors.DuplicateKeyError:
                    pass
            else:
                try:
                    post.insert(tweet)
                except pymongo.errors.DuplicateKeyError:
                    pass
            count += 1

def split_treatment():
    rec, proed = edrelatedcom.rec_proed() ## based on profiles
    times = dbt.db_connect_col('fed', 'timeline')
    prior = dbt.db_connect_col('fed', 'prior_treat')
    prior.create_index([('user.id', pymongo.ASCENDING),
                          ('id', pymongo.DESCENDING)])
    prior.create_index([('id', pymongo.ASCENDING)], unique=True)

    post = dbt.db_connect_col('fed', 'post_treat')
    post.create_index([('user.id', pymongo.ASCENDING),
                          ('id', pymongo.DESCENDING)])
    post.create_index([('id', pymongo.ASCENDING)], unique=True)

    for user in rec:
        Find = False
        for tweet in times.find({'user.id': int(user)}).sort([('id', 1)]):  # sort: 1 = ascending, -1 = descending
            if ('retweeted_status' not in tweet) and ('quoted_status' not in tweet):
                text = tweet['text'].encode('utf8')
                text = re.sub(r"(?:(RT\ ?@)|@|https?://)\S+", "", text) # replace RT @, @ and http://
                text = text.strip().lower()
                if 'treatment' in text or 'therap' in text \
                       or 'doctor' in text:
                    Find = True
            if Find:
                post.insert(tweet)
            else:
                prior.insert(tweet)



def count_recovery_tweets(dbname, comname):
    times = dbt.db_connect_col(dbname, 'timeline')
    com = dbt.db_connect_col(dbname, comname)
    recovery = set(iot.read_ed_recovery_hashtags())
    for user in com.find({'level': 1}, no_cursor_timeout=True):
        uid = user['id']
        count = 0
        for tweet in times.find({'user.id': uid, '$where': 'this.entities.hashtags.length>0'}, no_cursor_timeout=True):  # sort: 1 = ascending, -1 = descending
            # if ('retweeted_status' not in tweet) and ('quoted_status' not in tweet):
            #     text = tweet['text'].encode('utf8')
            #     text = re.sub(r"(?:(RT\ ?@)|@|https?://)\S+", "", text) # replace RT @, @ and http://
            #     text = text.strip().lower()
            #     if 'treatment' in text or 'therap' in text \
            #            or 'doctor' in text or 'recover' in text:
            #         count += 1
            hashtags = tweet['entities']['hashtags']
            for hash in hashtags:
                value = hash['text'].encode('utf-8').lower().replace('_', '').replace('-', '')
                if value in recovery:
                    count += 1
        com.update({'id': uid}, {'$set': {'recovery_tweets': count}}, upsert=False)




def filter_user():
    prior = dbt.db_connect_col('fed', 'prior_treat')
    post = dbt.db_connect_col('fed', 'post_treat')
    com = dbt.db_connect_col('fed', 'scom')

    treat_com = dbt.db_connect_col('fed', 'treat_com')
    treat_com.create_index("id", unique=True)

    prior_user = iot.get_values_one_field('fed', 'prior_treat', 'user.id')
    post_user = iot.get_values_one_field('fed', 'post_treat', 'user.id')
    print len(set(prior_user)), len(set(post_user)), len(set(prior_user).intersection(set(post_user)))
    users = list()
    propotions = list()
    for uid in set(prior_user).intersection(set(post_user)):
        count_prior = prior.count({'user.id': uid})
        count_post = post.count({'user.id': uid})
        if count_prior > 0 and count_post > 0:
            users.append(uid)
            propotions.append(float(count_prior)/(count_prior + count_post))

    print len(users)
    print np.mean(propotions)
    # sns.distplot(propotions)
    # plt.show()

    # for uid in users:
    #     user = com.find_one({'id': uid})
    #     treat_com.insert(user)


def liwc_process():
    liwcp.process_db('fed', 'treat_com', 'prior_treat', 'prior_liwc')
    liwcp.process_db('fed', 'treat_com', 'post_treat', 'post_liwc')
    liwcp.process_db('fed', 'control_com', 'prior_control', 'prior_liwc')
    liwcp.process_db('fed', 'control_com', 'post_control', 'post_liwc')


def compare_distribute(dbname, comname):
    user = iot.get_values_one_field(dbname, comname, 'id', {'prior-liwc.result.WC':{'$exists': True},
                                                                'post-liwc.result.WC':{'$exists': True}})
    print len(user)
    print user
    features = [
        '.result.i',
        '.result.we',
        '.result.bio',
        '.result.body',
        '.result.health',
        '.result.posemo',
        '.result.negemo',
        '.result.ingest',
        '.result.anx',
        '.result.anger',
        '.result.sad'
        # '.result.work'
        # '.result.future'
                ]
    names = [
        'I', 'We',
             'Bio', 'Body', 'Health', 'Posemo', 'Negemo', 'Ingest', 'Anx', 'Anger', 'Sad',
        # 'Work',
        # 'Future'
    ]
    df = []
    for i in xrange(len(features)):
        feature = features[i]
        prior_values = iot.get_values_one_field(dbname, comname, 'prior-liwc'+feature, {'id':{'$in': user}})
        post_values = iot.get_values_one_field(dbname, comname, 'post-liwc'+feature, {'id':{'$in': user}})
        # sns.kdeplot(np.array(prior_values), label="Prior")
        # sns.kdeplot(np.array(post_values), label="Post")
        # plt.legend()
        # sns.plt.title(feature)
        # plt.show()
        # plt.clf()
        df_prior = pd.DataFrame({'Feature': names[i], 'Group': 'Prior', 'Values': prior_values})
        df_post = pd.DataFrame({'Feature': names[i], 'Group': 'Post', 'Values': post_values})

        df.append(df_prior)
        df.append(df_post)
    df = pd.concat(df)
    sns.set(style="whitegrid", palette="pastel", color_codes=True)
    sns.boxplot(x="Feature", y="Values", hue="Group", data=df, palette="PRGn")
    # sns.despine(offset=10, trim=True)
    plt.show()


def out_data():
    control = dbt.db_connect_col('fed', 'control_com')
    treat = dbt.db_connect_col('fed', 'treat_com')
    control_user = iot.get_values_one_field('fed', 'control_com', 'id', {'prior_liwc.result.WC':{'$exists': True},
                                                                'post_liwc.result.WC':{'$exists': True}})
    treat_user = iot.get_values_one_field('fed', 'treat_com', 'id', {'prior_liwc.result.WC':{'$exists': True},
                                                                'post_liwc.result.WC':{'$exists': True}})
    data = []
    fields = iot.read_fields()
    prefix = ['prior_liwc', 'post_liwc']
    for i in xrange(2):
        uids = [control_user, treat_user][i]
        for uid in uids:
            user = [control, treat][i].find_one({'id': uid})
            for j in xrange(2):
                fields_new = ['id_str']+[field.replace('liwc_anal', prefix[j]) for field in fields]
                values = iot.get_fields_one_doc(user, fields_new)
                data.append(values+[i, j])

    df = pd.DataFrame(data, columns=['id']+[field.split('.')[-1] for field in fields]+['treated', 'time'])

    df.to_csv('treatment.csv')






if __name__ == '__main__':
    # split_treatment()
    # filter_user()
    #
    # liwc_process()
    #
    # # compare_distribute('fed', 'control_com')
    #
    # # -------------control group-----------------------
    # control_users()
    # split_control()
    # out_data()

    count_recovery_tweets('fed2', 'com')