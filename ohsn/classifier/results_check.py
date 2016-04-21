# -*- coding: utf-8 -*-
"""
Created on 1:35 PM, 3/8/16

@author: tw
"""

from ohsn.util import db_util as dbt
import pickle
import numpy as np


def check():
    rdb = dbt.db_connect_no_auth('fed')
    # ydb = dbt.db_connect_no_auth('young')
    rcol = rdb['com']
    # ycol = ydb['com']

    test_ids = pickle.load(open('data/test_id_class.pick', 'r'))
    test_ids1 = pickle.load(open('data/test_id_reg.pick', 'r'))
    print np.array_equal(test_ids, test_ids1)
    test_class = pickle.load(open('data/test_class.pick', 'r'))
    test_class[test_class < 0] = 0
    test_class = test_class.astype(bool)
    targest_ids = test_ids[test_class]
    print targest_ids.shape
    for uid in targest_ids:
        print (uid)
        user = rcol.find_one({'id': uid}, ['screen_name'])
        # if user is None:
        #     user = ycol.find_one({'id': uid}, ['screen_name'])
        print user['screen_name']

# check()

a = 696189699430289409
print a
# b = float(a)
# print b
# print nstr(mpf(b), 50)

# print int(696189699430289409)
#
# a = np.array([6.9618969943e+17], dtype='int64')
# print a