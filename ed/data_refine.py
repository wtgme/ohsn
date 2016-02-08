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

db = dbt.db_connect_no_auth('ed')

ed_poi = db['poi_ed_all']
ed_net = db['net_ed_all']

def eliminate_non_ed(poidb, netdb):
    for user in poidb.find({'level':1}):
        if not profiles_preposs.check_ed(user):
            poidb.delete_one({'id': user['id']})
            netdb.delete_many({'user': user['id']})
            netdb.delete_many({'follower': user['id']})


def count_eds(poidb):
    print 'start count'
    count = 0
    for user in poidb.find({}):
        if profiles_preposs.check_ed(user):
            print user['screen_name']
            count += 1
    print count

count_eds(ed_poi)
