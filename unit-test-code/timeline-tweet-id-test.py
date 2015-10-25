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

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

# connect to database

# Choose a connection method:
# for local use this: 
conn = pymongo.MongoClient()
# for remote use this:
# conn = MongoClient(MONGOURL)

db = conn['keytest']
poi = db['poi']

# creating an index doesn;t seem to have scale issues...
# you can do it more than once as well...

timepre = datetime.datetime.now()
poi.create_index([("id", pymongo.DESCENDING)], unique=True)
timepost = datetime.datetime.now()
delta = timepost -timepre
print "index created"
print delta

timepre = datetime.datetime.now()
poi.create_index([("id", pymongo.DESCENDING)], unique=True)
timepost = datetime.datetime.now()
delta = timepost -timepre
print "index created"
print delta

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
