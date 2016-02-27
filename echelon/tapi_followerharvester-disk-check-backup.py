# -*- coding: utf-8 -*-
"""
Created on Tue Jun 23 11:31:14 2015

@author: brendan
"""

import pymongo
from twython import Twython, TwythonRateLimitError, TwythonAuthError, TwythonError
# import urllib
import datetime
import time
import re
import subprocess


MONGOURL = 'localhost'
MONGOUSER =  'harold'
DBPASSWD = 'AcKerTalksMaChine'
DBNAME = 'echelon'
MONGOAUTH = 'mongodb://' + MONGOUSER + ':' + DBPASSWD + '@' + MONGOURL + '/' + DBNAME
POI_COL = 'poi'
EDGES_COL = 'followfriendedges'

try:
    conn = pymongo.MongoClient(MONGOAUTH)
    db = conn[DBNAME]
    
    poi = db[POI_COL]
    print  MONGOUSER +" connected to " + DBNAME  + "." + POI_COL
    poi.create_index([("id", pymongo.DESCENDING)], unique=True)
    print "index created on " + POI_COL + " by id"            

    edges = db[EDGES_COL]
    print  MONGOUSER +" connected to " + DBNAME  + "." + EDGES_COL
    edges.create_index([("id0", pymongo.ASCENDING), ("id1", pymongo.ASCENDING), ("relationship", pymongo.ASCENDING)])
    print "network unique index created on v0,v1,relationship"


except Exception:
    print MONGOUSER +" FAILED to connect to " + DBNAME
    exit()

APP_KEY    = 'Mfm5oNdGSPMvwhZcB8N4MlsL8'
APP_SECRET = 'C0rbmJP0uKbuF6xcT6aR5vFOV9fS4L1965TKOH97pSqj3NJ1mP'
OAUTH_TOKEN        = '3034707280-wFGQAF4FGBviaiSguCUdeG36NIQG1uh8qqXTC1G'
OAUTH_TOKEN_SECRET = 'HUWMfHKyPShE6nH5WXlI26izoQjNtV3US3mNpND1F9qrO'

timeline_twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
timeline_twitter.verify_credentials()

GET_USER_TIMELINE_COUNT = 200
ON_EXCEPTION_WAIT = 60*16
AUTH_ERROR_WAIT = 10
# don't scrape a user more than once every day.
MIN_RESOLUTION = datetime.timedelta(seconds=1*604800)
# if no poi are due to be harvested wait this long..
# the logic being that if you dynamically add new poi it will spot the new poi in this amount of time and harvest it
IDLETIME = 60*10 # 10 minutes

TIMELINE_POI_CLASS_THRESHOLD = 1

#user_id = 2734355331
#user_id = 535436903
#user_id = 1452532201

# globals to hold the remining calls before waiting
friendcall_remaining = 0
friendcall_reset = ON_EXCEPTION_WAIT 
followercall_remaining = 0
followercall_reset = ON_EXCEPTION_WAIT 

# on program initialisation get current rate info
while True: 
    try:
        rate_limit_status = timeline_twitter.get_application_rate_limit_status(resources = ['followers', 'friends', 'application'])
        friendcall_reset  = float(rate_limit_status['resources']['friends']['/friends/ids']['reset'])
        friendcall_remaining = int(rate_limit_status['resources']['friends']['/friends/ids']['remaining'])   
        followercall_remaining = int(rate_limit_status['resources']['followers']['/followers/ids']['remaining'])
        followercall_reset = float(rate_limit_status['resources']['followers']['/followers/ids']['reset'])
        print "friend calls reset at " + str(friendcall_reset)
        print "friend calls remaining " +str(friendcall_remaining)
        print "echelon calls reset at " + str(followercall_reset)
        print "echelon calls remaining " +str(followercall_remaining)
        break
    except TwythonError, e:
        error = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + "TWYTHONERROR getting rate-limit-status\t" + str(e.__class__) +"\t" + str(e) + " Non rate-limit exception encountered. Sleeping for " + str(ON_EXCEPTION_WAIT) + " before retrying\n" 
        print error            
        print "waiting for " + str(ON_EXCEPTION_WAIT)+ " seconds"
        time.sleep(ON_EXCEPTION_WAIT)


