# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 10:56:50 2015

@author: brendan
"""

# datasift-collection-processor
import datetime
import pymongo
import urllib
import textprocessor
# import networkminer
# import poiclassifier

# POI_THRESHOLD = 0
TEST_SAMPLE_LIMIT = 10

ERROR_LOG_FILENAME = 'log/datasift-collection-processor_errorlog_' + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + '.log'
errorfile = open(ERROR_LOG_FILENAME, 'w')

DATASIFTMONGOURL = "localhost"
DATASIFTMONGOUSER = "dsUser"
DATASIFTMONGOPWD = urllib.quote_plus('SiftLittleMentsals')
DATASIFTDBNAME = 'datasift'

DATASIFT_PROCESSED_COLNAME = "datasift_all"
DATASIFT_POI_COLNAME = "datasift_poi"

DATASIFTMONGOAUTH = 'mongodb://' + DATASIFTMONGOUSER + ':' + DATASIFTMONGOPWD + '@' + DATASIFTMONGOURL + '/' + DATASIFTDBNAME
# connect to database
print DATASIFTMONGOAUTH
dsclient = pymongo.MongoClient(DATASIFTMONGOAUTH)
print DATASIFTMONGOUSER +" connected to " + DATASIFTDBNAME
dsdb = dsclient[DATASIFTDBNAME]
processed = dsdb[DATASIFT_PROCESSED_COLNAME]
print "connected to collection: " + DATASIFT_PROCESSED_COLNAME
# create an index on the tweet id so we don't get duplicates
# timelines.create_index([("id", pymongo.DESCENDING)], unique=True)
processed.create_index([("interaction.twitter.id", pymongo.DESCENDING)], unique=True)
print "index created on " + DATASIFT_PROCESSED_COLNAME + " by interaction.twitter.id"
poi = dsdb[DATASIFT_POI_COLNAME]
print "connected to collection: " + DATASIFT_POI_COLNAME
poi.create_index([("id", pymongo.DESCENDING)], unique=True)
print "index created on " + DATASIFT_POI_COLNAME + " by id"


# connect to the webobs
serverAddress = "mongodb://dsUser:webobservatory@ec2-54-228-51-114.eu-west-1.compute.amazonaws.com:27017/datasift"
databaseName = "datasift"

DATASIFTCOLNAMES = ['twitter_obesity_profile_GW_2015_01',
'twitter_obesity_profile_GW_2015_02',
'twitter_obesity_profile_GW_2015_03',
'twitter_obesity_profile_ana_2015_01',
'twitter_obesity_profile_ana_2015_02',
'twitter_obesity_profile_ana_2015_03',
'twitter_obesity_tweet_GW_2015_01',
'twitter_obesity_tweet_GW_2015_02',
'twitter_obesity_tweet_GW_2015_03',
'twitter_obesity_tweet_ana_2015_01',
'twitter_obesity_tweet_ana_2015_02',
'twitter_obesity_tweet_ana_2015_03']

client = pymongo.MongoClient(serverAddress)
db = client[databaseName]

for col in DATASIFTCOLNAMES:
    dstweets = db[col]
    dstweets.create_index([("interaction.twitter.id", pymongo.DESCENDING)])
    print "index created on " + col + " by interaction.twitter.id"
    print "Found " + str(dstweets.count()) + " tweets in " + col
    print "processing for measurement data and saving to " + DATASIFT_PROCESSED_COLNAME
    print "WARNING THIS ASSUMES TWEETS ARRIVE IN TIME ORDER!!!!"    
    
    # for tweet in dstweets.find().sort('interaction.twitter.id', 1).limit(TEST_SAMPLE_LIMIT):
    for tweet in dstweets.find().sort('interaction.twitter.id', 1):
        
        # print tweet['interaction']['twitter']['created_at']

        
        # fix the mangled id values.
        if tweet['interaction']['twitter']['user']['id'] < 0:
            tweet['interaction']['twitter']['user']['id'] = long(tweet['interaction']['twitter']['user']['id_str'])
            #error = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  +\t + "negative id found! " + str(newpoi['id']) + "\t" +  newpoi['screen_name'] +"\t"+ str(newpoi['id']) + "=" + tweet['interaction']['twitter']['user']['id_str'] + "?"
            #errorfile.write(error)
            #errorfile.flush()        
        try:          
            
            # when the analysers are run later as seperate proc we will update the echelon structure not insert.
            # or you will get a duplicate key error
            processed.insert(tweet)
            textprocessor.processDatasiftTweet(tweet, poi, processed)

            # meta = networkminer.processDatasiftTweet(tweet, edges)
#            edges.insert(meta)
#            tweet['echelon']['rmr-edge-detector'] = {}
#            tweet['echelon']['rmr-edge-detector']['dateparsed'] = meta['dateparsed']
#            tweet['echelon']['rmr-edge-detector']['parser_version'] = meta['parser_version']
            
            # we should add nodes to poi
            # poi will have an index on id so how will that work with mentions?
            # can we get a id from the mentions data in twitter api and datasift?
            # poi.insert() not none values... if last obs time < this ones....            
           
        except pymongo.errors.DuplicateKeyError, e:
            error = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + "DuplicateKeyError " + str(tweet['interaction']['twitter']['id']) + "\n" 
            errorfile.write(error)
            errorfile.flush()            
            print "tweet id already in db!"
            pass
            #print "poi " + str(i) + "already in db!"
        except Exception, e:
            print e

print "Found " + str(processed.count()) + " tweets in " + DATASIFT_PROCESSED_COLNAME

# processed.find()

#for tweet in processed.find():
#    print tweet

#for ob in observations.find():
#    print ob
    
