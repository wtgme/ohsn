# -*- coding: utf-8 -*-
"""
Created on Tue Jun 23 13:19:30 2015
@author: brendan
"""
import pymongo

# MONGOURL = 'aicvm-bjn1c13-1.ecs.soton.ac.uk'
MONGOURL = 'localhost'
MONGOUSER = 'harold'
DBPASSWD = 'AcKerTalksMaChine'
DBNAME = 'echelon'
MONGOAUTH = 'mongodb://' + MONGOUSER + ':' + DBPASSWD + '@' + MONGOURL + '/' + DBNAME
POI_COL = 'timelines'

try:
    conn = pymongo.MongoClient(MONGOAUTH)
    db = conn[DBNAME]
    tweets = db[POI_COL]
    print  MONGOUSER +" connected to " + DBNAME  + "." + POI_COL
except Exception as detail:
    print detail
    print MONGOUSER +" FAILED to connect to " + DBNAME
    exit()

for tweet in tweets.find().limit(10):    
    print tweet