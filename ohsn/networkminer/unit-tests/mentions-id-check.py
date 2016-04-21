# -*- coding: utf-8 -*-
"""
Created on Thu May 07 12:32:49 2015

@author: home
"""

from pymongo import MongoClient

#Usi this method FIRST in order to establish a connection to a server
def connectToMongoServer(serverAddress):
    try:
        global client
        client = MongoClient(serverAddress)
    except:
        print "error"

#connec to a database
def connectoMongoDatabase(databaseName):
    try:
        global db
        db = client[databaseName]
    except Exception, e:
        print e

#connec to a database
def connectoMongoCollection(collectionName):
    try:
        global collection
        collection = db[collectionName]
    except Exception, e:
        print e


def print_mentions():
   
    for tweet in collection.find().limit(100): 
                print "-------"
                try:
                    print tweet['interaction']['interaction']['author']['username']
                    print tweet['interaction']['twitter']['user']['id']
                    print tweet['interaction']['twitter']['user']['id_str']
                    for ment in tweet['interaction']['interaction']['mentions']: print ment
                    for ment in tweet['interaction']['interaction']['mention_ids']: print ment
                   
                except Exception, e :
                    print "no mentions"

#main run module
if __name__ == '__main__':
    
    connectToMongoServer("mongodb://dsUser:webobservatory@ec2-54-228-51-114.eu-west-1.compute.amazonaws.com:27017/datasift");
    #connectToMongoServer("mongodb://justin:password123@mdb-001.ecs.soton.ac.uk:27017/twitter_immigration");
    connectoMongoDatabase("datasift")
    connectoMongoCollection("twitter_obesity_tweet_ana_2015_02")
    #datasift.twitter_obesity_profile_GW_2015_02
    #do a check to see if you can found the collection and records.
    
    #print "TODO: not all urls are being captured?"
    #crossfit #vegan #anorexia #gym http://t.co/QHODdovVx2
        
    print_mentions()
    