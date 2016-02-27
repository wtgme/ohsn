# -*- coding: utf-8 -*-
"""
Created on Tue Jun 23 11:31:14 2015

@author: brendan
"""

#import pymongo
from twython import Twython, TwythonRateLimitError, TwythonAuthError, TwythonError
#import urllib
import datetime
import time
import re

APP_KEY    = 'Mfm5oNdGSPMvwhZcB8N4MlsL8'
APP_SECRET = 'C0rbmJP0uKbuF6xcT6aR5vFOV9fS4L1965TKOH97pSqj3NJ1mP'
OAUTH_TOKEN        = '3034707280-wFGQAF4FGBviaiSguCUdeG36NIQG1uh8qqXTC1G'
OAUTH_TOKEN_SECRET = 'HUWMfHKyPShE6nH5WXlI26izoQjNtV3US3mNpND1F9qrO'

timeline_twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
timeline_twitter.verify_credentials()

ON_EXCEPTION_WAIT = 60*15


userid = 32343278


while True:
    try:
        rate_limit_status = timeline_twitter.get_application_rate_limit_status(resources = ['statuses', 'application'])
        reset = float(rate_limit_status['resources']['statuses']['/statuses/user_timeline']['reset'])
        remaining = int(rate_limit_status['resources']['statuses']['/statuses/user_timeline']['remaining'])
        print str(reset)
        print str(remaining)
        break
    except TwythonError, e:
        error = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + "TWYTHONERROR getting rate-limit-status\t" + str(e.__class__) +"\t" + str(e) + " Non rate-limit exception encountered. Sleeping for " + str(ON_EXCEPTION_WAIT) + " before retrying\n" 
        print error            
        print "waiting for " + str(ON_EXCEPTION_WAIT)+ " seconds"
        time.sleep(ON_EXCEPTION_WAIT)

while True:       
    try:
        print "if check: remaining = " + str(remaining)
        if remaining <= 1:
            wait = max(reset - time.time(), 0) + 15 # addding 15 second pad     
            print "main:if user_timeline remaining <= 1; waiting " +str(wait) + " seconds for reset"        
            print datetime.datetime.now().time()            
            time.sleep(wait)
            
        params = {'count':20, 'contributor_details':True, 'id':userid, 'since_id':None, 'include_rts':1}           
        print "timeline-call"    
        response = timeline_twitter.get_user_timeline(**params)
        reset = float(timeline_twitter.get_lastfunction_header('x-rate-limit-reset'))
        remaining = int(timeline_twitter.get_lastfunction_header('x-rate-limit-remaining'))
        print "main: user_timeline reset at " + str(reset)
        print "main: user_timeline remaining = " + str(remaining)
        # time.sleep(1)
        
        # TODO: if we are upto date break and move on to the next user
    
    except TwythonRateLimitError, e:
        error = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + "TwythonRateLimitError\t" + str(e.__class__) +"\t" + str(e) + "\n" 
        print error
        print "this shouldn't happen if your using the function headers right, unless twitter are playing silly buggers"
