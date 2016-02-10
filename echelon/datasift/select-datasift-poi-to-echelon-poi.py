# -*- coding: utf-8 -*-
"""
Created on Fri Jun 19 18:17:27 2015

@author: brendan
"""

#import datetime
import pymongo
import urllib

# POI_THRESHOLD = 0

DATASIFTMONGOURL = "localhost"
DATASIFTMONGOUSER = "dsUser"
DATASIFTMONGOPWD = urllib.quote_plus('SiftLittleMentsals')
DATASIFTDBNAME = 'datasift'

DATASIFT_PROCESSED_COLNAME = "datasift_poi"
# DATASIFTCOLNAMES = ["twitter_obesity_profile_GW_2015_01",'twitter_obesity_profile_GW_2015_02',"twitter_obesity_profile_GW_2015_03"]
# DATASIFTCOLNAMES = ["twitter_obesity_profile_GW_2015_01"]

DATASIFTMONGOAUTH = 'mongodb://' + DATASIFTMONGOUSER + ':' + DATASIFTMONGOPWD + '@' + DATASIFTMONGOURL + '/' + DATASIFTDBNAME
# connect to database
#print DATASIFTMONGOAUTH

try:
    dsclient = pymongo.MongoClient(DATASIFTMONGOAUTH)
    print DATASIFTMONGOUSER +" connected to " + DATASIFTDBNAME
    dsdb = dsclient[DATASIFTDBNAME]
    processed = dsdb[DATASIFT_PROCESSED_COLNAME]
except Exception:
    print DATASIFTMONGOUSER +" FAILED to connect to " + DATASIFTDBNAME
    exit()
    
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
    echelon_poi.create_index([("id", pymongo.DESCENDING)], unique=True)
    print "index created on " + POI_COL + " by id"        
except Exception:
    print MONGOUSER +" FAILED to connect to " + DBNAME
    exit()
 

#for person in processed.find():
#    try:
#        print person
#        print "\n"
#    except:
#        pass

print str(processed.count())  + " POI in datasift poi database"

print str(processed.find({ 'text_anal.gw': { '$exists': True} }).count()) + " POI have gw"

print str(processed.find({ 'text_anal.cw': { '$exists': True} }).count()) + " POI have cw"

print str(processed.find({ 'text_anal.a': { '$exists': True} }).count()) + " POI have age"

print str(processed.find({ 'text_anal.h': { '$exists': True} }).count()) + " POI have height"

print str(processed.find({ 'text_anal.edword_count.value': { '$exists': True, '$gte': 1} }).count()) + " POI have ed word count > 1"

# move the interesting ones to the echelon poi

for person in processed.find({ 'text_anal.gw': { '$exists': True} }):
    try:
        echelon_poi.insert(person)
    except pymongo.errors.DuplicateKeyError:
        print "Duplicate POI"

for person in processed.find({ 'text_anal.cw': { '$exists': True} }):
    try:
        echelon_poi.insert(person)
    except pymongo.errors.DuplicateKeyError:
        print "Duplicate POI"
        
for person in processed.find({ 'text_anal.edword_count.value': { '$exists': True, '$gte': 1} }):
    try:
        echelon_poi.insert(person)
    except pymongo.errors.DuplicateKeyError:
        print "Duplicate POI"


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

