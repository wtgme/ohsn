# -*- coding: utf-8 -*-
"""
Created on Tue Jun 23 13:19:30 2015

@author: brendan
"""
import pymongo

MONGOURL = 'localhost'
MONGOUSER = 'harold'
DBPASSWD = 'AcKerTalksMaChine'
DBNAME = 'echelon'
MONGOAUTH = 'mongodb://' + MONGOUSER + ':' + DBPASSWD + '@' + MONGOURL + '/' + DBNAME
POI_COL = 'edges'

try:
    conn = pymongo.MongoClient(MONGOAUTH)
    db = conn[DBNAME]
    edges = db[POI_COL]
    print  MONGOUSER + " connected to " + DBNAME + "." + POI_COL
except Exception:
    print MONGOUSER + " FAILED to connect to " + DBNAME
    exit()

for edge in edges.find().limit(10):
    print edge
