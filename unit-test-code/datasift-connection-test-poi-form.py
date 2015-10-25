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

DATASIFTMONGOURL = "ec2-54-228-51-114.eu-west-1.compute.amazonaws.com"
DATASIFTMONGOUSER = "dsUser"
DATASIFTMONGOPWD = urllib.quote_plus('webobservatory')
DATASIFTDBNAME = 'datasift'

DATASIFTCOLNAMES = ["twitter_obesity_profile_GW_2015_01",'twitter_obesity_profile_GW_2015_02',"twitter_obesity_profile_GW_2015_03"]
# COLNAMES = ["twitter_obesity_profile_GW_2015_01"]

DATASIFTMONGOAUTH = 'mongodb://' + DATASIFTMONGOUSER + ':' + DATASIFTMONGOPWD + '@' + DATASIFTMONGOURL + '/' + DATASIFTDBNAME
# connect to database
print DATASIFTMONGOAUTH

try:
	dsclient = pymongo.MongoClient(DATASIFTMONGOAUTH)
	print DATASIFTMONGOUSER +" connected to " + DATASIFTDBNAME
	dsdb = dsclient[DATASIFTDBNAME]
except Exception, e:
	print DATASIFTMONGOUSER +" FAILED to connect to " + DATASIFTDBNAME
	exit()

print "DATASIFT db connection established"

ECHELONMONGOURL = "aicvm-bjn1c13-1.ecs.soton.ac.uk"
#ECHELONMONGOURL = "localhost"
ECHELONMONGOUSER = "harold"
ECHELONMONGOPWD = urllib.quote_plus('AcKerTalksMaChine')
ECHELONDBNAME = 'echelon'
ECHELONCOLNAME = 'poi'
#MONGOAUTH = "localhost"
ECHELONMONGOAUTH = 'mongodb://' + ECHELONMONGOUSER + ':' + ECHELONMONGOPWD + '@' + ECHELONMONGOURL + '/' + ECHELONDBNAME

# connect to database
print ECHELONMONGOAUTH

try:
	ecclient = pymongo.MongoClient(ECHELONMONGOAUTH)
	print MONGOUSER +" connected to " + DBNAME
	ecdb = ecclient[DBNAME]
	poi = ecdb[COLNAME]
except Exception, e:
	print MONGOUSER +" FAILED to connect to " + DBNAME
	exit()

print "ECHELON db connection established"

poi.create_index([("id", pymongo.DESCENDING)], unique=True)
print "poi index created on id parameter"

for col in COLNAMES:
	dstweets = db[col]
	print "Found " + str(dstweets.count()) + " tweets in " + col
	for tweet in dstweets.find():
		try:
			newpoi = dict()
			newpoi['id'] = tweet['interaction']['interaction']['id']
			newpoi['screen_name'] = tweet['interaction']['interaction']['author']['username']
			newpoi['datetime_joined_twitter'] = datetime.datetime.strptime(tweet['interaction']['twitter']['user']['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
			newpoi['poi_classification'] = 0
			newpoi['datetime_last_timeline_scrape'] = datetime.datetime.now()
			newpoi['datetime_last_follower_scrape'] = datetime.datetime.now()
			newpoi['timeline_auth_error_flag']  = False
			newpoi['follower_auth_error_flag']  = False

			if newpoi['id'] < 0:
				print "negative id found! " + str(newpoi['id']) + "\t" +  newpoi['screen_name']
			else:
				try:
					poi.insert(anewpoi)
					# print "poi " + str(i) + " added."
				except pymongo.errors.DuplicateKeyError, e:
					#print "poi " + str(i) + "already in db!"
					pass
		except Exception, e:
		    print e

print "ECHELON will download and monitor " + str(poi.count()) + " twitter users"
