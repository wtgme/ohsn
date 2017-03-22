# -*- coding: utf-8 -*-
"""
Created on 10:09, 08/11/16

@author: wt

This script is to explore that users' emotions would lead to their dropouts in Twitter
"""

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

from ohsn.util import db_util as dbt
from ohsn.util import io_util as iot
from ohsn.util import graph_util as gt
from ohsn.api import profiles_check
import numpy as np
from ohsn.util import plot_util as pltt
from datetime import datetime
import pandas as pd
import pickle


print 'Centrality Calculate .........'
# users = iot.get_values_one_field('fed', 'com', 'id', {'level': {'$lt': 3}})

# print 'Number of users', len(users)
# network1 = gt.load_network_subset('fed', 'net', {'user': {'$in': users}, 'follower': {'$in': users}})
# network1 = gt.load_network('fed', 'net')
# pickle.dump(network1, open('net.pick', 'w'))
network1 = pickle.load(open('net.pick','r'))

'''Centralities Calculation'''
eigen = network1.eigenvector_centrality()
# closeness = network.closeness()
# betweenness = network.betweenness()
# print len(eigen), len(closeness), len(betweenness)

nodes = [int(v['name']) for v in network1.vs]
print len(nodes), len(eigen)
print type(nodes), type(eigen)
eigen_map = dict(zip(nodes, eigen))
print eigen_map.get(nodes[1]), type(eigen_map.get(nodes[1]))
# closeness_map = dict(zip(nodes, closeness))
# betweenness_map = dict(zip(nodes, betweenness))
print 'Centrality Calculate .........'


def friend_user_change(dbname1, dbname2, comname1, comname2):
    filter_que = {'level': 1, 'liwc_anal.result.WC':{'$exists':True}}
    user2 = iot.get_values_one_field(dbname2, comname2, 'id', filter_que)
    fields = ['liwc_anal.result.posemo', 'liwc_anal.result.negemo', 'liwc_anal.result.body', 'liwc_anal.result.ingest']
    network1 = gt.load_network(dbname1, 'net')
    network2 = gt.load_network(dbname2, 'net')
    for field in fields:
        print '-----------------%s----------------' %field
        user_changes, friends_changes = [], []
        for uid in user2:
            user_feature_old = iot.get_values_one_field(dbname1, comname1, field, {'id': uid})
            user_feature_new = iot.get_values_one_field(dbname2, comname2, field, {'id': uid})
            if len(user_feature_old) != len(user_feature_new) and len(user_feature_new) != 1:
                print 'User feature value length %d, %d' %(len(user_feature_old), len(user_feature_new))
            user_change = np.mean(user_feature_new) - np.mean(user_feature_old)
            exist = True
            try:
                v = network1.vs.find(name=str(uid))
                v = network2.vs.find(name=str(uid))
            except ValueError:
                exist = False
            if exist:
                friends_old = network1.successors(str(uid))
                friends_new = network2.successors(str(uid))
                old_friend_ids = [int(network1.vs[v]['name']) for v in friends_old]
                new_friend_ids = [int(network2.vs[v]['name']) for v in friends_new]
                if len(old_friend_ids) != len(new_friend_ids):
                    print 'Friend feature value length %d, %d' % (len(old_friend_ids), len(new_friend_ids))
                friends_feature_old = iot.get_values_one_field(dbname1, comname1, field, {'id': {'$in': old_friend_ids}})
                friends_feature_new = iot.get_values_one_field(dbname2, comname2, field, {'id': {'$in': new_friend_ids}})
                friend_change = np.mean(friends_feature_new) - np.mean(friends_feature_old)
                friends_changes.append(friend_change)
                user_changes.append(user_change)
        pltt.correlation(friends_changes, user_changes, r'$\Delta$(F_'+field+')', r'$\Delta$(U_'+field+')', field+'-friend-user.pdf')


