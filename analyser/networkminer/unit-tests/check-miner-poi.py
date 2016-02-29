# -*- coding: utf-8 -*-
"""
Created on Fri Jun 19 18:17:27 2015

@author: brendan
"""

#import datetime
import pymongo
import urllib

# POI_THRESHOLD = 0


# Echelon connection    

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
 

print str(echelon_poi.count())  + " POI in echelon poi database"

print str(echelon_poi.find({ 'text_anal.gw': { '$exists': True} }).count()) + " POI have gw"

print str(echelon_poi.find({ 'text_anal.cw': { '$exists': True} }).count()) + " POI have cw"

print str(echelon_poi.find({ 'text_anal.a': { '$exists': True} }).count()) + " POI have age"

print str(echelon_poi.find({ 'text_anal.h': { '$exists': True} }).count()) + " POI have height"

print str(echelon_poi.find({ 'text_anal.edword_count.value': { '$exists': True, '$gte': 1} }).count()) + " POI have ed word count > 1"

print str(echelon_poi.find({ 'lang':{'$in':['en','en-gb']}}).count()) + " POI have lang = en or en-gb"

print str(echelon_poi.find({ 'ds_gender':{'$in':['male','female']}}).count()) + " POI have gender = male/female"

print str(echelon_poi.find({ 'location':{ '$ne': None } }).count()) + " POI have location data"

print str(echelon_poi.find({ 'coordinates.datetime':{ '$ne': None } }).count()) + " POI have coordinate data"

for person in echelon_poi.find({ 'text_anal.edword_count.value': { '$exists': True, '$gte': 3} }).limit(3):
	print person['id']

print str(echelon_poi.find({'timeline_auth_error_flag':False, "net_anal.mrrmined": False}).count()) + " POI have timeline auth error false and netmined = false"
print str(echelon_poi.find({'timeline_auth_error_flag':False, "net_anal.mrrmined": True}).count()) + " POI have timeline auth error false and netmined = true"


