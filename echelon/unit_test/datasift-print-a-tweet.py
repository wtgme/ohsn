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

# DATASIFTCOLNAMES = ["twitter_obesity_profile_GW_2015_01",'twitter_obesity_profile_GW_2015_02',"twitter_obesity_profile_GW_2015_03"]
DATASIFTCOLNAMES = ["twitter_obesity_profile_GW_2015_01"]

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

#ECHELONMONGOURL = "aicvm-bjn1c13-1.ecs.soton.ac.uk"
ECHELONMONGOURL = "localhost"
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
	print ECHELONMONGOUSER +" connected to " + ECHELONDBNAME
	ecdb = ecclient[ECHELONDBNAME]
	poi = ecdb[ECHELONCOLNAME]
except Exception, e:
	print ECHELONMONGOUSER +" FAILED to connect to " + ECHELONDBNAME
	exit()

print "ECHELON db connection established"

poi.create_index([("id", pymongo.DESCENDING)], unique=True)
print "poi index created on id parameter"

for col in DATASIFTCOLNAMES:
	dstweets = dsdb[col]
	print "Found " + str(dstweets.count()) + " tweets in " + col
	for tweet in dstweets.find().limit(1):
		print tweet['interaction']
