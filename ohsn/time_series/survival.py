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


def read_user_time():
    com = dbt.db_connect_col('fed', 'scom')
    data = []
    for user in com.find({'liwc_anal.result.WC': {'$exists': True}}, no_cursor_timeout=True):
        if 'status' in user:
            created_at = datetime.strptime(user['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
            scraped_at = user['scrape_timeline_at']
            last_post = datetime.strptime(user['status']['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
            data.append([user['id_str'], created_at, last_post, scraped_at, 'ED'])
    com = dbt.db_connect_col('random', 'scom')
    for user in com.find({'liwc_anal.result.WC': {'$exists': True}}, no_cursor_timeout=True):
        if 'status' in user:
            created_at = datetime.strptime(user['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
            scraped_at = user['scrape_timeline_at']
            last_post = datetime.strptime(user['status']['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
            data.append([user['id_str'], created_at, last_post, scraped_at, 'RD'])

    com = dbt.db_connect_col('younger', 'scom')
    for user in com.find({'liwc_anal.result.WC': {'$exists': True}}, no_cursor_timeout=True):
        if 'status' in user:
            created_at = datetime.strptime(user['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
            scraped_at = user['scrape_timeline_at']
            last_post = datetime.strptime(user['status']['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
            data.append([user['id_str'], created_at, last_post, scraped_at, 'YG'])

    df = pd.DataFrame(data, columns=['uid', 'created_at', 'last_post', 'scraped_at', 'type'])
    df.to_csv('user-key-date.csv')
if __name__ == '__main__':

    read_user_time()

