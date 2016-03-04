# -*- coding: utf-8 -*-
"""
Created on 11:19 PM, 3/3/16

@author: tw
"""

import sys
sys.path.append('..')
from api import retweeter
import util.db_util as dbt

dbname = 'rt'
db = dbt.db_connect_no_auth(dbname)
poi = db['ygcom']
poi.create_index("id", unique=True)
#  @taylorswift13 "id": 700890866920067100,
#     "id_str": "700890866920067072",
#     "text": "I'm very happy to say the next single from 1989 will be 'New Romantics'.",
retweeter.get_tweet_retweeters(700890866920067072, poi)
