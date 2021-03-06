import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import pymongo
from ohsn.util import db_util as dbt
from datetime import datetime
import pickle
import numpy as np
import pandas as pd
import ohsn.util.io_util as iot
from lifelines.utils import datetimes_to_durations
import ohsn.util.graph_util as gt
import scipy.stats as stats

def attribute_corre(filename):
    fields = ['liwc_anal.result.posemo',
              'liwc_anal.result.negemo',
              'liwc_anal.result.ingest',
              'liwc_anal.result.bio',
              'liwc_anal.result.body',
              'liwc_anal.result.health',
              'liwc_anal.result.death'
              'liwc_anal.result.anx',
              'liwc_anal.result.anger',
              'liwc_anal.result.sad',
              'liwc_anal.result.i',
              'liwc_anal.result.we',
              'liwc_anal.result.negate',
              'liwc_anal.result.swear',
              'liwc_anal.result.social',
              'liwc_anal.result.family',
              'liwc_anal.result.friend',
              'liwc_anal.result.affect',
            'senti.result.whole.posm',
            # 'senti.result.whole.posstd',
            'senti.result.whole.negm',
            # 'senti.result.whole.negstd',
            'senti.result.whole.scalem',
            # 'senti.result.whole.scalestd',
            'senti.result.whole.N',
            'senti.result.prior.scalem',
            'senti.result.post.scalem'
              ]
    trimed_fields = ['-'.join(field.split('.')[-2:]) for field in fields]
    groups = [
         ('ED', 'fed', 'com', 'fed', 'com_survival', {
                                                        'liwc_anal.result.WC': {'$exists': True},
                                                        'level': 1,
                                                        'senti.result.whole.N': {'$gt': 10}}),
         ('RD', 'random', 'scom', 'random', 'com_survival', {
                                                        'liwc_anal.result.WC': {'$exists': True},
                                                        'senti.result.whole.N': {'$gt': 10}}),
         ('YG', 'younger', 'scom', 'younger', 'com_survival', {
                                                            'liwc_anal.result.WC': {'$exists': True},
                                                            'senti.result.whole.N': {'$gt': 10}})
    ]
    data = []
    for tag, dbname, comname, dbname2, comname2, filter_values in groups:
        com = dbt.db_connect_col(dbname, comname)
        network1 = gt.Graph.Read_GraphML(tag.lower()+'-net-all-active.graphml')

        for user in com.find(filter_values, no_cursor_timeout=True):
            uid = user['id']
            level = user['level']
            values = iot.get_fields_one_doc(user, fields)
            exist = True
            try:
                v = network1.vs.find(name=str(uid))
            except ValueError:
                exist = False
            if exist:
                # friends = set(network1.neighbors(str(uid))) # id or name
                friends = set(network1.successors(str(uid)))
                fatts = []
                if len(friends) > 0:
                    friend_ids = [int(network1.vs[vi]['name']) for vi in friends] # return id
                    print uid in friend_ids
                    print len(friend_ids)
                    fatts = []
                    alive = 0
                    for fid in friend_ids:
                        fu = com.find_one({'id': fid, 'liwc_anal.result.WC':{'$exists':True},
                                                   'senti.result.whole.N': {'$gt': 10}})
                        if fu:
                            fatt = iot.get_fields_one_doc(fu, fields)
                            fatts.append(fatt)
                            alive += 1
                    if len(fatts) > 0:
                        fatts = np.array(fatts)
                        fmatts = np.mean(fatts, axis=0)
                        values.extend(fmatts)
                        data.append([user['id_str'], level, tag, alive, len(friends)] +  values)
    df = pd.DataFrame(data, columns=['uid', 'level',
                                     'group', 'alive_friends', 'all_friends'] +
                                    ['u_'+field for field in trimed_fields] +
                                    ['f_'+tf for tf in trimed_fields] )
    df.to_csv(filename)



def out_nets():
    gt.out_edgelist(dbname='fed', netname='net', filename='fed2net', ego='follower', alter='user', filter={})
    gt.out_edgelist(dbname='fed', netname='net2round', filename='fed3net', ego='follower', alter='user', filter={})
    gt.out_edgelist(dbname='fed', netname='bnet', filename='fed2bnet', ego='id0', alter='id1', filter={'type': {'$in': [1, 2, 3]}})


