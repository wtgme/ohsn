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


db = dbt.db_connect_no_auth('fed')
com = db['com']
count = 0
i = 0
for user in com.find({}, ['id', 'description']):
    # print i
    if profiles_check.check_ed_profile(user['description']):
        print user['id'], ' '.join(user['description'].split()).encode('utf-8')
        count += 1
    i += 1
print count


