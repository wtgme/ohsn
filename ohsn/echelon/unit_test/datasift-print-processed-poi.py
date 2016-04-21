# -*- coding: utf-8 -*-
"""
Created on Fri Jun 19 18:17:27 2015

@author: brendan
"""

# -*- coding: utf-8 -*-
"""
Created on Sat Jun 13 09:07:17 2015
@author: home
"""

#import datetime
import pymongo
import urllib

# POI_THRESHOLD = 0

# Echelon connection    

MONGOURL = 'aicvm-bjn1c13-1'
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


#for tweet in processed.find( {'qty': { '$exists': True, '$nin': [ 5, 15 ] } } ):
#    print tweet
#    print "\n"

for person in echelon_poi.find():
    try:
        print person
        print "\n"
    except:
        pass

print str(echelon_poi.count())  + " POI in echelon poi database"

print str(echelon_poi.find({ 'text_anal.gw': { '$exists': True} }).count()) + " POI have gw"

print str(echelon_poi.find({ 'text_anal.cw': { '$exists': True} }).count()) + " POI have cw"

print str(echelon_poi.find({ 'text_anal.a': { '$exists': True} }).count()) + " POI have age"

print str(echelon_poi.find({ 'text_anal.h': { '$exists': True} }).count()) + " POI have height"

print str(echelon_poi.find({ 'text_anal.edword_count.value': { '$exists': True, '$gte': 1} }).count()) + " POI have ed word count > 1"