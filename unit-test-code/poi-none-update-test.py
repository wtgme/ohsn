# -*- coding: utf-8 -*-
"""
Created on Fri Jun 19 08:09:44 2015

@author: brendan
"""
# datasift-collection-processor
import datetime
import pymongo
import urllib
#import textprocessor
#import networkminer
# import poiclassifier

# POI_THRESHOLD = 0
TEST_SAMPLE_LIMIT = 10

ERROR_LOG_FILENAME = 'test-update_errorlog_' + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + '.log'
errorfile = open(ERROR_LOG_FILENAME, 'w')

# DATASIFTMONGOURL = "localhost"
DATASIFTMONGOURL = "aicvm-bjn1c13-1.ecs.soton.ac.uk"
DATASIFTMONGOUSER = "dsUser"
DATASIFTMONGOPWD = urllib.quote_plus('SiftLittleMentsals')
DATASIFTDBNAME = 'datasift'

# DATASIFT_PROCESSED_COLNAME = "update_test"

TWEETS_COLNAME = 'tweets'
POI_COLNAME = 'poi'
#OBS_COLNAME = 'observations'
#EDGES_COLNAME = 'edges'

DATASIFTMONGOAUTH = 'mongodb://' + DATASIFTMONGOUSER + ':' + DATASIFTMONGOPWD + '@' + DATASIFTMONGOURL + '/' + DATASIFTDBNAME
# connect to database
print DATASIFTMONGOAUTH

#try:
dsclient = pymongo.MongoClient(DATASIFTMONGOAUTH)
print DATASIFTMONGOUSER +" connected to " + DATASIFTDBNAME
dsdb = dsclient[DATASIFTDBNAME]

# Connect to all the collections   
timelines = dsdb[TWEETS_COLNAME] 
print "connected to collection: " + TWEETS_COLNAME
timelines.create_index([("interaction.twitter.id", pymongo.DESCENDING)], unique=True)
print "timeline unique index created on tweet id"

poi = dsdb[POI_COLNAME]
print "connected to collection: " + POI_COLNAME
poi.create_index([("user_id", pymongo.DESCENDING)], unique=True)
print "index created on " + POI_COLNAME + " by user_id"

#observations = dsdb[OBS_COLNAME]
#print "connected to collection: " + OBS_COLNAME
#observations.Xcreate_index([("user_id", pymongo.DESCENDING)], unique=True)
#print X "index created on " + OBS_COLNAME + " by ??????"

#edges = dsdb[EDGES_COLNAME]
#print "connected to collection: " + EDGES_COLNAME
#edges. X create_index([("user_id", pymongo.DESCENDING)], unique=True)
#print X "index created on " + EDGES_COLNAME + " by ??????????"


def create_poi_from_datasift_tweet(ds_tweet):

    newpoi = dict()               
    newpoi['id'] = ds_tweet['interaction']['twitter']['user']['id']
    newpoi['id_str'] = ds_tweet['interaction']['twitter']['user']['id_str']
    newpoi['screen_name'] = ds_tweet['interaction']['twitter']['user']['screen_name']
    newpoi['datetime_joined_twitter'] = datetime.datetime.strptime(ds_tweet['interaction']['twitter']['user']['created_at'], '%a, %d %b %Y %H:%M:%S +0000')
    # newpoi['poi_classification'] = poiclassifier.getPoiClassification(ds_tweet)
    newpoi['lang'] = ds_tweet['interaction']['twitter']['lang']
    newpoi['poi_classification'] = 0
    newpoi['datetime_last_timeline_scrape'] = datetime.datetime.now()
    newpoi['datetime_last_follower_scrape'] = datetime.datetime.now()
    newpoi['timeline_auth_error_flag']  = False
    newpoi['follower_auth_error_flag']  = False
    return newpoi
    

def create_fake_tweet_1():
    tweet = {}
    tweet['interaction'] = {}
    tweet['interaction']['twitter'] = {}
    tweet['interaction']['twitter']['id'] = 555620518624497666
    tweet['interaction']['twitter']['user'] = {}
    tweet['interaction']['twitter']['user']['id']  = 5647729299292    
    tweet['interaction']['twitter']['user']['id_str'] = '5647729299292'
    tweet['interaction']['twitter']['user']['screen_name'] = "testy"
    tweet['interaction']['twitter']['user']['lang'] = "en-gb"
    tweet['interaction']['twitter']['user']['created_at'] = 'Thu, 15 Jan 2015 07:00:29 +0000'
    tweet['interaction']['twitter']['created_at'] =  'Thu, 15 Jan 2015 07:00:29 +0000'
    tweet['interaction']['twitter']['user']['description'] = '15, anorexic, cw=40kg, gw=34kg' 
    tweet['interaction']['twitter']['text'] = 'blah blah blah RT @jane hw=35'   
