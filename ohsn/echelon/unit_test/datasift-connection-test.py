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

MONGOURL = "ec2-54-228-51-114.eu-west-1.compute.amazonaws.com"
MONGOUSER = "dsUser"
MONGOPWD = urllib.quote_plus('webobservatory')
DBNAME = 'datasift'

COLNAMES = ["twitter_obesity_profile_GW_2015_01",'twitter_obesity_profile_GW_2015_02',"twitter_obesity_profile_GW_2015_03"]

MONGOAUTH = 'mongodb://' + MONGOUSER + ':' + MONGOPWD + '@' + MONGOURL + '/' + DBNAME
# connect to database
print MONGOAUTH

try:
	client = pymongo.MongoClient(MONGOAUTH)
	print MONGOUSER +" connected to " + DBNAME
	db = client[DBNAME]
except Exception, e:
	print MONGOUSER +" FAILED to connect to " + DBNAME
	exit()

print "db connection established"

psoi = []
print "psoi: " + str(len(psoi))

for col in COLNAMES:
	print col
	tweets = db[col]
	print tweets.count()
	for tweet in tweets.find(): 
	try:
		newpoi = dict()
		newpoi['id'] = tweet['interaction']['interaction']['id']
		newpoi['screen_name'] = tweet['interaction']['interaction']['author']['username']
		newpoi['datetime_joined_twitter']  = tweet['interaction']['interaction']['author']['created_at']
		newpoi['poi_classification']  = 0
		newpoi['datetime_last_timeline_scrape']  = datetime.datetime.now()
		newpoi['datetime_last_follower_scrape']  = datetime.datetime.now()
		newpoi['timeline_auth_error_flag']  = False
		newpoi['follower_auth_error_flag']  = False
		psoi.append(newpoi)
        except Exception, e:
            print e              

print psoi[0]
print "total tweets found: " + str(len(posi))
