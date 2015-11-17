# -*- coding: utf-8 -*-
"""
Created on Tue Jun 16 18:17:30 2015

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
    test.create_index([("tweetid", pymongo.DESCENDING)], unique=True)
    #print "poi index created on id parameter"
except Exception, e:
	print ECHELONMONGOUSER +" FAILED to connect to " + ECHELONDBNAME
	exit()

for i in range(sampleSize):
    doc = {}
    doc['tweetid'] = i
    doc['id'] = random.randint(0,9)
    doc['date'] = datetime.datetime.now() 

    if random.random() < 0.5:
        doc['TCW'] = random.randint(45,55)
    if random.random() < 0.5:
        doc['DCW'] = random.randint(43,49)
    if random.random() < 0.5:    
        doc['TGW'] = random.randint(35,39)
    if random.random() < 0.5:    
        doc['DGW'] = random.randint(29,33)
    
    test.insert(doc)



    
# So each tweet becomes a data point if it contains a piece of data
# TCW = [(datetime,value), (datetime,value), (datetime,value) ]
# In r I can just tell it to skip null values?