#    tweet['interaction']['twitter']['created_at'] =  'Thu, 16 Jan 2015 07:00:29 +0000'
#    tweet['interaction']['twitter']['user']['description'] = '15, anorexic, cw=40kg, gw=34kg' 
#    tweet['interaction']['twitter']['text'] = 'blah blah cw=35 blah '   
    return tweet
    
def create_fake_tweet_2():
    tweet = {}
    tweet['interaction']
    tweet['interaction']['twitter'] = {}    
    tweet['interaction']['twitter']['id'] = 555620518624497667
    tweet['interaction']['twitter']['user'] = {}
    tweet['interaction']['twitter']['user']['id']  = 5647729299292    
    tweet['interaction']['twitter']['user']['id_str'] = '5647729299292'
    tweet['interaction']['twitter']['user']['screen_name'] = "testy"
    tweet['interaction']['twitter']['user']['lang'] = "en-gb"
    tweet['interaction']['twitter']['user']['created_at'] = 'Thu, 15 Jan 2015 07:00:29 +0000'
#    tweet['interaction']['twitter']['created_at'] =  'Thu, 15 Jan 2015 07:00:29 +0000'
#    tweet['interaction']['twitter']['user']['description'] = '15, anorexic, cw=40kg, gw=34kg' 
#    tweet['interaction']['twitter']['text'] = 'blah blah blah RT @jane hw=35'        
    tweet['interaction']['twitter']['created_at'] =  'Thu, 16 Jan 2015 07:00:29 +0000'
    tweet['interaction']['twitter']['user']['description'] = '15, anorexic, cw=40kg, gw=34kg' 
    tweet['interaction']['twitter']['text'] = 'blah blah cw=35 blah '
    return tweet

try:
    tweet = create_fake_tweet_1()
    timelines.insert(tweet)
except pymongo.errors.DuplicateKeyError, e:
    print "Duplicate Tweet"
#create_fake_tweet_1()
try:
    newpoi = create_dummy_poi(tweet)
    poi.insert(newpoi)
except pymongo.errors.DuplicateKeyError, e:
    print "Duplicate POI"

for person in poi.find():
    print person
    
for tweet in timelines.find():
    print tweet
    
exit()

#    
#meta = textprocessor.mineTweet(tweet)
#print meta
#
#exit()

#meta = {}
#meta['text_anal']={}
#meta['text_anal']['lang'] = "en-gb" 
#meta['text_anal']['status_id'] = 2344432434
#meta['text_anal']['parser_version'] = 0.01
#
#meta['text_anal']['cw'] = 39
## meta['text_anal']['cw-updated'] = datetime.datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
#meta['text_anal']['cw-updated'] = tweet['created_at']
#
#meta['text_anal']['gw'] = 33
## meta['text_anal']['gw-updated'] = datetime.datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
#meta['text_anal']['gw-updated'] = tweet['created_at']
#
#meta['text_anal']['lw'] = 32
## meta['text_anal']['lw-updated'] = datetime.datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
#meta['text_anal']['lw-updated'] = tweet['created_at']
#
#meta['text_anal']['hw'] = 74
## meta['text_anal']['hw-updated'] = datetime.datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
#meta['text_anal']['hw-updated'] = tweet['created_at']
#
#poi = psoi.find({'user_id':5647729299292 })[0]
#
#if meta['text_anal']['cw'] is not None:
#    if meta['text_anal']['cw-updated'] < meta['text_anal']['cw-updated']:
#        poi['text_anal']['cw'] = meta['text_anal']['cw']
#        poi['text_anal']['cw-updated'] = tweet['created_at']
#
#        
#psoi.update({'user_id':poi['user_id']}, {"$unset":{"text_anal":""}})
#psoi.update({'user_id':poi['user_id']}, {'$set' : {'text_anal':poi['text_anal']}})
#
#for poi in psoi.find():
#    print poi