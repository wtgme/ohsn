# -*- coding: utf-8 -*-
"""
Created on 9:18 PM, 2/25/16
finanlize data of ED, RD, YG for dynamic monitor

@author: tw
"""

import sys
sys.path.append('..')
import util.db_util as dbt

db = dbt.db_connect_no_auth('yg')
cols = db['com']
db = dbt.db_connect_no_auth('dyg')
cold = db['com']
for user in cols.find({}, ['id', 'screen_name']):
    cold.insert({'id': user['id'], 'screen_name':user['screen_name']})