#        reset = twitter.get_lastfunction_header('x-rate-limit-reset')
#        remaining = twitter.get_lastfunction_header('x-rate-limit-remaining')
        # loop until you can get a valid rate-limit-status               
        while True:
            try:               
                print "getting rate_limit_status..."
                rate_limit_status = timeline_twitter.get_application_rate_limit_status(resources = ['statuses', 'application'])
                print "rate_limit_status returned..."
                reset = float(rate_limit_status['resources']['statuses']['/statuses/user_timeline']['reset'])
                remaining = int(rate_limit_status['resources']['statuses']['/statuses/user_timeline']['remaining'])
                print "rate_limit_status: user_timeline reset at " + str(reset)
                print "rate_limit_status: user_timeline remaining = " + str(remaining)
                break
            except TwythonError, e:
                error = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + "TWYTHONERROR getting rate_limit_status\t" + str(e.__class__) +"\t" + str(e) + " Non rate-limit exception encountered. Sleeping for " + str(ON_EXCEPTION_WAIT) + " before retrying\n" 
                print error            
                print "waiting for " + str(ON_EXCEPTION_WAIT)+ " seconds"
                time.sleep(ON_EXCEPTION_WAIT)

    except TwythonAuthError, e:
        # most likely this is due to a private user, so its best to give up.
        # TODO poi.update({'id':userid},{'$set':{"datetime_last_timeline_scrape": datetime.datetime.now(), 'timeline_auth_error_flag':True}}, upsert=False)
        # poi.update({'id':user_id},{'$set':{"timeline_auth_error_flag": True}}, upsert=False)
        error = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + "AUTHERROR\t get_user_timeline(" + str(userid) + ")\t" + str(e.__class__) +"\t" + str(e) + "\n"
        print error
        wait = 30
        print "setting auth error flag true; waiting for: " +  str(wait) + " to not wind up twitter :)"
        time.sleep(wait)
        # this will break out of the while True that is getting the usertimeline
        # it should go on to the next user....        
        break
                
    except TwythonError, e:
        pattern = re.compile('\s+404\s+', re.IGNORECASE)
        match = pattern.search(str(e))
        if match:
            error = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + "TWYTHONERROR\t get_user_timeline(" + str(userid) + ")\t" + str(e.__class__) +"\t" + str(e) + " Non rate-limit exception encountered\n" 
            print error            
            wait = 60
            print "setting auth error flag true; waiting: " +  str(wait)
            # TODO poi.update({'id':userid},{'$set':{"datetime_last_timeline_scrape": datetime.datetime.now(), 'timeline_auth_error_flag':True}}, upsert=False)
            time.sleep(wait)
            # this will break out of the while True that is getting the usertimeline
            # it should go on to the next user....        
            break
        else:                
            error = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + "TWYTHONERROR\t" + str(e.__class__) +"\t" + str(e) + " Non rate-limit exception encountered. Sleeping for " + str(ON_EXCEPTION_WAIT) + " before retrying\n" 
            print error            
            time.sleep(ON_EXCEPTION_WAIT)
    except Exception, e:
        error = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + "ERROR\t get_user_timeline(" + str(userid) + ")\t" + str(e.__class__) +"\t" + str(e) + " Non rate-limit exception encountered\n" 
        print error
        print "EXITING"
        exit()
        
exit()

#status = twitter.get_application_rate_limit_status(resources = ['friends', 'followers', 'statuses', 'application'])
## print status
#print "rate-limit-call"
#print twitter.get_lastfunction_header('x-rate-limit-reset')
#print twitter.get_lastfunction_header('x-rate-limit-remaining')

response = timeline_twitter.get_followers_ids(user_id=userid, count=10, cursor = -1)
print "followers-call"
print timeline_twitter.get_lastfunction_header('x-rate-limit-reset')
print timeline_twitter.get_lastfunction_header('x-rate-limit-remaining')

#status = twitter.get_application_rate_limit_status(resources = ['friends', 'followers', 'statuses', 'application'])
#print "rate-limit-call"
#print twitter.get_lastfunction_header('x-rate-limit-reset')
#print twitter.get_lastfunction_header('x-rate-limit-remaining')

response = timeline_twitter.get_friends_ids(user_id=userid, count=10, cursor = -1)
print "friends-call"
print timeline_twitter.get_lastfunction_header('x-rate-limit-reset')
print timeline_twitter.get_lastfunction_header('x-rate-limit-remaining')

#status = twitter.get_application_rate_limit_status(resources = ['friends', 'followers', 'statuses', 'application'])
#print "rate-limit-call"
#print twitter.get_lastfunction_header('x-rate-limit-reset')
#print twitter.get_lastfunction_header('x-rate-limit-remaining')

## doing the get_user_timeline() call reduces this by one:
#
#resources.statuses
#
#u'/statuses/user_timeline': {u'reset': 1435060035, u'limit': 180, u'remaining': 178}
#
#resources.followers.
#
#u'/followers/ids': {u'reset': 1435060106, u'limit': 15, u'remaining': 12}}

# for friends this is decremented

# u'/friends/ids'

