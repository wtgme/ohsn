# -*- coding: utf-8 -*-
"""
Created on 17:08, 07/03/16

@author: wt
"""
from os import path
import sys
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
import util.db_util as dbutil

db = dbutil.db_connect_no_auth('fed')
bio = db['bio']
com = db['com']
for bior in bio.find():
    sn = bior.get('screen_name', None)
    if sn is None:
        user = com.find_one({'id': bior['uid']})
        bio.update({"uid": bior['uid']}, {'$set': {'screen_name': user['screen_name']}}, upsert=False)
