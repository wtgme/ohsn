# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 12:29:37 2015
Initial code purloined from the example at: https://unsupervisedlearning.wordpress.com/
Since then I've changed quite a bit, but credit where its due :)
@author: Brendan Neville
"""

import urllib
import imghdr
import os
import datetime
import pymongo
import time
from twython import Twython, TwythonRateLimitError, TwythonAuthError, TwythonError
import re

# spin up database collections
# Echelon connection    

MONGOURL = 'aicvm-bjn1c13-1.ecs.soton.ac.uk'
MONGOUSER =  'harold'
DBPASSWD = 'AcKerTalksMaChine'
DBNAME = 'echelon'
MONGOAUTH = 'mongodb://' + MONGOUSER + ':' + DBPASSWD + '@' + MONGOURL + '/' + DBNAME
POI_COL = 'poi'
TIMELINES_COL = 'timelines'

try:
    conn = pymongo.MongoClient(MONGOAUTH)
    db = conn[DBNAME]
    
    poi = db[POI_COL]
    print  MONGOUSER +" connected to " + DBNAME  + "." + POI_COL
    poi.create_index([("id", pymongo.DESCENDING)], unique=True)
    print "index created on " + POI_COL + " by id"            

    timelines = db[TIMELINES_COL]
    print  MONGOUSER +" connected to " + DBNAME  + "." + TIMELINES_COL
    timelines.create_index([("id", pymongo.DESCENDING)], unique=True)
    print "timeline unique index created on tweet id"

except Exception:
    print MONGOUSER +" FAILED to connect to " + DBNAME
    exit()

# Twitter application auth codes...    
APP_KEY    = 'Mfm5oNdGSPMvwhZcB8N4MlsL8'
APP_SECRET = 'C0rbmJP0uKbuF6xcT6aR5vFOV9fS4L1965TKOH97pSqj3NJ1mP'
OAUTH_TOKEN        = '3034707280-wFGQAF4FGBviaiSguCUdeG36NIQG1uh8qqXTC1G'
OAUTH_TOKEN_SECRET = 'HUWMfHKyPShE6nH5WXlI26izoQjNtV3US3mNpND1F9qrO'

TIMELINE_POI_CLASS_THRESHOLD = 1
GET_TIMELINE_IMAGES = False
#current TAPI max is 200
GET_USER_TIMELINE_COUNT = 200
# wait for 15 minutes if an exception occurs
ON_EXCEPTION_WAIT = 60*15

ON_404_WAIT = 60
# don't scrape a user more than once every day.
# Turn this into a timedelta
MIN_RESOLUTION = datetime.timedelta(seconds=86400)
# if no poi are due to be harvested wait this long..
# the logic being that if you dynamically add new poi it will spot the new poi in this amount of time and harvest it
IDLETIME = 60*10 # 10 minutes

starttime = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

# if a non-rate-limit or authorisation error occurs log it here....    
ERROR_LOG_FILENAME = 'log/timelineharvester_errors_' + starttime  + '.log'
errorfile = open(ERROR_LOG_FILENAME, 'w')

LOG_FILENAME = 'log/timelineharvester_' + starttime  + '.log'
logfile = open(LOG_FILENAME, 'w')

twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
twitter.verify_credentials()

# get initail rate status
rate_limit_status = twitter.get_application_rate_limit_status(resources = ['friends', 'followers', 'statuses', 'application'])


def run_scraper():
    global rate_limit_status
    
    while True:
    
        if rate_limit_status['resources']['statuses']['/statuses/user_timeline']['remaining'] > 0:
            print "timeline calls"
            # decrement for each call  
        else:
            wait = max(rate_limit_status['resources']['statuses']['/statuses/user_timeline']['reset'] - time.time(),0) + 5
            print "out of calls waiting " + str(wait) + " seconds"            
            time.sleep(wait)
        
        if rate_limit_status['resources']['application']['/application/rate_limit_status']['remaining'] > 0:
            rate_limit_status = twitter.get_application_rate_limit_status(resources = ['friends', 'followers', 'statuses', 'application'])
        else:
            wait = rate_limit_status['resources']['application']['/application/rate_limit_status']['reset'] - time.time() + 5
            time.sleep(wait)            
            rate_limit_status = twitter.get_application_rate_limit_status(resources = ['friends', 'followers', 'statuses', 'application'])




def scrape_poi_data():
    while True:
            # print("selecting next person of interest...")
            # selects on the basis of choosing the one that hasn't been updated in a long time.            
            # don't waste time/twitter calls checking if it hasn't been long enough
            try:
                nextpoi = poi.find({'poi_classification': { '$lt': TIMELINE_POI_CLASS_THRESHOLD}, 'timeline_auth_error_flag':False}, sort=[('datetime_last_timeline_scrape',1)]).limit( 1 )[0]     
                next_harvest_due_at = nextpoi['datetime_last_timeline_scrape'] +  MIN_RESOLUTION
                if next_harvest_due_at > datetime.datetime.now():
                    print "no user due to be scraped"
                    # it wont wait till this poi is due to check again, as new poi might be added to the db before that.
                    # set this to about ten minutes.
                    time.sleep(IDLETIME)
                else:
                    get_user_timeline(nextpoi['id'])
                    
            except Exception, e:
                error = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + "ERROR" + "\t" + "get_user_timelines()\t" + str(e.__class__) +"\t"+ str(e) + "Non rate-limit exception encountered. Sleeping for " + str(ON_EXCEPTION_WAIT) + " before retrying\n" 
                print error            
                errorfile.write(error)
                errorfile.flush()
                time.sleep(ON_EXCEPTION_WAIT)
                pass

scrape_poi_data()