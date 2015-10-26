# -*- coding: utf-8 -*-
"""
Created on Tue Jun 23 13:19:30 2015

@author: brendan
"""
import pymongo


MONGOURL = 'localhost'
MONGOUSER =  'harold'
DBPASSWD = 'AcKerTalksMaChine'
DBNAME = 'echelon'
MONGOAUTH = 'mongodb://' + MONGOUSER + ':' + DBPASSWD + '@' + MONGOURL + '/' + DBNAME
POI_COL = 'poi'

try:
    conn = pymongo.MongoClient(MONGOAUTH)
    db = conn[DBNAME]
    echelon_poi = db[POI_COL]
    print  MONGOUSER +" connected to " + DBNAME  + "." + POI_COL
except Exception:
    print MONGOUSER +" FAILED to connect to " + DBNAME
    exit()


count= 0    
unique = set()

for person in echelon_poi.find().limit(10):    
    count = count+1
    print person
    try:
        unique.add(person['id'])
    except Exception, e:
        print e              
    
print "checked total: " +str(count)
print "unique found: " + str(len(unique))
