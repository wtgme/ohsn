# -*- coding: utf-8 -*-
"""
Created on 09:40, 11/02/16

@author: wt

verify all users in ED have been added in com db
"""

import sys
sys.path.append('..')
import util.db_util as dbt
import pymongo
import datetime
import time

db = dbt.db_connect_no_auth('fed')
com = db['com']
poi = db['poi']
time = db['timeline']

print time.count()

# count_none, count_hl = 0, 0
# for up in poi.find({}, ['id', 'screen_name']):
#     uid = up['id']
#     user = com.find_one({'id': uid})
#     if user == None:
#         count_none += 1
#         print 'none user', up['screen_name']
#     else:
#         if user['level']!=1:
#             count_hl += 1
#             print 'high level user', up['screen_name']
# print count_none, count_hl