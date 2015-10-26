# -*- coding: utf-8 -*-
"""
Created on 20:34, 26/10/15

@author: wt
"""

import pymongo
import ConfigParser
import os

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
        print MONGOUSER + " connected to " + DBNAME
        return db
    except Exception as detail:
        print detail
        print MONGOUSER + " FAILED to connect to " + DBNAME
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
        print "Success connected to " + DBNAME
        return db
    except Exception as detail:
        print detail
        print "FAILED to connect to " + DBNAME
        exit()


''' testing collection'''
# collection = DBConnect('echelon', 'timelines')
# for tweet in collection.find().limit(10):
#     print tweet
# collection = DBConnectNOAuth('twitter_test', 'streamtrack')