#
#{u'rate_limit_context': {u'access_token': u'3034707280-wFGQAF4FGBviaiSguCUdeG36NIQG1uh8qqXTC1G'}, u'resources': {u'application': {u'/application/rate_limit_status': {u'reset': 1435060034, u'limit': 180, u'remaining': 172}}, u'friends': {u'/friends/list': {u'reset': 1435060782, u'limit': 15, u'remaining': 15}, u'/friends/following/ids': {u'reset': 1435060782, u'limit': 15, u'remaining': 15}, u'/friends/ids': {u'reset': 1435060782, u'limit': 15, u'remaining': 15}, u'/friends/following/list': {u'reset': 1435060782, u'limit': 15, u'remaining': 15}}, u'followers': {u'/followers/list': {u'reset': 1435060782, u'limit': 15, u'remaining': 15}, u'/followers/ids': {u'reset': 1435060106, u'limit': 15, u'remaining': 13}}, u'statuses': {u'/statuses/retweets_of_me': {u'reset': 1435060782, u'limit': 15, u'remaining': 15}, u'/statuses/retweeters/ids': {u'reset': 1435060782, u'limit': 15, u'remaining': 15}, u'/statuses/mentions_timeline': {u'reset': 1435060782, u'limit': 15, u'remaining': 15}, u'/statuses/user_timeline': {u'reset': 1435060035, u'limit': 180, u'remaining': 177}, u'/statuses/lookup': {u'reset': 1435060782, u'limit': 180, u'remaining': 180}, u'/statuses/oembed': {u'reset': 1435060782, u'limit': 180, u'remaining': 180}, u'/statuses/show/:id': {u'reset': 1435060782, u'limit': 180, u'remaining': 180}, u'/statuses/friends': {u'reset': 1435060782, u'limit': 15, u'remaining': 15}, u'/statuses/home_timeline': {u'reset': 1435060782, u'limit': 15, u'remaining': 15}, u'/statuses/retweets/:id': {u'reset': 1435060782, u'limit': 60, u'remaining': 60}}}}
#POST TIMELINE
#{u'rate_limit_context': {u'access_token': u'3034707280-wFGQAF4FGBviaiSguCUdeG36NIQG1uh8qqXTC1G'}, u'resources': {u'application': {u'/application/rate_limit_status': {u'reset': 1435060034, u'limit': 180, u'remaining': 171}}, u'friends': {u'/friends/list': {u'reset': 1435060782, u'limit': 15, u'remaining': 15}, u'/friends/following/ids': {u'reset': 1435060782, u'limit': 15, u'remaining': 15}, u'/friends/ids': {u'reset': 1435060782, u'limit': 15, u'remaining': 15}, u'/friends/following/list': {u'reset': 1435060782, u'limit': 15, u'remaining': 15}}, u'followers': {u'/followers/list': {u'reset': 1435060782, u'limit': 15, u'remaining': 15}, u'/followers/ids': {u'reset': 1435060106, u'limit': 15, u'remaining': 13}}, u'statuses': {u'/statuses/retweets_of_me': {u'reset': 1435060782, u'limit': 15, u'remaining': 15}, u'/statuses/retweeters/ids': {u'reset': 1435060782, u'limit': 15, u'remaining': 15}, u'/statuses/mentions_timeline': {u'reset': 1435060782, u'limit': 15, u'remaining': 15}, u'/statuses/user_timeline': {u'reset': 1435060035, u'limit': 180, u'remaining': 176}, u'/statuses/lookup': {u'reset': 1435060782, u'limit': 180, u'remaining': 180}, u'/statuses/oembed': {u'reset': 1435060782, u'limit': 180, u'remaining': 180}, u'/statuses/show/:id': {u'reset': 1435060782, u'limit': 180, u'remaining': 180}, u'/statuses/friends': {u'reset': 1435060782, u'limit': 15, u'remaining': 15}, u'/statuses/home_timeline': {u'reset': 1435060782, u'limit': 15, u'remaining': 15}, u'/statuses/retweets/:id': {u'reset': 1435060782, u'limit': 60, u'remaining': 60}}}}
#POST FOLLOWER
#{u'rate_limit_context': {u'access_token': u'3034707280-wFGQAF4FGBviaiSguCUdeG36NIQG1uh8qqXTC1G'}, u'resources': {u'application': {u'/application/rate_limit_status': {u'reset': 1435060034, u'limit': 180, u'remaining': 170}}, u'friends': {u'/friends/list': {u'reset': 1435060782, u'limit': 15, u'remaining': 15}, u'/friends/following/ids': {u'reset': 1435060782, u'limit': 15, u'remaining': 15}, u'/friends/ids': {u'reset': 1435060782, u'limit': 15, u'remaining': 15}, u'/friends/following/list': {u'reset': 1435060782, u'limit': 15, u'remaining': 15}}, u'followers': {u'/followers/list': {u'reset': 1435060782, u'limit': 15, u'remaining': 15}, u'/followers/ids': {u'reset': 1435060106, u'limit': 15, u'remaining': 12}}, u'statuses': {u'/statuses/retweets_of_me': {u'reset': 1435060782, u'limit': 15, u'remaining': 15}, u'/statuses/retweeters/ids': {u'reset': 1435060782, u'limit': 15, u'remaining': 15}, u'/statuses/mentions_timeline': {u'reset': 1435060782, u'limit': 15, u'remaining': 15}, u'/statuses/user_timeline': {u'reset': 1435060035, u'limit': 180, u'remaining': 176}, u'/statuses/lookup': {u'reset': 1435060782, u'limit': 180, u'remaining': 180}, u'/statuses/oembed': {u'reset': 1435060782, u'limit': 180, u'remaining': 180}, u'/statuses/show/:id': {u'reset': 1435060782, u'limit': 180, u'remaining': 180}, u'/statuses/friends': {u'reset': 1435060782, u'limit': 15, u'remaining': 15}, u'/statuses/home_timeline': {u'reset': 1435060782, u'limit': 15, u'remaining': 15}, u'/statuses/retweets/:id': {u'reset': 1435060782, u'limit': 60, u'remaining': 60}}}}
#
#
#{u'rate_limit_context': {u'access_token': u'3034707280-wFGQAF4FGBviaiSguCUdeG36NIQG1uh8qqXTC1G'}, u'resources': {u'application': {u'/application/rate_limit_status': {u'reset': 1435061505, u'limit': 180, u'remaining': 179}}, u'friends': {u'/friends/list': {u'reset': 1435061505, u'limit': 15, u'remaining': 15}, u'/friends/following/ids': {u'reset': 1435061505, u'limit': 15, u'remaining': 15}, u'/friends/ids': {u'reset': 1435061505, u'limit': 15, u'remaining': 15}, u'/friends/following/list': {u'reset': 1435061505, u'limit': 15, u'remaining': 15}}, u'followers': {u'/followers/list': {u'reset': 1435061505, u'limit': 15, u'remaining': 15}, u'/followers/ids': {u'reset': 1435061505, u'limit': 15, u'remaining': 15}}, u'statuses': {u'/statuses/retweets_of_me': {u'reset': 1435061505, u'limit': 15, u'remaining': 15}, u'/statuses/retweeters/ids': {u'reset': 1435061505, u'limit': 15, u'remaining': 15}, u'/statuses/mentions_timeline': {u'reset': 1435061505, u'limit': 15, u'remaining': 15}, u'/statuses/user_timeline': {u'reset': 1435061505, u'limit': 180, u'remaining': 180}, u'/statuses/lookup': {u'reset': 1435061505, u'limit': 180, u'remaining': 180}, u'/statuses/oembed': {u'reset': 1435061505, u'limit': 180, u'remaining': 180}, u'/statuses/show/:id': {u'reset': 1435061505, u'limit': 180, u'remaining': 180}, u'/statuses/friends': {u'reset': 1435061505, u'limit': 15, u'remaining': 15}, u'/statuses/home_timeline': {u'reset': 1435061505, u'limit': 15, u'remaining': 15}, u'/statuses/retweets/:id': {u'reset': 1435061505, u'limit': 60, u'remaining': 60}}}}
#{u'rate_limit_context': {u'access_token': u'3034707280-wFGQAF4FGBviaiSguCUdeG36NIQG1uh8qqXTC1G'}, u'resources': {u'application': {u'/application/rate_limit_status': {u'reset': 1435061505, u'limit': 180, u'remaining': 178}}, u'friends': {u'/friends/list': {u'reset': 1435061505, u'limit': 15, u'remaining': 15}, u'/friends/following/ids': {u'reset': 1435061505, u'limit': 15, u'remaining': 15}, u'/friends/ids': {u'reset': 1435061505, u'limit': 15, u'remaining': 15}, u'/friends/following/list': {u'reset': 1435061505, u'limit': 15, u'remaining': 15}}, u'followers': {u'/followers/list': {u'reset': 1435061505, u'limit': 15, u'remaining': 15}, u'/followers/ids': {u'reset': 1435061505, u'limit': 15, u'remaining': 15}}, u'statuses': {u'/statuses/retweets_of_me': {u'reset': 1435061505, u'limit': 15, u'remaining': 15}, u'/statuses/retweeters/ids': {u'reset': 1435061505, u'limit': 15, u'remaining': 15}, u'/statuses/mentions_timeline': {u'reset': 1435061505, u'limit': 15, u'remaining': 15}, u'/statuses/user_timeline': {u'reset': 1435061505, u'limit': 180, u'remaining': 179}, u'/statuses/lookup': {u'reset': 1435061505, u'limit': 180, u'remaining': 180}, u'/statuses/oembed': {u'reset': 1435061505, u'limit': 180, u'remaining': 180}, u'/statuses/show/:id': {u'reset': 1435061505, u'limit': 180, u'remaining': 180}, u'/statuses/friends': {u'reset': 1435061505, u'limit': 15, u'remaining': 15}, u'/statuses/home_timeline': {u'reset': 1435061505, u'limit': 15, u'remaining': 15}, u'/statuses/retweets/:id': {u'reset': 1435061505, u'limit': 60, u'remaining': 60}}}}
#{u'rate_limit_context': {u'access_token': u'3034707280-wFGQAF4FGBviaiSguCUdeG36NIQG1uh8qqXTC1G'}, u'resources': {u'application': {u'/application/rate_limit_status': {u'reset': 1435061505, u'limit': 180, u'remaining': 177}}, u'friends': {u'/friends/list': {u'reset': 1435061506, u'limit': 15, u'remaining': 15}, u'/friends/following/ids': {u'reset': 1435061506, u'limit': 15, u'remaining': 15}, u'/friends/ids': {u'reset': 1435061506, u'limit': 15, u'remaining': 15}, u'/friends/following/list': {u'reset': 1435061506, u'limit': 15, u'remaining': 15}}, u'followers': {u'/followers/list': {u'reset': 1435061506, u'limit': 15, u'remaining': 15}, u'/followers/ids': {u'reset': 1435061506, u'limit': 15, u'remaining': 14}}, u'statuses': {u'/statuses/retweets_of_me': {u'reset': 1435061506, u'limit': 15, u'remaining': 15}, u'/statuses/retweeters/ids': {u'reset': 1435061506, u'limit': 15, u'remaining': 15}, u'/statuses/mentions_timeline': {u'reset': 1435061506, u'limit': 15, u'remaining': 15}, u'/statuses/user_timeline': {u'reset': 1435061505, u'limit': 180, u'remaining': 179}, u'/statuses/lookup': {u'reset': 1435061506, u'limit': 180, u'remaining': 180}, u'/statuses/oembed': {u'reset': 1435061506, u'limit': 180, u'remaining': 180}, u'/statuses/show/:id': {u'reset': 1435061506, u'limit': 180, u'remaining': 180}, u'/statuses/friends': {u'reset': 1435061506, u'limit': 15, u'remaining': 15}, u'/statuses/home_timeline': {u'reset': 1435061506, u'limit': 15, u'remaining': 15}, u'/statuses/retweets/:id': {u'reset': 1435061506, u'limit': 60, u'remaining': 60}}}}
#{u'rate_limit_context': {u'access_token': u'3034707280-wFGQAF4FGBviaiSguCUdeG36NIQG1uh8qqXTC1G'}, u'resources': {u'application': {u'/application/rate_limit_status': {u'reset': 1435061505, u'limit': 180, u'remaining': 176}}, u'friends': {u'/friends/list': {u'reset': 1435061506, u'limit': 15, u'remaining': 15}, u'/friends/following/ids': {u'reset': 1435061506, u'limit': 15, u'remaining': 15}, u'/friends/ids': {u'reset': 1435061506, u'limit': 15, u'remaining': 14}, u'/friends/following/list': {u'reset': 1435061506, u'limit': 15, u'remaining': 15}}, u'followers': {u'/followers/list': {u'reset': 1435061506, u'limit': 15, u'remaining': 15}, u'/followers/ids': {u'reset': 1435061506, u'limit': 15, u'remaining': 14}}, u'statuses': {u'/statuses/retweets_of_me': {u'reset': 1435061506, u'limit': 15, u'remaining': 15}, u'/statuses/retweeters/ids': {u'reset': 1435061506, u'limit': 15, u'remaining': 15}, u'/statuses/mentions_timeline': {u'reset': 1435061506, u'limit': 15, u'remaining': 15}, u'/statuses/user_timeline': {u'reset': 1435061505, u'limit': 180, u'remaining': 179}, u'/statuses/lookup': {u'reset': 1435061506, u'limit': 180, u'remaining': 180}, u'/statuses/oembed': {u'reset': 1435061506, u'limit': 180, u'remaining': 180}, u'/statuses/show/:id': {u'reset': 1435061506, u'limit': 180, u'remaining': 180}, u'/statuses/friends': {u'reset': 1435061506, u'limit': 15, u'remaining': 15}, u'/statuses/home_timeline': {u'reset': 1435061506, u'limit': 15, u'remaining': 15}, u'/statuses/retweets/:id': {u'reset': 1435061506, u'limit': 60, u'remaining': 60}}}}
##
#
#
#
#
#
#
#
#















