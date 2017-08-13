# -*- coding: utf-8 -*-
"""
Created on 14:33, 20/04/17

@author: wt
"""

import json
import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
import pymongo
import ohsn.util.db_util as dbt
import ohsn.util.io_util as iot
from os import listdir
from os.path import isfile, join
import ast
import ohsn.util.graph_util as gt
import numpy as np


def store_users_profile():
    com = dbt.db_connect_col('depression', 'neg_com')
    com.create_index("id", unique=True)

    with open('/home/wt/Code/ohsn/ohsn/depression/data/negative/user_profile/written_users_info_detail_list.txt') as data_file:
        for line in data_file.readlines():
            print line
            parsed_json = ast.literal_eval(line.strip())
            try:
                com.insert(parsed_json)
            except pymongo.errors.DuplicateKeyError:
                    pass

def store_tweets():
    times = dbt.db_connect_col('depression', 'neg_timeline')
    times.create_index([('user.id', pymongo.ASCENDING),
                              ('id', pymongo.DESCENDING)])
    times.create_index([('id', pymongo.ASCENDING)], unique=True)

    mypath = '/home/wt/Code/ohsn/ohsn/depression/data/negative/user_tweets'
    onlyfiles = [mypath+'/'+f for f in listdir(mypath) if isfile(join(mypath, f))]
    for file_path in onlyfiles:
        with open(file_path) as data_file:
            print file_path
            for line in data_file.readlines():
                parsed_json = ast.literal_eval(line.strip())
                try:
                    times.insert(parsed_json)
                except pymongo.errors.DuplicateKeyError:
                    pass

def label_positive():
    com = dbt.db_connect_col('depression', 'com')
    with open('/home/wt/Code/ohsn/ohsn/depression/data/positive/positive_users_selections_screennaes.txt') as data_file:
        for line in data_file.readlines():
            print line
            screen_name = line.strip()
            com.update_one({'screen_name': screen_name}, {'$set': {'checked': True}}, upsert=False)

def data_stat():
    # stat for how many users
    stream = dbt.db_connect_col('depression', 'search')
    uids = set()
    for tweet in stream.find({}):
        uids.add(tweet['user']['id'])
    print len(uids)


def network_analysis():
    # output network among depression users
    user1 = iot.get_values_one_field('depression', 'users1', 'id')
    user2 = iot.get_values_one_field('depression', 'users2', 'id')
    print len(user1), len(user2)
    alluser = user1 + user2
    follow_net = gt.load_network_subset('depression', 'net', {'user': {'$in': alluser},
                                                              'follower': {'$in': alluser}})
    gt.net_stat(follow_net)
    follow_net.write_graphml('data/follow_net.graphml')

    for beh in ['retweet', 'communication']:
        print beh
        bnetwork = gt.load_beh_network_subset(userlist=alluser, db_name='depression',
                                              collection='bnet', btype=beh)
        gt.net_stat(bnetwork)
        bnetwork.write_graphml('data/'+beh+'_net.graphml')


def liwc_feature():
    fields = iot.read_fields()
    for field in fields:
        values = iot.get_values_one_field('depression', 'users1', field)
        print field, np.mean(values), np.std(values)


def drop_initials(list_a):
    # discard the zeros in a list
    return [i for i in list_a if i > -1000000000.0]


def network_assort():
    # test network assortative
    gs = ['follow', 'retweet', 'communication']
    fields = iot.read_fields()
    print len(fields)
    for gf in gs:
        g = gt.Graph.Read_GraphML('data/'+gf+'_net.graphml')
        g = gt.giant_component(g)
        gt.net_stat(g)

        for filed in fields:
            g = gt.add_attribute(g, 'foi', 'depression', 'com', filed)
            raw_values = np.array(g.vs['foi'])
            values = drop_initials(raw_values)
            if len(values) > 100:
                output = gf + ',' + filed.split('.')[-1] + ','
                # maxv, minv = np.percentile(values, 97.5), np.percentile(values, 2.5)
                # maxv, minv = max(values), min(values)
                # vs = g.vs.select(foi_ge=minv, foi_le=maxv)
                # sg = g.subgraph(vs)
                raw_assort = g.assortativity('foi', 'foi', directed=True)
                ass_list = []
                for i in xrange(1000):
                    np.random.shuffle(raw_values)
                    g.vs["foi"] = raw_values
                    # vs = g.vs.select(foi_ge=minv, foi_le=maxv)
                    # sg = g.subgraph(vs)
                    ass_list.append(g.assortativity('foi', 'foi', directed=True))

                ass_list = np.array(ass_list)
                amean, astd = np.mean(ass_list), np.std(ass_list)
                absobserved = abs(raw_assort)
                pval = (np.sum(ass_list >= absobserved) +
                        np.sum(ass_list <= -absobserved))/float(len(ass_list))
                zscore = (raw_assort-amean)/astd
                output += format(raw_assort, '.2f') + ',' + format(amean, '.2f') + ',' + \
                          format(astd, '.2f') + ',' + format(zscore, '.2f') + ',' + format(pval, '.2f')
                if pval < 0.001:
                    output += '***'
                    print output
                    continue
                if pval < 0.01:
                    output += '**'
                    print output
                    continue
                if pval < 0.05:
                    output += '*'
                    print output
                    continue
                else:
                    print output
                    continue





if __name__ == '__main__':
    # store_users_profile()
    # store_tweets()
    # label_positive()

    # data_stat()
    network_analysis()
    network_assort()
    # liwc_feature()