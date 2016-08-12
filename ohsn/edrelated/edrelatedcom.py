# -*- coding: utf-8 -*-
"""
Created on 15:48, 09/08/16

@author: wt
"""
import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import ohsn.util.db_util as dbt
from ohsn.api import profiles_check
import ohsn.util.graph_util as gt
import pickle


def rec_user(dbname, colname):
    user_lit = []
    db = dbt.db_connect_no_auth(dbname)
    com = db[colname]
    count = 0
    i = 0
    for user in com.find({}, ['id', 'description']):
        if 'recover' in (user['description'].strip().lower().replace("-", "").replace('_', '')):
            # print user['id'], ' '.join(user['description'].split()).encode('utf-8')
            user_lit.append(user['id'])
            count += 1
        i += 1
    print count
    return user_lit


def ed_user(dbname, colname):
    user_lit = []
    db = dbt.db_connect_no_auth(dbname)
    com = db[colname]
    count = 0
    i = 0
    for user in com.find({}, ['id', 'description']):
        if profiles_check.check_ed_related_profile(user['description']):
            # print user['id'], ' '.join(user['description'].split()).encode('utf-8')
            user_lit.append(user['id'])
            count += 1
        i += 1
    print count
    return user_lit


def network(dbname, colname):
    # ed_usersd = ed_user(dbname, colname)
    # pickle.dump(ed_usersd, open('data/ed_users.pick', 'w'))
    ed_usersd = pickle.load(open('data/ed_users.pick', 'r'))

    # rec_usersd = rec_user(dbname, colname)
    # pickle.dump(rec_usersd, open('data/rec_users.pick', 'w'))
    rec_usersd = pickle.load(open('data/rec_users.pick', 'r'))

    inlist = list(set(ed_usersd).union(set(rec_usersd)))
    print len(inlist)
    g = gt.load_network_subset(inlist, dbname, colname)
    g.vs['rec'] = 0
    for uid in rec_usersd:
        exist = True
        try:
            v = g.vs.find(name=str(uid))
        except ValueError:
            exist = False
        if exist:
            v['rec'] = 1
    g.write_dot('data/rec_friendship.DOT')



if __name__ == '__main__':
    # ed_users = ed_user('fed', 'com')
    # rec_users = rec_user('fed', 'com')
    # print len(set(ed_users).intersection(rec_users))
    network('fed', 'com')

