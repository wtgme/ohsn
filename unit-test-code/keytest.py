# -*- coding: utf-8 -*-
"""
Created on Sat Jun 13 09:07:17 2015

@author: home
"""

import time
import datetime
import pymongo
import random
import string
import urllib

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

# connect to database

MONGOURL = "aicvm-bjn1c13-1.ecs.soton.ac.uk"
#MONGOURL = "localhost"
MONGOUSER = "harold"
MONGOPWD = urllib.quote_plus('AcKerTalksMaChine')
DBNAME = 'echelon'
COLNAME = 'poi'
#MONGOAUTH = "localhost"
MONGOAUTH = 'mongodb://' + MONGOUSER + ':' + MONGOPWD + '@' + MONGOURL + '/' + DBNAME
print MONGOAUTH

try:
	client = pymongo.MongoClient(MONGOAUTH)
	print MONGOUSER +" connected to " + DBNAME
	db = client[DBNAME]
	poi = db[COLNAME]
except Exception, e:
	print MONGOUSER +" FAILED to connect to " + DBNAME
	exit()

# creating an index doesn;t seem to have scale issues...
# you can do it more than once as well...

poi.create_index([("id", pymongo.DESCENDING)], unique=True)
print "index created"

## Initialize the random seed using the system clock
## (although this is done by default anyway)
random.seed()

# insert into db
for i in range(6000):
    newpoi = dict()
    newpoi['id'] = i
    newpoi['screen_name'] = id_generator()
    newpoi['datetime_joined_twitter']  = datetime.datetime.now()
    newpoi['poi_classification']  = 0
    newpoi['datetime_last_timeline_scrape']  = datetime.datetime.now()
    newpoi['datetime_last_follower_scrape']  = datetime.datetime.now()
    newpoi['timeline_auth_error_flag']  = False
    newpoi['follower_auth_error_flag']  = False
    try:
        poi.insert(newpoi)
        #print "poi " + str(i) + " added."
    except pymongo.errors.DuplicateKeyError, e:
        #print "poi " + str(i) + "already in db!"
        pass
        
# insert into db
for i in range(6000):
    newpoi = dict()
    newpoi['id'] = i
    newpoi['screen_name'] = id_generator()
    newpoi['datetime_joined_twitter']  = datetime.datetime.now()
    newpoi['poi_classification']  = 0
    newpoi['datetime_last_timeline_scrape']  = datetime.datetime.now()
    newpoi['datetime_last_follower_scrape']  = datetime.datetime.now()
    newpoi['timeline_auth_error_flag']  = False
    newpoi['follower_auth_error_flag']  = False
    try:
        poi.insert(newpoi)
        #print "poi " + str(i) + " added."
    except pymongo.errors.DuplicateKeyError, e:
        #print "poi " + str(i) + " already in db!"
        pass

timepre = datetime.datetime.now()
poi.create_index([("id", pymongo.DESCENDING)], unique=True)
timepost = datetime.datetime.now()
delta = timepost -timepre
print "index created"
print delta

print "sleeping"
time.sleep(10)    

for i in range(11):    
    poi.update({'id':i},{'$set':{"datetime_last_timeline_scrape": datetime.datetime.now()}}, upsert=False)
    
poi.update({'id':1},{'$set':{"timeline_auth_error_flag": True}}, upsert=False)
poi.update({'id':2},{'$set':{"poi_classification": 2}}, upsert=False)
poi.update({'id':3},{'$set':{"poi_classification": -1}}, upsert=False)

TIMELINE_POI_CLASS_THRESHOLD = 1

nextpoi = poi.find({'poi_classification': { '$lt': TIMELINE_POI_CLASS_THRESHOLD}}, sort=[('datetime_last_timeline_scrape',1)]).limit( 1 )[0]

print nextpoi



