# -*- coding: utf-8 -*-
"""
Created on 12:10 AM, 2/7/16

@author: tw
"""

import pymongo

from ohsn.api import profiles_check
from ohsn.util import db_util as dbt


def eliminate_non_ed(poidb, netdb):
    for user in poidb.find({'level':1}):
        if not profiles_check.check_ed(user):
            poidb.delete_one({'id': user['id']})
            netdb.delete_many({'user': user['id']})
            netdb.delete_many({'follower': user['id']})


def delete_user(poidb, netdb):
    count = poidb.count()
    for user in poidb.find({'level':3}).limit(count-3380):
        poidb.delete_one({'id': user['id']})
        netdb.delete_many({'user': user['id']})
        netdb.delete_many({'follower': user['id']})


def delete_net(poidb, netdb):
    user_set = set()
    for user in poidb.find():
        user_set.add(user['id'])
    for record in netdb.find():
        if (record['user'] not in user_set) or (record['follower'] not in user_set):
            netdb.delete_one({'_id': record['_id']})


def tran_pro(poidb):
    level1 = poidb.count({'level':1})
    level2 = poidb.count({'level':2})
    allsum = 0.0
    for user in poidb.find({'level':1}):
        allsum += user['followers_count']
        allsum += user['friends_count']
    return level2/allsum


def count_eds(poidb):
    print 'start count'
    count = 0
    for user in poidb.find({}):
        if profiles_check.check_ed(user):
            print user['screen_name']
            count += 1
    print count


def trans(db1, db2):
    db2.create_index("id", unique=True)
    for user in db1.find({}):
        if profiles_check.check_ed(user) == True:
            try:
                db2.insert(user)
            except pymongo.errors.DuplicateKeyError:
                pass


db = dbt.db_connect_no_auth('rd')
ed_poi1 = db['com']
netbd = db['net']
delete_net(ed_poi1, netbd)
# db2 = dbt.db_connect_no_auth('fed')
# ed_poi2 = db2['poi']
# trans(ed_poi1, ed_poi2)
# ed_net = db['net_ed_all']

