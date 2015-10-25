# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 12:29:37 2015
Initial code purloined from the example at: https://unsupervisedlearning.wordpress.com/
@author: Brendan Neville

"""
import urllib
import imghdr
import os
import ConfigParser
import datetime
from pymongo import Connection
import time
from twython import Twython, TwythonRateLimitError, TwythonAuthError
 
config = ConfigParser.ConfigParser()
config.read('scraper.cfg')
 
# spin up twitter api
APP_KEY    = config.get('credentials','app_key')
APP_SECRET = config.get('credentials','app_secret')
OAUTH_TOKEN        = config.get('credentials','oath_token')
OAUTH_TOKEN_SECRET = config.get('credentials','oath_token_secret')

#twitter = Twython(app_key='Mfm5oNdGSPMvwhZcB8N4MlsL8',
#    app_secret='C0rbmJP0uKbuF6xcT6aR5vFOV9fS4L1965TKOH97pSqj3NJ1mP',
#    oauth_token='3034707280-wFGQAF4FGBviaiSguCUdeG36NIQG1uh8qqXTC1G',
#    oauth_token_secret='HUWMfHKyPShE6nH5WXlI26izoQjNtV3US3mNpND1F9qrO')
 
twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
twitter.verify_credentials()
 
# spin up database
DBNAME = config.get('database', 'name')
COLLECTION = config.get('database', 'collection')
COLLECTION = 'manostimeline'
print(DBNAME)
print(COLLECTION)

conn = Connection()
db = conn[DBNAME]
tweets = db[COLLECTION]

on_exception_waittime = 60*15

print("twitter connection and database connection configured")

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

def store_tweets(tweets_to_save, collection=tweets, pictures=False):
    """
    Simple wrapper to facilitate persisting tweets. Right now, the only
    pre-processing accomplished is coercing date values to datetime.
    """
    for tw in tweets_to_save:
        tw['created_at'] = datetime.datetime.strptime(tw['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
        tw['user']['created_at'] = datetime.datetime.strptime(tw['user']['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
        # get pictures in tweet...
        if pictures:
            get_pictures(tw)
 
    print "TODO: alter the schema of the tweet to match the edge network spec from the network miner..."
    print "TODO: make the tweet id a unique index to avoid duplicates... db.collection.createIndex( { a: 1 }, { unique: true } )"
    collection.insert(tweets_to_save)
    print("storing tweets")
 
def handle_rate_limiting():
    app_status = {'remaining':1} # prepopulating this to make the first 'if' check fail
    while True:
        wait = 0
        if app_status['remaining'] > 0:
            status = twitter.get_application_rate_limit_status(resources = ['statuses', 'application'])
            app_status = status['resources']['application']['/application/rate_limit_status']
            home_status = status['resources']['statuses']['/statuses/home_timeline']
            if home_status['remaining'] == 0:
                wait = max(home_status['reset'] - time.time(), 0) + 1 # addding 1 second pad
                time.sleep(wait)
            else:
                return
        else :
            wait = max(app_status['reset'] - time.time(), 0) + 10
            time.sleep(wait)


def get_user_timeline(username):
    print username
    # get the user's timeline or in all likelihood the update to their timeline
    # process those tweets for new mentions/replies 
    # if those users are new.. add those users to the list of nodes to get timelines for... mark these nodes with the orginal usernames rank + 1...
    # if the user is already in the database check if thier rank is currently >= thisuserrank + 1 if so reduce their rank to thisuserrank + 1
    latest = None   # most recent id scraped
    #print "TODO: Change this so it gets the last tweet of a specific user..."
       
    try:
        # last_tweet = tweets.find(None, sort=[('id',-1)]).limit( 1 )[0] # sort: 1 = ascending, -1 = descending
        last_tweet = tweets.find({'user.screen_name':username}, sort=[('id',-1)]).limit( 1 )[0] # sort: 1 = ascending, -1 = descending
        if last_tweet:
            latest = last_tweet['id']
            print str(latest)
    except Exception, e:
        print "Error retrieving tweets. username not found or database probably needs to be populated before it can be queried." + str(e)
    
    while True:
        try:
            newest = None # this is just a flag to let us know if we should update the "latest" value
            #params = {'screen_name':'anasecretss', 'since_id':latest}
            print "latest = " + str(latest)
            # latest = 0
            params = {'count':200, 'contributor_details':True, 'screen_name':username, 'since_id':latest, 'include_rts':1}
            #params = {'count':200, 'contributor_details':True, 'since_id':latest}
            
            handle_rate_limiting()
            #home = twitter.get_home_timeline(**params)
            home = twitter.get_user_timeline(**params)
            print("querying twitter")
            if home:
                while home:
                    store_tweets(home)
     
                    # Only update "latest" if we're inside the first pass through the inner while loop
                    if newest is None:
                        newest = True
                        latest = home[0]['id']
     
                    params['max_id'] = home[-1]['id'] - 1
                    handle_rate_limiting()
                    home = twitter.get_user_timeline(**params)
                    # user_timeline=twitter.getUserTimeline(screen_name="dksbhj", count=200, include_rts=1)
            else: 
                print "Ran out of tweets for the current username"
                break
     
        except TwythonRateLimitError, e:
            print "Rate-limit exception encountered. Sleeping for ~ 15 min before retrying"
            print datetime.datetime.now().time()
            reset = int(twitter.get_lastfunction_header('x-rate-limit-reset'))
            wait = max(reset - time.time(), 0) + 10 # addding 10 second pad
            time.sleep(wait)
        except TwythonAuthError, e:
            # most likely this is due to a private user, so its best to give up.
            home = None
            print e
            break
        except Exception, e:
            print e
            print "Non rate-limit exception encountered. Sleeping for 15 min before retrying"
            time.sleep(on_exception_waittime)
    
    
def get_user_timelines(usernames, persistant=False):

    if persistant:       
        while True:
            for username in usernames:
                get_user_timeline(username)
       
            print "Checked for updates on all the usernames... going around again... in 15 minutes"
            # time.sleep(60*15)
            time.sleep(60*1)
    else:
        for username in usernames:
            get_user_timeline(username)

# Get all the usernames 
# Get all the usernames from the nodes database
print("loading list of nodes of interest...")
print "TODO: Change so it runs through and monitors the users in the node database with rank <= 2..."

# usernames = {'needingbones', 'anasecretss', 'tiinyterry'}
usernames = {'ementzakis'}
get_user_timelines(usernames, persistant=True)


#username = 'drbnev'
#get_user_timeline(username)
