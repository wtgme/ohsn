# -*- coding: utf-8 -*-
"""
Created on 1:11 PM, 10/30/15

@author: wt

"""
import ConfigParser
import datetime
from pymongo import Connection
import time
from twython import Twython, TwythonRateLimitError

config = ConfigParser.ConfigParser()
config.read('scraper.cfg')

# spin up twitter api
APP_KEY    = config.get('credentials','app_key')
APP_SECRET = config.get('credentials','app_secret')
OAUTH_TOKEN        = config.get('credentials','oath_token')
OAUTH_TOKEN_SECRET = config.get('credentials','oath_token_secret')

twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
twitter.verify_credentials()

# spin up database
DBNAME = config.get('database', 'name')
COLLECTION = config.get('database', 'collection')
conn = Connection()
db = conn[DBNAME]
tweets = db[COLLECTION]

status = twitter.get_application_rate_limit_status(resources = ['statuses'])
home_status = status['resources']['statuses']['/statuses/home_timeline']

def store_tweets(tweets_to_save, collection=tweets):
    """
    Simple wrapper to facilitate persisting tweets. Right now, the only
    pre-processing accomplished is coercing 'created_at' attribute to datetime.
    """
    for tw in tweets_to_save:
        tw['created_at'] = datetime.datetime.strptime(tw['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
    collection.insert(tweets_to_save)

def handle_rate_limiting():
    app_status = {'remaining':1} # prepopulating this to make the first 'if' check fail
    while True:
        wait = 0
        if app_status['remaining'] &gt; 0:
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

latest = None   # most recent id scraped
try:
    last_tweet = tweets.find(limit=1, sort=[('id',-1)])[0] # sort: 1 = ascending, -1 = descending
    if last_tweet:
        latest = last_tweet['id']
except:
    print "Error retrieving tweets. Database probably needs to be populated before it can be queried."

no_tweets_sleep = 1
while True:
    try:
        newest = None # this is just a flag to let us know if we should update the "latest" value
        params = {'count':200, 'contributor_details':True, 'since_id':latest}
        handle_rate_limiting()
        home = twitter.get_home_timeline(**params)
        if home:
            while home:
                store_tweets(home)

                # Only update "latest" if we're inside the first pass through the inner while loop
                if newest is None:
                    newest = True
                    latest = home[0]['id']

                params['max_id'] = home[-1]['id'] - 1
                handle_rate_limiting()
                home = twitter.get_home_timeline(**params)
        else:
            time.sleep(60*no_tweets_sleep)

    except TwythonRateLimitError, e:
        reset = int(twitter.get_lastfunction_header('x-rate-limit-reset'))
        wait = max(reset - time.time(), 0) + 10 # addding 10 second pad
        time.sleep(wait)
    except Exception, e:
        print e
        print "Non rate-limit exception encountered. Sleeping for 15 min before retrying"
        time.sleep(60*15)