def out_data():
    net2 = gt.Graph.Read_GraphML('ed-net-all-active.graphml')
    gt.summary(net2)

    com = pd.read_csv('data/fed.com.csv', sep='\t')
    com['posemor'] = com['posemo']/com['affect']
    com['negemor'] = com['negemo']/com['affect']
    com['emor'] = (com['posemo'] - com['negemo']) /com['affect']
    com = com.drop(columns=['followers_day', 'friends_day', 'statuses_day', 'hashtag_pro', 'quote_pro', 'reply_pro', 'retweet_pro', 'dmention_pro'])
    com = com.dropna()
    com = com.set_index(['id'])

    data = []

    name = ['id', 'timeline_count', 'friends_count', 'followers_count', 'statuses_count',
    'affect', 'posemo', 'negemo', 'bio', 'body', 'ingest', 'scalem', 'posm', 'negm', 'level', 'active_day',
    'posemor', 'negemor', 'emor']
     # 'active_day',
    # 'followers_day', 'friends_day', 'statuses_day', 'hashtag_pro', 'quote_pro', 'reply_pro', 'retweet_pro', 'dmention_pro']

    for index, row in com[com.level==1].iterrows():
        record = [index]
        uid = str(index)
        print uid
        record += row.tolist()
        exist = True
        try:
            v = net2.vs.find(name=uid)
        except ValueError:
            exist = False
        if exist:
            record.append(v['alive'])
            record.append(v['duration'])
            # Ego's followings and neighbors (including followings and followers)
            friends = set(net2.successors(uid))
            neighbors = set(net2.neighbors(uid))
            if len(friends) > 0:
                friend_ids = [int(net2.vs[vi]['name']) for vi in friends] # return id
                f_records = []
                ff_records = []
                for fid in friend_ids:
                    if fid in com.index:
                        f_records.append(com.loc[(fid)].tolist())
                    # second-order followings - second-order follower - first-order neighbors
                    ffs = set(net2.successors(str(fid)))
                    followers = set(net2.predecessors(str(fid)))
                    ffs = ffs - followers
                    ffs = ffs - neighbors
                    if len(ffs) > 0:
                        ff_ids = [int(net2.vs[vi]['name']) for vi in ffs] # return id
                        for ffid in ff_ids:
                            if ffid in com.index:
                                ff_records.append(com.loc[(ffid)].tolist())
                if (len(f_records) > 0) and (len(ff_records) > 0):
                    f_records = np.array(f_records)
                    ff_records = np.array(ff_records)
                    f_mean = np.mean(f_records, axis=0)
                    f_sum = np.sum(f_records, axis=0)
                    ff_mean = np.mean(ff_records, axis=0)
                    ff_sum = np.sum(ff_records, axis=0)
                    fnum = len(f_records)
                    ffnum = len(ff_records)
                    data.append(record + f_sum.tolist() + f_mean.tolist() + ff_sum.tolist() + ff_mean.tolist() + [fnum, ffnum] )

    df = pd.DataFrame(data, columns=name  + ['alive', 'duration']+ ['fsum_'+field for field in name[1:]] +
                     ['favg_'+field for field in name[1:]] +  ['ffsum_'+field for field in name[1:]] +
                     ['ffavg_'+field for field in name[1:]]+
                     ['fnum', 'ffnum']
                     )
    df.to_csv('data/peereff.csv')


def out_wwwdata():
    # out peer effect data for www random users.
    # Note that the network directions are opposite with in ED networks
    net2 = gt.Graph.Read_Ncol('data/www.net', directed=True) # users ---> followers
    net2 = gt.giant_component(net2)



    com = pd.read_csv('data/www.newcom.csv', sep='\t')
    com['created_at'] = pd.to_datetime(com['created_at'], format='%a %b %d %H:%M:%S +0000 %Y', errors='ignore')

    com['posemor'] = com['posemo']/com['affect']
    com['negemor'] = com['negemo']/com['affect']
    com['emor'] = (com['posemo'] - com['negemo']) /com['affect']
    com = com.dropna()
    com = com.set_index(['id'])

    data = []

    name = ['id', 'timeline_count', 'friend_count', 'follower_count', 'active_day', 'affect', 'posemo', 'negemo',
    'bio', 'body', 'ingest', 'scalem', 'posm', 'negm', 'created_at', 'posemor', 'negemor', 'emor']
    first_obser = datetime.strptime('Mon Sep 28 20:03:05 +0000 2009', '%a %b %d %H:%M:%S +0000 %Y')

    for index, row in com.iterrows():
        record = [index]
        uid = str(index)
        print uid
        record += row.tolist()
        exist = True
        try:
            v = net2.vs.find(name=uid)
        except ValueError:
            exist = False
        if exist:
            alive = 0
            duration = 0
            if row['created_at'] > first_obser:
                alive = 1
                delt = row['created_at'] - first_obser
                duration = delt.days + 1

            record.append(alive)
            record.append(duration)
            # Ego's followings and neighbors (including followings and followers)
            friends = set(net2.predecessors(uid))
            neighbors = set(net2.neighbors(uid))
            if len(friends) > 0:
                friend_ids = [int(net2.vs[vi]['name']) for vi in friends] # return id
                f_records = []
                ff_records = []
                for fid in friend_ids:
                    if fid in com.index:
                        f_records.append(com.loc[(fid)].tolist())
                    # second-order followings - second-order follower - first-order neighbors
                    ffs = set(net2.predecessors(str(fid)))
                    followers = set(net2.successors(str(fid)))
                    ffs = ffs - followers
                    ffs = ffs - neighbors
                    if len(ffs) > 0:
                        ff_ids = [int(net2.vs[vi]['name']) for vi in ffs] # return id
                        for ffid in ff_ids:
                            if ffid in com.index:
                                ff_records.append(com.loc[(ffid)].tolist())
                if (len(f_records) > 0) and (len(ff_records) > 0):
                    f_records = np.array(f_records)
                    ff_records = np.array(ff_records)
                    f_mean = np.mean(f_records, axis=0)
                    f_sum = np.sum(f_records, axis=0)
                    ff_mean = np.mean(ff_records, axis=0)
                    ff_sum = np.sum(ff_records, axis=0)
                    fnum = len(f_records)
                    ffnum = len(ff_records)
                    data.append(record + f_sum.tolist() + f_mean.tolist() + ff_sum.tolist() + ff_mean.tolist() + [fnum, ffnum] )

    df = pd.DataFrame(data, columns=name  + ['alive', 'duration']+ ['fsum_'+field for field in name[1:]] +
                     ['favg_'+field for field in name[1:]] +  ['ffsum_'+field for field in name[1:]] +
                     ['ffavg_'+field for field in name[1:]]+
                     ['fnum', 'ffnum']
                     )
    df.to_csv('data/wwwpeereff.csv')


