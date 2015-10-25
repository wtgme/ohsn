# -*- coding: utf-8 -*-
"""
Created on Sat Jun 13 09:07:17 2015

@author: home
"""

import datetime
import pymongo
import random
import string
import urllib

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


MONGOURL = "aicvm-bjn1c13-1.ecs.soton.ac.uk"
#MONGOURL = "localhost"
MONGOUSER = "harold"
MONGOPWD = urllib.quote_plus('AcKerTalksMaChine')
DBNAME = 'echelon'
COLNAME = 'poi'
#MONGOAUTH = "localhost"
MONGOAUTH = 'mongodb://' + MONGOUSER + ':' + MONGOPWD + '@' + MONGOURL + '/' + DBNAME

# connect to database
print MONGOAUTH


try:
	client = pymongo.MongoClient(MONGOAUTH)
	print MONGOUSER +" connected to " + DBNAME
	db = client[DBNAME]
	poi = db[COLNAME]
except Exception, e:
	print MONGOUSER +" FAILED to connect to " + DBNAME
	exit()

print "db connection established"

poi.create_index([("id", pymongo.DESCENDING)], unique=True)
print "index created"

psoi = []

for i in range(50):
    newpoi = dict()
    newpoi['id'] = i
    newpoi['screen_name'] = id_generator()
    newpoi['datetime_joined_twitter']  = datetime.datetime.now()
    newpoi['poi_classification']  = 0
    newpoi['datetime_last_timeline_scrape']  = datetime.datetime.now()
    newpoi['datetime_last_follower_scrape']  = datetime.datetime.now()
    newpoi['timeline_auth_error_flag']  = False
    newpoi['follower_auth_error_flag']  = False
    psoi.append(newpoi)

for i in range(50):
    newpoi = dict()
    newpoi['id'] = i
    newpoi['screen_name'] = id_generator()
    newpoi['datetime_joined_twitter']  = datetime.datetime.now()
    newpoi['poi_classification']  = 0
    newpoi['datetime_last_timeline_scrape']  = datetime.datetime.now()
    newpoi['datetime_last_follower_scrape']  = datetime.datetime.now()
    newpoi['timeline_auth_error_flag']  = False
    newpoi['follower_auth_error_flag']  = False
    psoi.append(newpoi)

# insert into poi db
for anewpoi in psoi:
    try:
        poi.insert(anewpoi)
        print "poi " + str(i) + " added."
    except pymongo.errors.DuplicateKeyError, e:
        print "poi " + str(i) + "already in db!"
        pass

print "ECHELON will download and monitor " + str(poi.count()) + " twitter users"
