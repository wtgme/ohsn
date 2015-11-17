# -*- coding: utf-8 -*-
"""
Created on Sat Jun 13 09:07:17 2015
@author: home
"""

import datetime
import pymongo
import urllib
import cwgwprocessor
import poiclassifier

# POI_THRESHOLD = 0

ERROR_LOG_FILENAME = 'POI_UPLOADER_ErrorLog_' + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + '.log'
errorfile = open(ERROR_LOG_FILENAME, 'w')

DATASIFTMONGOURL = "localhost"
DATASIFTMONGOUSER = "dsUser"
DATASIFTMONGOPWD = urllib.quote_plus('"SiftLittleMentsals"')
DATASIFTDBNAME = 'datasift'

DATASIFT_PROCESSED_COLNAME = "datasift_all_enriched"
# DATASIFTCOLNAMES = ["twitter_obesity_profile_GW_2015_01",'twitter_obesity_profile_GW_2015_02',"twitter_obesity_profile_GW_2015_03"]
# DATASIFTCOLNAMES = ["twitter_obesity_profile_GW_2015_01"]

print "TODO: add other datasift collections to list"

DATASIFTMONGOAUTH = 'mongodb://' + DATASIFTMONGOUSER + ':' + DATASIFTMONGOPWD + '@' + DATASIFTMONGOURL + '/' + DATASIFTDBNAME
# connect to database
#print DATASIFTMONGOAUTH

try:
    dsclient = pymongo.MongoClient(DATASIFTMONGOAUTH)
    print DATASIFTMONGOUSER +" connected to " + DATASIFTDBNAME
    dsdb = dsclient[DATASIFTDBNAME]
    processed = dsdb[DATASIFT_PROCESSED_COLNAME]
    # create an index on the tweet id so we don't get duplicates
    dsdb.processed.createIndex({'interaction.twitter.id' : 1}, {'unique' : True, 'dropDups' : True})
except Exception:
    print DATASIFTMONGOUSER +" FAILED to connect to " + DATASIFTDBNAME
    exit()

#print "DATASIFT db connection established"

#ECHELONMONGOURL = "aicvm-bjn1c13-1.ecs.soton.ac.uk"
ECHELONMONGOURL = "localhost"
ECHELONMONGOUSER = "harold"
ECHELONMONGOPWD = urllib.quote_plus('AcKerTalksMaChine')
ECHELONDBNAME = 'echelon'
ECHELONCOLNAME = 'poi'
#MONGOAUTH = "localhost"
ECHELONMONGOAUTH = 'mongodb://' + ECHELONMONGOUSER + ':' + ECHELONMONGOPWD + '@' + ECHELONMONGOURL + '/' + ECHELONDBNAME

# connect to database
#print ECHELONMONGOAUTH

try:
    ecclient = pymongo.MongoClient(ECHELONMONGOAUTH)
    print ECHELONMONGOUSER +" connected to " + ECHELONDBNAME
    ecdb = ecclient[ECHELONDBNAME]
    poi = ecdb[ECHELONCOLNAME]
    ecdb.poi.create_index([("id", pymongo.DESCENDING)], unique=True)
    #print "poi index created on id parameter"
except Exception, e:
    print ECHELONMONGOUSER +" FAILED to connect to " + ECHELONDBNAME
    exit()

#print "ECHELON db connection established"

#for col in DATASIFTCOLNAMES:
#    dstweets = dsdb[col]
#    # create an index on the tweet id so we don't get duplicates
#    dstweets.createIndex({'interaction.twitter.id' : 1}, {'unique' : True, 'dropDups' : True})
#
#    print "Found " + str(dstweets.count()) + " tweets in " + col
#    print "processing for measurement data and saving to " + DATASIFT_PROCESSED_COLNAME
#
#    for tweet in dstweets.find():
#        # fix the mangled id values.
#        if tweet['interaction']['twitter']['user']['id'] < 0:
#            tweet['interaction']['twitter']['user']['id'] = long(tweet['interaction']['twitter']['user']['id_str'])
#            #error = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  +\t + "negative id found! " + str(newpoi['id']) + "\t" +  newpoi['screen_name'] +"\t"+ str(newpoi['id']) + "=" + tweet['interaction']['twitter']['user']['id_str'] + "?"
#            #errorfile.write(error)
#            #errorfile.flush()
#        echtweet = cwgwprocessor.mineTweet(tweet['interaction']['twitter'])
#        # upload to processed with added echelon data
#        processed.insert(echtweet)
#    
#print "Found " + str(processed.count()) + " tweets in " + DATASIFT_PROCESSED_COLNAME
#
#exit()

print "processing for poi"
print "TODO: Group by userID"

for tweet in processed.find():
    try:
        # if tweet['interaction']['echelon']['poiclassification'] > POI_THRESHOLD:
        #    print "TODO what if the same user has different descriptions and poi class?" 
            # fix the mangled id values.
        if tweet['interaction']['twitter']['user']['id'] < 0:
            tweet['interaction']['twitter']['user']['id'] = long(tweet['interaction']['twitter']['user']['id_str'])
            #error = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  +\t + "negative id found! " + str(newpoi['id']) + "\t" +  newpoi['screen_name'] +"\t"+ str(newpoi['id']) + "=" + tweet['interaction']['twitter']['user']['id_str'] + "?"
            #errorfile.write(error)
            #errorfile.flush()
         
        newpoi = dict()               
        newpoi['id'] = tweet['interaction']['twitter']['user']['id']
        newpoi['screen_name'] = tweet['interaction']['twitter']['user']['screen_name']
        newpoi['datetime_joined_twitter'] = datetime.datetime.strptime(tweet['interaction']['twitter']['user']['created_at'], '%a, %d %b %Y %H:%M:%S +0000')
        
        # newpoi['poi_classification'] = poiclassifier.getPoiClassification(tweet)
        newpoi['poi_classification'] = 0 
        newpoi['datetime_last_timeline_scrape'] = datetime.datetime.now()
        newpoi['datetime_last_follower_scrape'] = datetime.datetime.now()
        newpoi['timeline_auth_error_flag']  = False
        newpoi['follower_auth_error_flag']  = False
   
        #need to process for match on keywords / weight
        #need to include the rationale/stats extracted here? NAH!!! KEEP it SEPERATE this is for monitor/timeline only
        #we can do stats from this, and do the datasift stats seperatly.
           
        try:
            poi.insert(newpoi)
            # print "poi " + str(i) + " added."
        except pymongo.errors.DuplicateKeyError, e:
            pass
            #print "poi " + str(i) + "already in db!"
        except Exception, e:
            print e
                   
print "ECHELON will download and monitor " + str(poi.count()) + " twitter users"