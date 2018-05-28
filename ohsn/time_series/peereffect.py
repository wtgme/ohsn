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

    com = pd.read_csv('data/fed.com.csv', sep=',')
    com = com.drop(columns=['retweet_count'])
    com = com.dropna()
    com = com.set_index(['id'])
    data = []

    name = [u'id', u'timeline_count', u'followers_count', u'friends_count',
           u'statuses_count', u'favourites_count', u'posemo',
           u'negemo', u'scalem', u'level']

    for index, row in com[com.level==1].iterrows():
        record = []
        uid = str(int(row['id']))
        print uid
        record += row.tolist()
        friends = set(net2.successors(uid))
        if len(friends) > 0:
            friend_ids = [int(net2.vs[vi]['name']) for vi in friends] # return id
            f_records = []
            ff_records = []
            for fid in friend_ids:
                frec = com[com.id==fid]
                if len(frec) == 1:
                    f_records.append(frec.iloc[0].tolist()[1:])
                ffs = set(net2.successors(str(fid)))
                if len(ffs) > 0:
                    ff_ids = [int(net2.vs[vi]['name']) for vi in ffs] # return id
                    for ffid in ff_ids:
                        ffrec = com[com.id==ffid]
                        if len(ffrec) == 1:
                            ff_records.append(ffrec.iloc[0].tolist()[1:])
            if (len(f_records) > 0) and (len(ff_records) > 0):
                f_records = np.array(f_records)
                ff_records = np.array(ff_records)
                f_mean = np.mean(f_records, axis=0)
                f_sum = np.sum(f_records, axis=0)
                ff_mean = np.mean(ff_records, axis=0)
                fnum = len(f_records)
                data.append(record + f_sum.tolist() + f_mean.tolist() + ff_mean.tolist() + [fnum] )

    df = pd.DataFrame(data, columns=name + ['fsum_'+field for field in name[1:]] +
                     ['favg_'+field for field in name[1:]] +
                     ['ffavg_'+field for field in name[1:]]+
                     ['fnum']
                     )
    df.to_csv('data/peereff.csv')

if __name__ == '__main__':
    # attribute_corre('user-friends-attributes-followee.csv')
    # out_nets()
    # uid = iot.get_values_one_field('fed', 'scom', 'id_str')
    # pickle.dump(uid, open('eduid.pick', 'w'))
    out_data()