def active_days(user):
    # print user['id']
    ts = datetime.strptime(user['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
    tts = datetime.strptime(user['status']['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
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


def before_after(u1, u2):
    u1tts = datetime.strptime(u1['status']['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
    u2tts = datetime.strptime(u2['status']['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
    delta = u1tts.date() - u2tts.date()
    if delta.days >= 0:
        return 1
    else:
        return 0
    

def emotion_dropout_IV_split(dbname1, dbname2, comname1, comname2):
    '''
    Split followees and followers as different variables
    :param dbname1:
    :param dbname2:
    :param comname1:
    :param comname2:
    :return:
    '''
    filter_que = {'level': 1, 'liwc_anal.result.WC':{'$exists': True}}
    user1 = iot.get_values_one_field(dbname1, comname1, 'id', filter_que)
    com1 = dbt.db_connect_col(dbname1, comname1)
    com2 = dbt.db_connect_col(dbname2, comname2)
    fields = ['liwc_anal.result.posemo',
              'liwc_anal.result.negemo',
              'liwc_anal.result.anx',
              'liwc_anal.result.anger',
              'liwc_anal.result.sad'
              ]
    prof_names = ['friends_count', 'statuses_count', 'followers_count',
        'friends_day', 'statuses_day', 'followers_day', 'days', 'eigenvector']
    attr_names = ['uid', 'attr']
    attr_names.extend(['u_'+field.split('.')[-1] for field in fields])
    attr_names.extend(['u_'+field for field in prof_names])
    attr_names.extend(['fr_'+field.split('.')[-1] for field in fields])
    attr_names.extend(['fr_'+field for field in prof_names])
    attr_names.extend(['fr_num', 'fr_palive'])
    attr_names.extend(['fo_'+field.split('.')[-1] for field in fields])
    attr_names.extend(['fo_'+field for field in prof_names])
    attr_names.extend(['fo_num', 'fo_palive'])
    attr_names.extend(['co_'+field.split('.')[-1] for field in fields])
    attr_names.extend(['co_'+field for field in prof_names])
    attr_names.extend(['co_num', 'co_palive'])
    print attr_names
    attr_length = len(fields) + len(prof_names) + 2
    # network1 = gt.load_network(dbname1, 'net')

    '''Centralities Calculation'''
    # eigen = network1.eigenvector_centrality()
    # closeness = network1.closeness()
    # betweenness = network1.betweenness()
    # nodes = [int(v['name']) for v in network1.vs]
    # eigen_map = dict(zip(nodes, eigen))
    # closeness_map = dict(zip(nodes, closeness))
    # betweenness_map = dict(zip(nodes, betweenness))

    data = []
    for uid in user1:
        row = [uid]
        u1 = com1.find_one({'id': uid})
        u2 = com2.find_one({'id': uid})
        if u2 is None or u2['timeline_count'] == 0:
            row.append(1)
        else:
            row.append(0)
        uatt = iot.get_fields_one_doc(u1, fields)
        row.extend(uatt)
        row.extend(active_days(u1))
        row.extend([eigen_map.get(u1['id'])])


        exist = True
        try:
            v = network1.vs.find(name=str(uid))
        except ValueError:
            exist = False
        if exist:
            print '--------------------user %d---------------' %uid
            followees = set([int(network1.vs[v]['name']) for v in network1.successors(str(uid))])
            followers = set([int(network1.vs[v]['name']) for v in network1.predecessors(str(uid))])
            common = followees.intersection(followers)
            followees = followees - common
            followers = followers - common
            for friend_ids in [followees, followers, common]:
                if len(friend_ids) > 0:
                    # friend_ids = [int(network1.vs[v]['name']) for v in friends]
                    print uid in friend_ids
                    print len(friend_ids)
                    fatts = []
                    alive = 0
                    for fid in friend_ids:
                        fu = com1.find_one({'id': fid, 'liwc_anal.result.WC':{'$exists':True}, 'status':{'$exists':True}})
                        fu2 = com2.find_one({'id': fid})
                        if fu != None:
                            fatt = iot.get_fields_one_doc(fu, fields) # Friends' LIWC
                            fatt.extend(active_days(fu))
                            fatt.extend([eigen_map.get(fu['id'])])

                            fatts.append(fatt)
                            if fu2 is None or fu2['timeline_count'] == 0:
                                alive += 0
                            else:
                                alive += 1
                    if len(fatts) > 0:
                        fatts = np.array(fatts)
                        fmatts = np.mean(fatts, axis=0)
                        row.extend(fmatts)
                        row.append(len(fatts))
                        paliv = float(alive)/len(fatts)
                        print 'Alive %d %d %.3f' % (alive, len(fatts), paliv)
                        row.append(paliv)
                else:
                    row.extend([None] * attr_length)
            # friends = followers # followers
            # if len(friends) > 0:
            #     friend_ids = [int(network1.vs[v]['name']) for v in friends]
            #     print uid in friend_ids
            #     print len(friend_ids)
            #     fatts = []
            #     alive = 0
            #     for fid in friend_ids:
            #         fu = com1.find_one({'id': fid, 'liwc_anal.result.WC':{'$exists':True}, 'status':{'$exists':True}})
            #         fu2 = com2.find_one({'id': fid})
            #         if fu != None:
            #             fatt = iot.get_fields_one_doc(fu, fields)
            #             fatt.extend(active_days(fu))
            #             fatts.append(fatt)
            #             if fu2 is None or fu2['timeline_count'] == 0:
            #                 alive += 0
            #             else:
            #                 alive += 1
            #     if len(fatts) > 0:
            #         fatts = np.array(fatts)
            #         fmatts = np.mean(fatts, axis=0)
            #         row.extend(fmatts)
            #         row.append(len(fatts))
            #         paliv = float(alive)/len(fatts)
            #         print 'Alive %d %d %.3f' % (alive, len(fatts), paliv)
            #         row.append(paliv)
        # print row
        data.append(row)
    df = pd.DataFrame(data, columns=attr_names)
    df.to_csv('data-attr-split.csv', index = False)


def emotion_dropout_IV_following(dbname1, dbname2, comname1, comname2):
    '''
    Only use following stats
    :param dbname1:
    :param dbname2:
    :param comname1:
    :param comname2:
    :return:
    '''
    print 'load liwc 2 batches'
    df = pd.read_pickle('ed-liwc2stage.csv'+'.pick')
    filter_que = {'level': 1, 'liwc_anal.result.WC':{'$exists': True}}
    user1 = iot.get_values_one_field(dbname1, comname1, 'id', filter_que)
    com1 = dbt.db_connect_col(dbname1, comname1)
    com2 = dbt.db_connect_col(dbname2, comname2)
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
    trimed_fields = [field.split('.')[-1] for field in fields]
    prof_names = ['friends_count', 'statuses_count', 'followers_count',
        'friends_day', 'statuses_day', 'followers_day', 'days', 'eigenvector']
    attr_names = ['uid', 'attr']
    attr_names.extend(['u_'+field for field in trimed_fields])
    attr_names.extend(['u_prior_'+field for field in trimed_fields])
    attr_names.extend(['u_post_'+field for field in trimed_fields])
    attr_names.extend(['u_change_'+field for field in trimed_fields])
    attr_names.extend(['u_'+field for field in prof_names])
    attr_names.extend(['u_recovery_tweets', 'u_timeline_count'])
    attr_names.extend(['f_'+field.split('.')[-1] for field in fields])
    attr_names.extend(['f_'+field for field in prof_names])
    attr_names.extend(['f_timeline_count', 'f_num', 'f_palive'])
    print attr_names


    data = []
    for uid in user1:
        # set uid
        row = [uid]
        # set attrition states
        u1 = com1.find_one({'id': uid})
        u2 = com2.find_one({'id': uid})
        if u2 is None or u2['timeline_count'] == 0:
            row.append(1)
        else:
            row.append(0)
        # set users liwc feature
        uatt = iot.get_fields_one_doc(u1, fields)
        row.extend(uatt)
        # set users liwc changes
        uvs = df[df.user_id == str(uid)].loc[:, trimed_fields]
        # print uvs
        if len(uvs) == 2:
            changes, priors, posts = [], [], []
            for name in trimed_fields:
                old = uvs.iloc[0][name]
                new = uvs.iloc[1][name]
                priors.append(old)
                posts.append(new)
                changes.append(new - old)
            row.extend(priors)
            row.extend(posts)
            row.extend(changes)
        else:
            row.extend([None]*(len(trimed_fields)*3))

        # set profile, active days and eigenvector centrality
        row.extend(active_days(u1))
        row.extend([eigen_map.get(u1['id'])])
        row.extend([u1['recovery_tweets'], u1['timeline_count']])

        exist = True
        try:
            v = network1.vs.find(name=str(uid))
        except ValueError:
            exist = False
        if exist:
            # friends = set(network1.neighbors(str(uid))) # id or name
            friends = set(network1.successors(str(uid)))
            if len(friends) > 0:
                friend_ids = [int(network1.vs[vi]['name']) for vi in friends] # return id
                print uid in friend_ids
                print len(friend_ids)
                fatts = []
                alive = 0
                for fid in friend_ids:
                    fu = com1.find_one({'id': fid, 'liwc_anal.result.WC':{'$exists':True}, 'status':{'$exists':True}})
                    fu2 = com2.find_one({'id': fid})
                    if fu != None:
                        fatt = iot.get_fields_one_doc(fu, fields)
                        fatt.extend(active_days(fu))
                        fatt.extend([eigen_map.get(fu['id'])])
                        fatt.extend([fu['timeline_count']])
                        fatts.append(fatt)

                        if fu2 is None or fu2['timeline_count'] == 0:
                            alive += 0
                        else:
                            alive += 1
                if len(fatts) > 0:
                    fatts = np.array(fatts)
                    fmatts = np.mean(fatts, axis=0)
                    row.extend(fmatts)
                    row.append(len(fatts))
                    paliv = float(alive)/len(fatts)
                    print 'Alive %d %d %.3f' % (alive, len(fatts), paliv)
                    row.append(paliv)
        # print row
        data.append(row)
    df = pd.DataFrame(data, columns=attr_names)
    df.to_csv('data-attr-following.csv', index = False)



def emotion_recovery_IV_following(dbname1, dbname2, comname1, comname2):
    '''
    Only use following stats
    :param dbname1:
    :param dbname2:
    :param comname1:
    :param comname2:
    :return:
    '''
    print 'load liwc 2 batches'
    df = pd.read_pickle('ed-liwc2stage.csv'+'.pick')
    filter_que = {'level': 1, 'liwc_anal.result.WC':{'$exists': True}}
    user1 = iot.get_values_one_field(dbname1, comname1, 'id', filter_que)
    com1 = dbt.db_connect_col(dbname1, comname1)
    com2 = dbt.db_connect_col(dbname2, comname2)
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
    trimed_fields = [field.split('.')[-1] for field in fields]
    prof_names = ['friends_count', 'statuses_count', 'followers_count',
        'friends_day', 'statuses_day', 'followers_day', 'days', 'eigenvector']
    attr_names = ['uid', 'attr', 'u_timeline_count_2p']
    attr_names.extend(['u_'+field for field in trimed_fields])
    attr_names.extend(['u_prior_'+field for field in trimed_fields])
    attr_names.extend(['u_post_'+field for field in trimed_fields])
    attr_names.extend(['u_change_'+field for field in trimed_fields])
    attr_names.extend(['u_'+field for field in prof_names])
    attr_names.extend(['u_recovery_tweets', 'u_timeline_count'])
    attr_names.extend(['f_'+field.split('.')[-1] for field in fields])
    attr_names.extend(['f_'+field for field in prof_names])
    attr_names.extend(['f_num', 'f_palive'])
    print attr_names


    data = []
    for uid in user1:
        # set uid
        row = [uid]
        # set attrition states
        u1 = com1.find_one({'id': uid})
        u2 = com2.find_one({'id': uid})
        if u2 is None or u2['timeline_count'] == 0:
            row.extend([None]*2)
        else:
            row.extend([u2['recovery_tweets'], u2['timeline_count']])
        # set users liwc feature
        uatt = iot.get_fields_one_doc(u1, fields)
        row.extend(uatt)
        # set users liwc changes
        uvs = df[df.user_id == str(uid)].loc[:, trimed_fields]
        # print uvs
        if len(uvs) == 2:
            changes, priors, posts = [], [], []
            for name in trimed_fields:
                old = uvs.iloc[0][name]
                new = uvs.iloc[1][name]
                priors.append(old)
                posts.append(new)
                changes.append(new - old)
            row.extend(priors)
            row.extend(posts)
            row.extend(changes)
        else:
            row.extend([None]*(len(trimed_fields)*3))

        # set profile, active days and eigenvector centrality
        row.extend(active_days(u1))
        row.extend([eigen_map.get(u1['id'])])
        row.extend([u1['recovery_tweets'], u1['timeline_count']])

        exist = True
        try:
            v = network1.vs.find(name=str(uid))
        except ValueError:
            exist = False
        if exist:
            # friends = set(network1.neighbors(str(uid))) # id or name
            friends = set(network1.successors(str(uid)))
            if len(friends) > 0:
                friend_ids = [int(network1.vs[vi]['name']) for vi in friends] # return id
                print uid in friend_ids
                print len(friend_ids)
                fatts = []
                alive = 0
                for fid in friend_ids:
                    fu = com1.find_one({'id': fid, 'liwc_anal.result.WC':{'$exists':True}, 'status':{'$exists':True}})
                    fu2 = com2.find_one({'id': fid})
                    if fu != None:
                        fatt = iot.get_fields_one_doc(fu, fields)
                        fatt.extend(active_days(fu))
                        fatt.extend([eigen_map.get(fu['id'])])

                        fatts.append(fatt)
                        if fu2 is None or fu2['timeline_count'] == 0:
                            alive += 0
                        else:
                            alive += 1
                if len(fatts) > 0:
                    fatts = np.array(fatts)
                    fmatts = np.mean(fatts, axis=0)
                    row.extend(fmatts)
                    row.append(len(fatts))
                    paliv = float(alive)/len(fatts)
                    print 'Alive %d %d %.3f' % (alive, len(fatts), paliv)
                    row.append(paliv)
        # print row
        data.append(row)
    df = pd.DataFrame(data, columns=attr_names)
    df.to_csv('data-recover-following.csv', index = False)



def states_change(dbname1, dbname2, comname1, comname2):
    db1 = dbt.db_connect_no_auth(dbname1)
    db2 = dbt.db_connect_no_auth(dbname2)
    com1 = db1[comname1]
    com2 = db2[comname2]
    count = 0
    index = 0
    for user1 in com1.find({'level': 1}):
        index += 1
        user1_ed = profiles_check.check_ed(user1)
        user2 = com2.find_one({'id': user1['id']})
        if user2:
            user2_ed = profiles_check.check_ed(user2)
            if user1_ed != user2_ed:
                print user1['id']
                count += 1
    print count
    print index



if __name__ == '__main__':
    # friend_user_change('fed', 'fed2', 'com', 'com')
    # network1 = gt.load_network('fed', 'snet')
    # friends_old = network1.successors(str('4036631952'))

    # print [network1.vs[v]['name'] for v in friends_old]
    # print friends_old
    # states_change('fed', 'fed2', 'com', 'com')
    # emotion_dropout_IV_split('fed', 'fed2', 'com', 'com')
    emotion_dropout_IV_following('fed', 'fed2', 'com', 'com')
    emotion_recovery_IV_following('fed', 'fed2', 'com', 'com')
