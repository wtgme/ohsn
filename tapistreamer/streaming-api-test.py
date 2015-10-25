# -*- coding: utf-8 -*-
"""
Created on Wed Jun 03 03:43:09 2015

@author: home
"""

from twython import TwythonStreamer

import urllib
import imghdr
import os
import ConfigParser
import datetime
from pymongo import Connection
#import time
#from twython import Twython, TwythonRateLimitError

config = ConfigParser.ConfigParser()
config.read('streamer.cfg')
 
# spin up twitter api
APP_KEY    = config.get('credentials','app_key')
APP_SECRET = config.get('credentials','app_secret')
OAUTH_TOKEN        = config.get('credentials','oath_token')
OAUTH_TOKEN_SECRET = config.get('credentials','oath_token_secret')

# spin up database
DBNAME = 'twitter_test'
COLLECTION = 'stream'
print(DBNAME)
print(COLLECTION)
conn = Connection()
db = conn[DBNAME]
tweets = db[COLLECTION]

print("twitter connection and database connection configured")

class MyStreamer(TwythonStreamer):
    def on_success(self, data):
        if 'warning' in data:
            print data['warning']['code'] + "\t" + data['warning']['message'] + "\t percent_full=" + data['warning']['percent_full']
            output = open("streaming-warnings.log","w")
            output.write( data['warning']['code'] + "\t" + data['warning']['message'] + "\t percent_full=" + data['warning']['percent_full'] +"\n")
            output.close()
        if 'text' in data:
            store_tweet(data)
            # print data['user']['screen_name'].encode('utf-8') + "\t" + data['text'].encode('utf-8').replace('\n', ' ') 
            
    def on_error(self, status_code, data):
        print status_code
        output = open("streaming-errors.log","w")
        output.write( data['warning']['code'] + "\t" + data['warning']['message'] + "\t percent_full=" + data['warning']['percent_full'] +"\n")
        output.close()

        # Want to stop trying to get data because of the error?
        # Uncomment the next line!
        # self.disconnect()

def get_pictures(tweet):
        # Get pictures in the tweets store as date-tweet-id-username.ext
        try:
            for item in tweet['entities']['media']:
                print item['media_url_https']
                if item['type']=='photo':
                    # print "PHOTO!!!"
                    urllib.urlretrieve(item['media_url_https'], 'api-timelines-scraper-media/' + item['id_str'])
                    # code to get the extension.... 
                    ext = imghdr.what('api-timelines-scraper-media/' + item['id_str'])
                    os.rename('api-timelines-scraper-media/' + item['id_str'], 'api-timelines-scraper-media/' + item['id_str'] + "." + ext)
        except: 
            pass

def store_tweet(tweet, collection=tweets, pictures=False):
    """
    Simple wrapper to facilitate persisting tweets. Right now, the only
    pre-processing accomplished is coercing date values to datetime.
    """
    tweet['created_at'] = datetime.datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
    tweet['user']['created_at'] = datetime.datetime.strptime(tweet['user']['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
    # get pictures in tweet...
    if pictures:
        get_pictures(tweet)
 
    #print "TODO: alter the schema of the tweet to match the edge network spec from the network miner..."
    #print "TODO: make the tweet id a unique index to avoid duplicates... db.collection.createIndex( { a: 1 }, { unique: true } )"
    collection.insert(tweet)
    # print("storing tweets")

while True:
    try:
        stream = MyStreamer(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
        # https://dev.twitter.com/streaming/overview/request-parameters                                 
        # stream.statuses.filter(language=['en'], track=['bulimic, anorexic, ednos, ed-nos, bulimia, anorexia, eating disorder, eating-disorder, eating disordered, eating-disordered, CW, UGW, GW2, GW1, GW'])                                 
        stream.statuses.filter(language=['en'], track=['bulimic, anorexic, ednos, ed-nos, bulimia, anorexia, eating disorder, eating-disorder, eating disordered, eating-disordered, CW, UGW, GW2, GW1, GW, thinspiration, thinspo, bonespo, bonespiration'])
    except:
        print "error to file"