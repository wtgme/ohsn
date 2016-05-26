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


if __name__ == '__main__':
    db = dbt.db_connect_no_auth('depression')
    search = db['search']
    search.create_index([('user.id', pymongo.ASCENDING),
                          ('id', pymongo.DESCENDING)])
    search.create_index([('id', pymongo.ASCENDING)], unique=True)
    search_api.search_query('#MyDepressionLooksLike', search)