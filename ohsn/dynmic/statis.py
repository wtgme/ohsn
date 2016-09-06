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


if __name__ == '__main__':
    keys = ['description', 'friends_count', 'friends_count_inc', 'friends_count_dec', 'followers_count', 'followers_count_inc', 'followers_count_dec',
            'statuses_count', 'statuses_count_inc', 'statuses_count_dec', 'net_changes']
    statis('monitor', 'changes', keys)