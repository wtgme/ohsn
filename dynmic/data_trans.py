# -*- coding: utf-8 -*-
"""
Created on 9:18 PM, 2/25/16
finanlize data of ED, RD, YG for dynamic monitor

@author: tw
"""

import sys
sys.path.append('..')
import util.db_util as dbt

def transform():
    db = dbt.db_connect_no_auth('yg')
    cols = db['com']
    db = dbt.db_connect_no_auth('dyg')
    cold = db['com']
    for user in cols.find({}, ['id', 'screen_name']):
        cold.insert({'id': user['id'], 'screen_name':user['screen_name']})


def get_users(dbname):
    user_set = set()
    db = dbt.db_connect_no_auth(dbname)
    cols = db['com']
    for user in cols.find({}, ['id']):
        user_set.add(user['id'])
    return user_set


def test_common():
    # eds, rds, ygs = get_users('ded'), get_users('drd'), get_users('dyg')
    rds, ygs = get_users('rd'), get_users('yg')
    # print eds.intersection(rds)
    # print eds.intersection(ygs)
    print ygs.intersection(rds)


def test_timline():
    db = dbt.db_connect_no_auth('yg')
    cols = db['com']
    for user in cols.find({'timeline_count': 0}, ['id', 'timeline_count', 'statuses_count']):
        # print user
        if user['statuses_count']-user['timeline_count']>100:
            print user['id']
            # cols.update({'id': user['id']}, {'$set':{"timeline_count": 0,
            #                                                  'timeline_scraped_times': 0}},
            #                        upsert=False)

test_common()

