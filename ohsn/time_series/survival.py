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

def diff_month(d1, d2):
    return (d1.year - d2.year)*12 + d1.month - d2.month


def read_user_time():
    com = dbt.db_connect_col('fed', 'scom')
    fields = iot.read_fields()
    trimed_fields = [field.split('.')[-1] for field in fields]


    data = []

    for user in com.find({'liwc_anal.result.WC': {'$exists': True}}, no_cursor_timeout=True):
        if 'status' in user:
            created_at = datetime.strptime(user['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
            scraped_at = user['scrape_timeline_at']
            last_post = datetime.strptime(user['status']['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
            if diff_month(scraped_at, last_post) > 2:
                death = 1
            else:
                death = 0
            values = iot.get_fields_one_doc(user, fields)
            data.append([user['id_str'], created_at, last_post, scraped_at, 'ED', death].extend(values))

    com = dbt.db_connect_col('random', 'scom')
    for user in com.find({'liwc_anal.result.WC': {'$exists': True}}, no_cursor_timeout=True):
        if 'status' in user:
            created_at = datetime.strptime(user['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
            scraped_at = user['scrape_timeline_at']
            last_post = datetime.strptime(user['status']['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
            if diff_month(scraped_at, last_post) > 2:
                death = 1
            else:
                death = 0
            values = iot.get_fields_one_doc(user, fields)
            data.append([user['id_str'], created_at, last_post, scraped_at, 'RD', death].extend(values))

    com = dbt.db_connect_col('younger', 'scom')
    for user in com.find({'liwc_anal.result.WC': {'$exists': True}}, no_cursor_timeout=True):
        if 'status' in user:
            created_at = datetime.strptime(user['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
            scraped_at = user['scrape_timeline_at']
            last_post = datetime.strptime(user['status']['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
            if diff_month(scraped_at, last_post) > 2:
                death = 1
            else:
                death = 0
            values = iot.get_fields_one_doc(user, fields)
            data.append([user['id_str'], created_at, last_post, scraped_at, 'YG', death].extend(values))

    df = pd.DataFrame(data, columns=['uid', 'created_at', 'last_post', 'scraped_at', 'group', 'death'].extend(trimed_fields))
    df.to_csv('user-durations.csv')

if __name__ == '__main__':

    read_user_time()
    # print diff_month(datetime(2010, 10,1), datetime(2010,9,1))