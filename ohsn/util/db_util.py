# -*- coding: utf-8 -*-
"""
Created on 20:34, 26/10/15

@author: wt
"""
import pymongo
import ConfigParser
import os
import datetime

def db_connect_auth(DBNAME):
    config = ConfigParser.ConfigParser()
    config.read(
        os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)), 'conf', 'Mongodb.cfg'))
    MONGOURL = config.get('host', 'url')
    PORT = '27017'
    MONGOUSER = config.get('user', 'name')
    DBPASSWD = config.get('user', 'psw')
    MONGOAUTH = 'mongodb://' + MONGOUSER + ':' + DBPASSWD + '@' + MONGOURL + ':' + PORT + '/' + DBNAME
    try:
        conn = pymongo.MongoClient(MONGOAUTH)
        db = conn[DBNAME]
        print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + MONGOUSER + " connected to " + DBNAME
        return db
    except Exception as detail:
        print detail
        print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + MONGOUSER + " FAILED to connect to " + DBNAME
        exit()


def db_connect_no_auth(DBNAME):
    config = ConfigParser.ConfigParser()
    config.read(
        os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)), 'conf', 'Mongodb.cfg'))
    MONGOURL = config.get('host', 'url')
    PORT = '27017'
    MONGOAUTH = 'mongodb://' + MONGOURL + ':' + PORT + '/' + DBNAME

    try:
        conn = pymongo.MongoClient(MONGOAUTH)
        db = conn[DBNAME]
        # print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + "Success connected to " + DBNAME
        return db
    except Exception as detail:
        print detail
        print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + "FAILED to connect to " + DBNAME
        exit()


def db_connect_col(dbname, colname):
    db = db_connect_no_auth(dbname)
    return db[colname]


''' testing collection'''
# collection = DBConnect('echelon', 'timelines')
# for tweet in collection.find().limit(10):
#     print tweet
# collection = DBConnectNOAuth('twitter_test', 'streamtrack')

if __name__ == '__main__':
    db = db_connect_no_auth('fed')
    net = db['com']
    print net.count({'net_anal.tnmined': {'$exists': False},'net_anal.tnmined': False})
    # print net.count({'net_anal.tnmined': {'$exists': False}})
    # print net.count({'net_anal.tnmined': False})
    print net.count({'$and': [{'net_anal.tnmined': {'$exists': False}},
                                            {'net_anal.tnmined': False}]})
    # print net.count({'$or': [{'net_anal.tnmined': {'$exists': False}},
    #                                         {'net_anal.tnmined': False}]})

    # com = db['scom']
    # ulist = []
    # for user in com.find({'timeline_count': {'$gt': 0}}):
    #     ulist.append(user['id'])
    # print len(ulist)
    # print net.count({'$and': [{'type': {'$in': [1]}}, {'id0': {'$in': ulist}}]})
    # print net.count({'type': {'$in': [1]}, 'id0': {'$in': ulist}})
