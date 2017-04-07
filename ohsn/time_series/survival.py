# -*- coding: utf-8 -*-
"""
Created on 14:45, 04/04/17

@author: wt
"""

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import pymongo
from ohsn.util import db_util as dbt
from datetime import datetime
import numpy as np
import pandas as pd
import ohsn.util.io_util as iot
from lifelines.utils import datetimes_to_durations

def diff_month(d1, d2):
    return (d1.year - d2.year)*12 + d1.month - d2.month


def diff_day(d2, d1):
    delta = d2 - d1
    return delta.days

def read_user_time():
    fields = iot.read_fields()
    trimed_fields = [field.split('.')[-1] for field in fields]
    data = []

    com = dbt.db_connect_col('fed', 'scom')
    for user in com.find({'liwc_anal.result.WC': {'$exists': True}}, no_cursor_timeout=True):
        if 'status' in user:
            created_at = datetime.strptime(user['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
            scraped_at = user['scrape_timeline_at']
            last_post = datetime.strptime(user['status']['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
            life_time = diff_day(last_post, created_at)
            average_time = float(life_time)/min(1, user['statuses_count'])
            if (diff_day(scraped_at, last_post)-average_time) > 60:
                death = 1
            else:
                death = 0
            values = iot.get_fields_one_doc(user, fields)
            data.append([user['id_str'], created_at, last_post, scraped_at, 'ED', death]+values)

    com = dbt.db_connect_col('random', 'scom')
    for user in com.find({'liwc_anal.result.WC': {'$exists': True}}, no_cursor_timeout=True):
        if 'status' in user:
            created_at = datetime.strptime(user['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
            scraped_at = user['scrape_timeline_at']
            last_post = datetime.strptime(user['status']['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
            life_time = diff_day(last_post, created_at)
            average_time = float(life_time)/min(1, user['statuses_count'])
            if (diff_day(scraped_at, last_post)-average_time) > 60:
                death = 1
            else:
                death = 0
            values = iot.get_fields_one_doc(user, fields)
            data.append([user['id_str'], created_at, last_post, scraped_at, 'RD', death]+values)

    com = dbt.db_connect_col('younger', 'scom')
    for user in com.find({'liwc_anal.result.WC': {'$exists': True}}, no_cursor_timeout=True):
        if 'status' in user:
            created_at = datetime.strptime(user['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
            scraped_at = user['scrape_timeline_at']
            last_post = datetime.strptime(user['status']['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
            life_time = diff_day(last_post, created_at)
            average_time = float(life_time)/min(1, user['statuses_count'])
            if (diff_day(scraped_at, last_post)-average_time) > 60:
                death = 1
            else:
                death = 0
            values = iot.get_fields_one_doc(user, fields)
            data.append([user['id_str'], created_at, last_post, scraped_at, 'YG', death]+values)

    df = pd.DataFrame(data, columns=['uid', 'created_at', 'last_post', 'scraped_at', 'group', 'event']+trimed_fields)
    df.to_csv('user-durations.csv')



if __name__ == '__main__':

    read_user_time()
    # print diff_month(datetime(2010, 10,1), datetime(2010,9,1))
    # from lifelines.utils import k_fold_cross_validation

