# -*- coding: utf-8 -*-
"""
Created on 12:10 AM, 2/7/16

@author: tw
"""

import profiles_preposs
import util.db_util as dbt
# import util.twitter_util as twutil
import datetime
import time
import pymongo



def eliminate_non_ed(poidb, netdb):
    for user in poidb.find({'level':1}):
        if not profiles_preposs.check_ed(user):
            poidb.delete_one({'id': user['id']})
            netdb.delete_many({'user': user['id']})
            netdb.delete_many({'follower': user['id']})


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
        if profiles_preposs.check_ed(user):
            print user['screen_name']
            count += 1
    print count


def trans(db1, db2):
    db2.create_index("id", unique=True)
    for user in db1.find({}):
        if profiles_preposs.check_ed(user) == True:
            try:
                db2.insert(user)
            except pymongo.errors.DuplicateKeyError:
                pass


db = dbt.db_connect_no_auth('ed')
ed_poi1 = db['poi_ed']
print tran_pro(ed_poi1)
# db2 = dbt.db_connect_no_auth('fed')
# ed_poi2 = db2['poi']
# trans(ed_poi1, ed_poi2)
# ed_net = db['net_ed_all']