def out_undirect_data():
    net2 = gt.Graph.Read_GraphML('ed-net-all-active.graphml')
    net2 = net2.as_undirected(mode="mutual")
    gt.summary(net2)

    components = net2.clusters()
    # net2.vs['group'] = components.membership
    dicts = dict(zip([int(vn) for vn in net2.vs['name']], components.membership))
    print len(dicts), min(components.membership), max(components.membership)

    com = pd.read_csv('data/fed.com.csv', sep='\t')
    com = com.drop(columns=['followers_day', 'friends_day', 'statuses_day', 'hashtag_pro', 'quote_pro', 'reply_pro', 'retweet_pro', 'dmention_pro'])
    com['posemo'] = com['posemo']/com['affect']
    com['negemo'] = com['negemo']/com['affect']
    com = com.dropna()

    uids = com['id'].tolist()
    com = com.set_index(['id'])
    name = ['id', 'timeline_count', 'friends_count', 'followers_count', 'statuses_count',
    'affect', 'posemo', 'negemo', 'bio', 'body', 'ingest', 'scalem', 'posm', 'negm', 'level', 'active_day']
    print uids[:10]
    groups = []
    maxgroups = max(components.membership)
    for i in uids:
        i = int(i)
        if i in dicts:
            groups.append(dicts[i])
        else:
            maxgroups += 1
            groups.append(maxgroups)
    com['group'] = groups
    # com = com.assign(group=groups)
    zscore = lambda x: (x - x.mean())
    levels = com['level']
    com = com.groupby('group')[name[1:]].transform(zscore)
    com['level'] = levels

    print com.head()
    data = []


     # 'active_day',
    # 'followers_day', 'friends_day', 'statuses_day', 'hashtag_pro', 'quote_pro', 'reply_pro', 'retweet_pro', 'dmention_pro']

    for index, row in com[com.level==1].iterrows():
        record = [index]
        uid = str(index)
        print uid
        record += row.tolist()
        exist = True
        try:
            v = net2.vs.find(name=uid)
        except ValueError:
            exist = False
        if exist:
            record.append(v['alive'])
            record.append(v['duration'])
            friends = set(net2.successors(uid))
            if len(friends) > 0:
                friend_ids = [int(net2.vs[vi]['name']) for vi in friends] # return id
                f_records = []
                ff_records = []
                for fid in friend_ids:
                    if fid in com.index:
                        f_records.append(com.loc[(fid)].tolist())
                    ffs = set(net2.successors(str(fid)))
                    ffs = ffs - friends
                    if len(ffs) > 0:
                        ff_ids = [int(net2.vs[vi]['name']) for vi in ffs] # return id
                        for ffid in ff_ids:
                            if ffid in com.index:
                                ff_records.append(com.loc[(ffid)].tolist())
                if (len(f_records) > 0) and (len(ff_records) > 0):
                    f_records = np.array(f_records)
                    ff_records = np.array(ff_records)
                    f_mean = np.mean(f_records, axis=0)
                    f_sum = np.sum(f_records, axis=0)
                    ff_mean = np.mean(ff_records, axis=0)
                    ff_sum = np.sum(ff_records, axis=0)
                    fnum = len(f_records)
                    ffnum = len(ff_records)
                    data.append(record + f_sum.tolist() + f_mean.tolist() + ff_sum.tolist() + ff_mean.tolist() + [fnum, ffnum] )

    df = pd.DataFrame(data, columns=name  + ['alive', 'duration']+ ['fsum_'+field for field in name[1:]] +
                     ['favg_'+field for field in name[1:]] +  ['ffsum_'+field for field in name[1:]] +
                     ['ffavg_'+field for field in name[1:]]+
                     ['fnum', 'ffnum']
                     )
    df.to_csv('data/undir-peereff.csv')

if __name__ == '__main__':
    # attribute_corre('user-friends-attributes-followee.csv')
    # out_nets()
    # uid = iot.get_values_one_field('fed', 'scom', 'id_str')
    # pickle.dump(uid, open('eduid.pick', 'w'))
    # out_data()
    # out_undirect_data()
    out_wwwdata()