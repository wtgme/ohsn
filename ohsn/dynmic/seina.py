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
import pickle
import ohsn.util.io_util as iot
import ohsn.util.graph_util as gt
import scipy.stats as stats


def readprofile(dbname, colname):
    g = gt.Graph.Read_GraphML('data/fed_sub.graphml')
    uids = [int(uid) for uid in g.vs['name']]
    print len(uids)
    field_names = iot.read_fields()
    print len(field_names)
    data = []
    poi = dbt.db_connect_col(dbname, colname)
    for x in poi.find({'id': {'$in': uids}}):
        values = iot.get_fields_one_doc(x, field_names)
        data.append(values)
    df = pd.DataFrame(data=data, columns=field_names)
    df.to_csv('data/' + dbname+'-com'+'.csv')


def out_tid_uid_hashtags(filename='/media/data/feds.tags.txt'):
    fo = open(filename, 'w')
    fo.write(str('tid') + '\t' + str('uid') + '\t' + str('created_at') + '\t' + str('retweet')  + '\t' + str('dbindex') + '\t' + 'tags' + '\n')
    filter = {}
    filter['$where'] = 'this.entities.hashtags.length>0'
    for dbindex, dbname in enumerate(['fed', 'fed2', 'fed3', 'fed4']):
        time = dbt.db_connect_col(dbname, 'timeline')
        for tweet in time.find(filter, no_cursor_timeout=True):
            tid = tweet['id']
            uid = tweet['user']['id']
            retweet = 0
            if 'retweeted_status' in tweet:
                retweet = 1
            created_at = datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
            hashtags = tweet['entities']['hashtags']
            hash_set = set()
            for hash in hashtags:
            # need no .encode('utf-8')
                tag = (hash['text'].encode('utf-8').lower().replace('_', '').replace('-', ''))
                hash_set.add(tag)
            tags = ' '.join(list(hash_set))
            fo.write(str(tid) + '\t' + str(uid) + '\t' + str(created_at) + '\t' + str(retweet)  + '\t' + str(dbindex) + '\t' + tags + '\n')
    fo.flush()
    fo.close()

if __name__ == '__main__':
    # readprofile('fed', 'com')
    # readprofile('fed2', 'com')
    # readprofile('fed3', 'com')
    # readprofile('fed4', 'com')

    out_tid_uid_hashtags()