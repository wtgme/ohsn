# -*- coding: utf-8 -*-
"""
Created on 16:12, 09/10/17

@author: wt

This script stats the activity of core ED users
"""


import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))


import ohsn.util.db_util as dbt
import ohsn.util.io_util as iot
import pymongo

def check_dumplice(dbname, timename, timename2):
    # add time1 into time2
    time1 = dbt.db_connect_col(dbname, timename)
    times = dbt.db_connect_col(dbname, timename2)
    for tweet in time1.find({}):
        try:
            times.insert(tweet)
        except pymongo.errors.DuplicateKeyError:
            pass

if __name__ == '__main__':
    check_dumplice('ded', 'timeline1', 'timeline')