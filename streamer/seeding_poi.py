# -*- coding: utf-8 -*-
"""
Created on 10:54, 24/11/15

1. Choose 100 random users from user collections (where include users in stream data)

@author: wt
"""

import sys
sys.path.append('..')
import util.db_util as dbt
import datetime
import random

# Connect to db
db = dbt.db_connect_no_auth('stream')
sample_user = db['user_sample']
track_user = db['user_track']

sample_seed = db['seed_sample']
sample_seed.create_index('id', unique=True)
track_seed = db['seed_track']
track_seed.create_index('id', unique=True)


def trans_user_2_seed(user_db, seed_db):
    seed_db.remove({})
    target_user_list = user_db.find({'geo_enabled': True,
                                    'protected': False,
                                    'verified': False,
                                    'status.created_at': {'$gte': datetime.date(2015, 10, 15).isoformat()}
                                    # 'statuses_count':{},
                                    })
    count = user_db.count({'geo_enabled': True,
                        'protected': False,
                        'verified': False,
                        'status.created_at': {'$gte': datetime.date(2015, 10, 15).isoformat()}
                        # 'statuses_count':{},
                        })
    print 'Satisfied user number', count
    rate = count/100.0
    num = 0
    index = 0
    while True:
        for user in target_user_list:
            index += 1
            if num < 100:
                rand = random.uniform(0, rate)
                # print rand
                if rand < 1:
                    seed_db.insert(user)
                    num += 1
                    print 'The seed', num, 'from', index
            else:
                return

trans_user_2_seed(sample_user, sample_seed)
trans_user_2_seed(track_user, track_seed)