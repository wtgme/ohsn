# -*- coding: utf-8 -*-
"""
Created on 12:10 AM, 2/7/16

@author: tw
"""

import profiles_preposs
import ed_following_snowball
import ed_follower_snowball
import util.db_util as dbt
import util.twitter_util as twutil
import datetime
import time
import pymongo



def eliminate_non_ed(poidb, netdb):
    for user in poidb.find({'level':1}):
        if not profiles_preposs.check_ed(user):
            poidb.delete_one({'id': user['id']})
            netdb.delete_many({'user': user['id']})
            netdb.delete_many({'follower': user['id']})


