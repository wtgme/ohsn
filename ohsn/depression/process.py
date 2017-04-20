# -*- coding: utf-8 -*-
"""
Created on 14:33, 20/04/17

@author: wt
"""

import json
import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
import pymongo
import ohsn.util.db_util as dbt
from os import listdir
from os.path import isfile, join
import ast


def store_users_profile():
    com = dbt.db_connect_col('depression', 'neg_com')
    com.create_index("id", unique=True)

    with open('/home/wt/Code/ohsn/ohsn/depression/data/negative/user_profile/written_users_info_detail_list.txt') as data_file:
        for line in data_file.readlines():
            print line
            parsed_json = ast.literal_eval(line.strip())
            try:
                com.insert(parsed_json)
            except pymongo.errors.DuplicateKeyError:
                    pass

def store_tweets():
    times = dbt.db_connect_col('depression', 'neg_timeline')
    times.create_index([('user.id', pymongo.ASCENDING),
                              ('id', pymongo.DESCENDING)])
    times.create_index([('id', pymongo.ASCENDING)], unique=True)

    mypath = '/home/wt/Code/ohsn/ohsn/depression/data/negative/user_tweets'
    onlyfiles = [mypath+'/'+f for f in listdir(mypath) if isfile(join(mypath, f))]
    for file_path in onlyfiles:
        with open(file_path) as data_file:
            print file_path
            for line in data_file.readlines():
                parsed_json = ast.literal_eval(line.strip())
                try:
                    times.insert(parsed_json)
                except pymongo.errors.DuplicateKeyError:
                    pass


if __name__ == '__main__':
    # store_users_profile()
    store_tweets()