def  get_user_followers(userid, maxfollowers=5000):

    global edges
    global followercall_remaining
    global followercall_reset
    global friendcall_remaining
    global friendcall_reset    
    
    next_cursor = -1
    while next_cursor != 0:   
        try:
            if followercall_remaining <= 1:
                wait = max(followercall_reset - time.time(), 0) + 15 # addding 15 second pad     
                #print "first user call: if user_timeline remaining <= 1; waiting " +str(wait) + " seconds for reset"        
                #print datetime.datetime.now().time()            
                time.sleep(wait)      
            
            response =  timeline_twitter.get_followers_ids(user_id=userid, count=maxfollowers, cursor = next_cursor)

	    #print "got response: "	
            if timeline_twitter.get_lastfunction_header('x-rate-limit-reset') is not None:
                followercall_reset  = float(timeline_twitter.get_lastfunction_header('x-rate-limit-reset'))
                followercall_remaining = int(timeline_twitter.get_lastfunction_header('x-rate-limit-remaining'))
            else:
                print "twitter.get_lastfunction_header is None!! Waiting on exception"
                time.sleep(ON_EXCEPTION_WAIT)            
            
            # response = twitter.get_friends_ids(user_id=userid, count=maxfollowers, cursor = next_cursor)
            # store_followers(response['ids'])
            #print response['next_cursor']
	    #print response['ids']

            next_cursor = response['next_cursor']        
            
            for follower in response['ids']:
            # print echelon['screen_name'] +"\t"+ echelon['description'].encode('utf-8').replace('\n', ' ')
                edge = {}
                edge['id0'] = userid
                # edge['screen_name_0'] = 
                edge['id1'] = follower
                # edge['screen_name_1'] = 
                edge['relationship'] = 'echelon'
                # edge['relationship'] = 'friend'
                # this is an observation we can merge observations into weighted and time period later.
                edge['last-date'] = datetime.datetime.now()
                edge['first-date'] = datetime.datetime.now()

                # N/A don;t have a status if its a echelon lookup
                # a copy of the status that established it: this will contain all that is needed for export to NodeXL or otherwise.
                # edge['status'] = 
                try:
                    edges.insert(edge)
                except pymongo.errors.DuplicateKeyError:
                    edges.update({ 'id0': edge['id0'], 'id1': edge['id1'] , 'relationship': edge['relationship']}, {'$set':{'last-date':edge['last-date']}})

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
                        rate_limit_status = timeline_twitter.get_application_rate_limit_status(resources = ['followers', 'friends', 'application'])
                        print "rate_limit_status returned..."                                                
                        followercall_remaining = int(rate_limit_status['resources']['followers']['/followers/ids']['remaining'])
                        followercall_reset = float(rate_limit_status['resources']['followers']['/followers/ids']['reset'])        
                        print "rate_limit_status: echelon reset at " + str(followercall_reset)
                        print "rate_limit_status: echelon remaining = " + str(followercall_remaining)
                        break
                    except TwythonError, e:
                        error = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + "TWYTHONERROR getting rate_limit_status\t" + str(e.__class__) +"\t" + str(e) + " Non rate-limit exception encountered. Sleeping for " + str(ON_EXCEPTION_WAIT) + " before retrying\n" 
                        print error            
                        print "waiting for " + str(ON_EXCEPTION_WAIT)+ " seconds"
                        time.sleep(ON_EXCEPTION_WAIT)
        
        except TwythonAuthError, e:
            # most likely this is due to a private user, so its best to give up.
            poi.update({'id':userid},{'$set':{"datetime_last_follower_scrape": datetime.datetime.now(), 'follower_auth_error_flag':True}}, upsert=False)            
            error = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + "AUTHERROR\t get_user_follower(" + str(userid) + ")\t" + str(e.__class__) +"\t" + str(e) + "\n"
            print error
            print "setting auth error flag true; waiting for: " +  str(AUTH_ERROR_WAIT) + " to not wind up twitter :)"
            time.sleep(AUTH_ERROR_WAIT)
            # this will break out of the while True that is getting the usertimeline
            # it should go on to the next user....        
            return False
        except TwythonError, e:
            pattern = re.compile('\s+404\s+', re.IGNORECASE)
            match = pattern.search(str(e))
            if match:
                error = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + "TWYTHONERROR\t get_user_follower(" + str(userid) + ")\t" + str(e.__class__) +"\t" + str(e) + " Non rate-limit exception encountered\n" 
                print error            
                wait = 60
                print "setting auth error flag true; waiting: " +  str(wait)
                poi.update({'id':userid},{'$set':{"datetime_last_follower_scrape": datetime.datetime.now(), 'follower_auth_error_flag':True}}, upsert=False)
                time.sleep(wait)
                # this will break out of the while True that is getting the usertimeline
                # it should go on to the next user....        
                return False
            else:                
                error = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + "TWYTHONERROR\t" + str(e.__class__) +"\t" + str(e) + " Non rate-limit exception encountered. Sleeping for " + str(ON_EXCEPTION_WAIT) + " before retrying\n" 
                print error            
                time.sleep(ON_EXCEPTION_WAIT)
        except Exception, e:
            error = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + "ERROR\t get_user_follower(" + str(userid) + ")\t" + str(e.__class__) +"\t" + str(e) + " Non rate-limit exception encountered\n" 
            print error
            time.sleep(ON_EXCEPTION_WAIT)
            print "Program EXITING"
            exit()

    print "getting friends"

    next_cursor = -1
    while next_cursor != 0:   
        try:
            if friendcall_remaining <= 1:
                wait = max(friendcall_reset - time.time(), 0) + 15 # addding 15 second pad     
                #print "first user call: if user_timeline remaining <= 1; waiting " +str(wait) + " seconds for reset"        
                #print datetime.datetime.now().time()            
                time.sleep(wait)      
            
            response =  timeline_twitter.get_friends_ids(user_id=userid, count=maxfollowers, cursor = next_cursor)

	    if timeline_twitter.get_lastfunction_header('x-rate-limit-reset') is not None:
                friendcall_reset  = float(timeline_twitter.get_lastfunction_header('x-rate-limit-reset'))
                friendcall_remaining = int(timeline_twitter.get_lastfunction_header('x-rate-limit-remaining'))
            else:
                print "twitter.get_lastfunction_header is None!! Waiting on exception"
                time.sleep(ON_EXCEPTION_WAIT)      

            # response = twitter.get_friends_ids(user_id=userid, count=maxfollowers, cursor = next_cursor)
            # store_followers(response['ids'])

            next_cursor = response['next_cursor']                
            
            for follower in response['ids']:
            # print echelon['screen_name'] +"\t"+ echelon['description'].encode('utf-8').replace('\n', ' ')
                edge = {}
                edge['id0'] = userid
                # edge['screen_name_0'] = 
                edge['id1'] = follower
                # edge['screen_name_1'] = 
                # edge['relationship'] = 'echelon'
                edge['relationship'] = 'friend'
                # this is an observation we can merge observations into weighted and time period later.
                edge['last-date'] = datetime.datetime.now()
                edge['first-date'] = datetime.datetime.now()

                # N/A don;t have a status if its a echelon lookup
                # a copy of the status that established it: this will contain all that is needed for export to NodeXL or otherwise.
                # edge['status'] = 
                try:
                    edges.insert(edge)
                except pymongo.errors.DuplicateKeyError:
                    edges.update({ 'id0': edge['id0'], 'id1': edge['id1'] , 'relationship': edge['relationship']}, {'$set':{'last-date':edge['last-date']}})

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
                        rate_limit_status = timeline_twitter.get_application_rate_limit_status(resources = ['followers', 'friends', 'application'])
                        print "rate_limit_status returned..."   
                        friendcall_reset  = float(rate_limit_status['resources']['friends']['/friends/ids']['reset'])
                        friendcall_remaining = int(rate_limit_status['resources']['friends']['/friends/ids']['remaining'])                                                    
                        print "rate_limit_status: friend reset at " + str(friendcall_reset)
                        print "rate_limit_status: friend remaining = " + str(friendcall_remaining)
                        break
                    except TwythonError, e:
                        error = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + "TWYTHONERROR getting rate_limit_status\t" + str(e.__class__) +"\t" + str(e) + " Non rate-limit exception encountered. Sleeping for " + str(ON_EXCEPTION_WAIT) + " before retrying\n" 
                        print error            
                        print "waiting for " + str(ON_EXCEPTION_WAIT)+ " seconds"
                        time.sleep(ON_EXCEPTION_WAIT)
        
        except TwythonAuthError, e:
            # most likely this is due to a private user, so its best to give up.
            poi.update({'id':userid},{'$set':{"datetime_last_follower_scrape": datetime.datetime.now(), 'follower_auth_error_flag':True}}, upsert=False)            
            error = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + "AUTHERROR\t get_user_friends(" + str(userid) + ")\t" + str(e.__class__) +"\t" + str(e) + "\n"
            print error
            print "setting auth error flag true; waiting for: " +  str(AUTH_ERROR_WAIT) + " to not wind up twitter :)"
            time.sleep(AUTH_ERROR_WAIT)
            # this will break out of the while True that is getting the usertimeline
            # it should go on to the next user....        
            return False
        except TwythonError, e:
            pattern = re.compile('\s+404\s+', re.IGNORECASE)
            match = pattern.search(str(e))
            if match:
                error = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + "TWYTHONERROR\t get_user_friends(" + str(userid) + ")\t" + str(e.__class__) +"\t" + str(e) + " Non rate-limit exception encountered\n" 
                print error            
                wait = 60
                print "setting auth error flag true; waiting: " +  str(wait)
                poi.update({'id':userid},{'$set':{"datetime_last_follower_scrape": datetime.datetime.now(), 'follower_auth_error_flag':True}}, upsert=False)
                time.sleep(wait)
                # this will break out of the while True that is getting the usertimeline
                # it should go on to the next user....        
                return False
            else:                
                error = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + "TWYTHONERROR\t" + str(e.__class__) +"\t" + str(e) + " Non rate-limit exception encountered. Sleeping for " + str(ON_EXCEPTION_WAIT) + " before retrying\n" 
                print error            
                time.sleep(ON_EXCEPTION_WAIT)
        except Exception, e:
            error = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + "ERROR\t get_user_friends(" + str(userid) + ")\t" + str(e.__class__) +"\t" + str(e) + " Non rate-limit exception encountered\n" 
            print error
            print "Program EXITING"
            exit()
    
    print "got friends"
    try:
        poi.update({'id':userid},{'$set':{"datetime_last_follower_scrape": datetime.datetime.now(), 'follower_auth_error_flag':False}}, upsert=False)
    except Exception, e:
        print "Exception occured updating poi scrape time"
	pass
    
    return True

