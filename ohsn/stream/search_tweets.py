# -*- coding: utf-8 -*-
"""
Created on 12:31 PM, 5/26/16

@author: tw
"""

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
import ohsn.util.db_util as dbt
import ohsn.api.search as search_api
import pymongo
import time


if __name__ == '__main__':
    db = dbt.db_connect_no_auth('depression')
    search = db['search']
    search.create_index([('user.id', pymongo.ASCENDING),
                          ('id', pymongo.DESCENDING)])
    search.create_index([('id', pymongo.ASCENDING)], unique=True)
    while True:
        count1 = search.count()
        search_api.search_query('#MyDepressionLooksLike', search)
        count2 = search.count()
        if count2 >= count1:
            time.sleep(60*60*12)
            continue
        else:
            break
