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

"mongodb://dsUser:webobservatory@ec2-54-228-51-114.eu-west-1.compute.amazonaws.com:27017/datasift"
"datasift"
"twitter_obesity_profile_GW_2015_02"


MONGOURL = "ec2-54-228-51-114.eu-west-1.compute.amazonaws.com"
MONGOUSER = "dsUser"
MONGOPWD = urllib.quote_plus('webobservatory')
DBNAME = 'datasift'

COLNAME = 'twitter_obesity_profile_GW_2015_02'

MONGOAUTH = 'mongodb://' + MONGOUSER + ':' + MONGOPWD + '@' + MONGOURL + '/' + DBNAME
# connect to database
print MONGOAUTH

try:
	client = pymongo.MongoClient(MONGOAUTH)
	print MONGOUSER +" connected to " + DBNAME
	db = client[DBNAME]
	col = db[COLNAME]
except Exception, e:
	print MONGOUSER +" FAILED to connect to " + DBNAME
	exit()

print "db connection established"
