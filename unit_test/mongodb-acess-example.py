# -*- coding: utf-8 -*-
"""
Created on Thu Mar 12 15:59:54 2015

@author: home
"""

import ConfigParser
import datetime
from pymongo import Connection
 
config = ConfigParser.ConfigParser()
config.read('scraper.cfg')

# spin up database
DBNAME = config.get('database', 'name')

COLLECTION = config.get('database', 'collection')
print(DBNAME)
print(COLLECTION)

conn = Connection()
db = conn[DBNAME]
tweets = db[COLLECTION]


print("twitter connection and database connection configured")

def returnAllRecords(collection=tweets):
    #output = open("output.csv","w")
    print "Collection Size:",collection.count()
    count= 0
    for tweet in collection.find(): 
        try:
            ##twitter = tweet['interaction']['twitter']
            #print json.dumps(twitter)
            count = count+1
            print(tweet['text'])
            ##output.write(json.dumps(twitter)+"\n")
            #print jsonTweet['twitter']
            # timestamp = tweet['timestamp'].encode('utf-8').strip()
            # tweetUser = tweet['user'].encode('utf-8').strip()
            # tweetText = tweet['tweetText'].encode('utf-8').strip()
            # output.write(forumTitle+','+userName+'\n')
        except Exception, e :
            print e              

    print "total:" +str(count)
    
returnAllRecords()