#
#{u'rate_limit_context': {
#u'access_token': u'3034707280-wFGQAF4FGBviaiSguCUdeG36NIQG1uh8qqXTC1G'
#}, 
#    u'resources': {
#        u'application': {
#            u'/application/rate_limit_status': {u'reset': 1435056848, u'limit': 180, u'remaining': 178}
#        }, 
#        u'friends': {
#            u'/friends/list': {u'reset': 1435057041, u'limit': 15, u'remaining': 15}, 
#            u'/friends/following/ids': {u'reset': 1435057041, u'limit': 15, u'remaining': 15}, 
#            u'/friends/ids': {u'reset': 1435057041, u'limit': 15, u'remaining': 15}, 
#            u'/friends/following/list': {u'reset': 1435057041, u'limit': 15, u'remaining': 15}
#        }
#    }
#}
#
#{u'rate_limit_context': {
#u'access_token': u'3034707280-wFGQAF4FGBviaiSguCUdeG36NIQG1uh8qqXTC1G'
#}, 
#u'resources': {
#    u'application': {
#        u'/application/rate_limit_status': {u'reset': 1435056848, u'limit': 180, u'remaining': 177}
#    }, 
#    u'statuses': {
#         u'/statuses/retweets_of_me': {u'reset': 1435057265, u'limit': 15, u'remaining': 15}, 
#         u'/statuses/retweeters/ids': {u'reset': 1435057265, u'limit': 15, u'remaining': 15}, 
#         u'/statuses/mentions_timeline': {u'reset': 1435057265, u'limit': 15, u'remaining': 15}, 
#         u'/statuses/user_timeline': {u'reset': 1435057265, u'limit': 180, u'remaining': 180}, 
#         u'/statuses/lookup': {u'reset': 1435057265, u'limit': 180, u'remaining': 180}, 
#         u'/statuses/oembed': {u'reset': 1435057265, u'limit': 180, u'remaining': 180}, 
#         u'/statuses/show/:id': {u'reset': 1435057265, u'limit': 180, u'remaining': 180}, 
#         u'/statuses/friends': {u'reset': 1435057265, u'limit': 15, u'remaining': 15}, 
#         u'/statuses/home_timeline': {u'reset': 1435057265, u'limit': 15, u'remaining': 15}, 
#         u'/statuses/retweets/:id': {u'reset': 1435057265, u'limit': 60, u'remaining': 60}
#        }
#    }
#}