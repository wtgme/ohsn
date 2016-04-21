# -*- coding: utf-8 -*-
"""
Created on Tue Jun 16 20:17:06 2015

@author: brendan
"""

import random
import datetime
import pymongo
import urllib

# insert a few documents with the following fields
# id date TCW DCW TGW DGW
sampleSize = 500  ## Try making this value bigger

## Initialize the random seed using the system clock
## (although this is done by default anyway)
random.seed()

ECHELONMONGOURL = "aicvm-bjn1c13-1.ecs.soton.ac.uk"
#ECHELONMONGOURL = "localhost"
ECHELONMONGOUSER = "harold"
ECHELONMONGOPWD = urllib.quote_plus('AcKerTalksMaChine')
ECHELONDBNAME = 'echelon'
ECHELONCOLNAME = 'timeseriestest'
#MONGOAUTH = "localhost"
ECHELONMONGOAUTH = 'mongodb://' + ECHELONMONGOUSER + ':' + ECHELONMONGOPWD + '@' + ECHELONMONGOURL + '/' + ECHELONDBNAME

# connect to database
#print ECHELONMONGOAUTH

try:
    ecclient = pymongo.MongoClient(ECHELONMONGOAUTH)
    print ECHELONMONGOUSER +" connected to " + ECHELONDBNAME
    ecdb = ecclient[ECHELONDBNAME]
    test = ecdb[ECHELONCOLNAME]
    # test.create_index([("tweetid", pymongo.DESCENDING)], unique=True)
    #print "poi index created on id parameter"
except Exception, e:
	print ECHELONMONGOUSER +" FAILED to connect to " + ECHELONDBNAME
	exit()

#for tweet in test.find():
#    print tweet['id'] + str(tweet['TCW'])

for tweet in test.find( { 'TCW': { '$exists': True } } ):
    print tweet['id'] + str(tweet['TCW'])




    
# So each tweet becomes a data point if it contains a piece of data
# TCW = [(datetime,value), (datetime,value), (datetime,value) ]
# In r I can just tell it to skip null values?