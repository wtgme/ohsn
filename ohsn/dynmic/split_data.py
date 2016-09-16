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
import sys
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
        newtime.insert(tweet)
        oldtime.delete_one({'id': tweet['id']})


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
        print ('\mu_b=%.3f(%.3f), \mu_a=%.3f(%.3f), ks=%.3f(%.3f)' %((np.mean(old_values)), (np.std(old_values)),
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
    distribution_change('dyg', 'com')

