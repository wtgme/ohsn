# -*- coding: utf-8 -*-
"""
Created on 10:09, 08/11/16

@author: wt
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
    ts = datetime.strptime(user['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
    tts = datetime.strptime(user['status']['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
    delta = tts.date() - ts.date()
    days = delta.days+1
    return days

def emotion_dropout_IV(dbname1, dbname2, comname1, comname2):
    filter_que = {'level': 1, 'liwc_anal.result.WC':{'$exists':True}}
    user1 = iot.get_values_one_field(dbname1, comname1, 'id', filter_que)
    com1 = dbt.db_connect_col(dbname1, comname1)
    com2 = dbt.db_connect_col(dbname2, comname2)
    fields = ['liwc_anal.result.posemo',
              'liwc_anal.result.negemo',
              'liwc_anal.result.anx',
              'liwc_anal.result.anger',
              'liwc_anal.result.sad',
              'engage.friend_count',
              'engage.status_count',
              'engage.follower_count',
              'engage.friends_day',
              'engage.statuses_day',
              'engage.followers_day']
    network1 = gt.load_network(dbname1, 'net')
    # network2 = gt.load_network(dbname2, 'net')
    for uid in user1:
        row = []
        u1 = com1.find_one({'id': uid})
        u2 = com2.find_one({'id': uid})
        if u2 is None or u2['timeline_count'] == 0:
            row.append(0)
        else:
            row.append(1)
        uatt = iot.get_fields_one_doc(u1, fields)
        row.append(att for att in uatt)
        exist = True
        try:
            v = network1.vs.find(name=str(uid))
        except ValueError:
            exist = False
        if exist:
            friends_old = network1.successors(str(uid))


    for field in fields:
        print '-----------------%s----------------' %field
        user_changes, friends_changes = [], []
        for uid in user1:
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
    states_change('fed', 'fed2', 'com', 'com')