def get_disk_utilisation(filename = "disk-space-check.file"):
        df = subprocess.Popen(["df", filename], stdout=subprocess.PIPE)
        output = df.communicate()[0]
        device, size, used, available, percent, mountpoint = output.split("\n")[1].split()
        percent = float(percent[:-1])

def check_disk_space_and_wait(maxpercent=90, sleeptime=60):
    percent = get_disk_utilisation()
    while percent > maxpercent:
        print "Disk utilisation ("+ str(percent) +"%) is above " + str(maxpercent) + "% waiting till it is reduced"
        time.sleep(sleeptime)           
        percent = get_disk_utilisation()


def get_user_followeredges():
        while True:
            # print("selecting next person of interest...")
            # selects on the basis of choosing the one that hasn't been updated in a long time.            
            # don't waste time/twitter calls checking if it hasn't been long enough
            try:
                nextpoi = poi.find({'poi_classification': { '$lt': TIMELINE_POI_CLASS_THRESHOLD}, 'follower_auth_error_flag':False}, sort=[('datetime_last_follower_scrape',1)]).limit( 1 )[0]     
                next_harvest_due_at = nextpoi['datetime_last_follower_scrape'] +  MIN_RESOLUTION
                if next_harvest_due_at > datetime.datetime.now():
                    print "no user due to be scraped"
                    # it wont wait till this poi is due to check again, as new poi might be added to the db before that.
                    # set this to about ten minutes.
                    time.sleep(IDLETIME)
                else:
                    print "getting friend/follow	er edges of: " + str(nextpoi['id'])
                    get_user_followers(nextpoi['id'])
                    # wait a few seconds
                    time.sleep(3)
                    # db.command("collstats", EDGES_COL)
                    check_disk_space_and_wait()
                    
            except Exception, e:
                error = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + "ERROR" + "\t" + "get_user_followeredges()\t" + str(e.__class__) +"\t"+ str(e) + "Non rate-limit exception encountered. Sleeping for " + str(ON_EXCEPTION_WAIT) + " before retrying\n" 
                print error            
#                errorfile.write(error)
#                errorfile.flush()
                time.sleep(ON_EXCEPTION_WAIT)
                pass

print "program main"
get_user_followeredges()
# get_user_timeline(user_id)
exit()
