y# -*- coding: utf-8 -*-
"""
Created on Mon Jul 13 20:16:48 2015

This parses the tweets in the timelines db for mentions/replies/retweets 
and creates edges in the mrredges collection.

@author: brendan
"""

import pymongo
import datetime

MONGOURL = 'localhost'
MONGOUSER =  'harold'
DBPASSWD = 'AcKerTalksMaChine'
DBNAME = 'echelon'
MONGOAUTH = 'mongodb://' + MONGOUSER + ':' + DBPASSWD + '@' + MONGOURL + '/' + DBNAME
POI_COL = 'poi'
TIMELINES_COL = 'timelines'
MRR_COL = 'mrredges'

try:
    conn = pymongo.MongoClient(MONGOAUTH)
    db = conn[DBNAME]
    
    poi = db[POI_COL]
    print  MONGOUSER +" connected to " + DBNAME  + "." + POI_COL

    timelines = db[TIMELINES_COL]
    print  MONGOUSER +" connected to " + DBNAME  + "." + TIMELINES_COL

    mrredges = db[MRR_COL]
    print  MONGOUSER +" connected to " + DBNAME  + "." + MRR_COL
    mrredges.create_index([("id0", pymongo.ASCENDING), ("id1", pymongo.ASCENDING), ("relationship", pymongo.ASCENDING), ("statusid", pymongo.ASCENDING)], unique=True)
    print "network unique index created on v0,v1,relationship"

except Exception:
    print MONGOUSER +" FAILED to connect to " + DBNAME
    exit()


def add_tweet_edge(userid, createdat, statusid):
    edge = {}
    edge['id0'] = userid
    # edge['screen_name_0'] = 
    edge['id1'] = userid
    # edge['screen_name_1'] = 
    edge['relationship'] = 'tweet'
    # edge['relationship'] = 'friend'
    # this is an observation we can merge observations into weighted and time period later.
    edge['last-date'] = createdat
    edge['first-date'] = createdat
    edge['statusid'] = statusid
    
    #print 'tweet\t' + str(userid) +"\t"+ str(createdat) +"\t"+ str(statusid)
    
    try:
        mrredges.insert(edge)
    except pymongo.errors.DuplicateKeyError:
        pass
        #print "forming tweet edge Duplicate Key ERROR! this shouldn't happen..."
        #print 'tweet\t' + str(userid) +"\t"+ str(createdat) +"\t"+ str(statusid)
    
def add_reply_edge(userid, replied_to, createdat, statusid):
    edge = {}
    edge['id0'] = userid
    # edge['screen_name_0'] = 
    edge['id1'] = replied_to
    # edge['screen_name_1'] = 
    edge['relationship'] = 'reply-to'
    # edge['relationship'] = 'friend'
    # this is an observation we can merge observations into weighted and time period later.
    edge['last-date'] = createdat
    edge['first-date'] = createdat
    edge['statusid'] = statusid
    
    #print 'reply-to\t' + str(userid) +"\t"+ str(replied_to) +"\t"+ str(createdat) +"\t"+ str(statusid)    
    
    try:
        mrredges.insert(edge)
    except pymongo.errors.DuplicateKeyError:
        pass        
        #print "forming reply edge Duplicate Key ERROR! this shouldn't happen..."
        #print 'reply-to\t' + str(userid) +"\t"+ str(replied_to) +"\t"+ str(createdat) +"\t"+ str(statusid)    

def add_mentions_edge(userid, mentioned, createdat, statusid):
    edge = {}
    edge['id0'] = userid
    # edge['screen_name_0'] = 
    edge['id1'] = mentioned
    # edge['screen_name_1'] = 
    edge['relationship'] = 'mentioned'
    # edge['relationship'] = 'friend'
    # this is an observation we can merge observations into weighted and time period later.
    edge['last-date'] = createdat
    edge['first-date'] = createdat
    edge['statusid'] = statusid

    #print 'mentions\t' + str(userid) +"\t"+ str(mentioned) +"\t"+ str(createdat) +"\t"+ str(statusid)    
    
    try:
        mrredges.insert(edge)
    except pymongo.errors.DuplicateKeyError:
        pass
        #print "forming mentions edge Duplicate Key ERROR! this shouldn't happen..."
        #print 'mentions\t' + str(userid) +"\t"+ str(mentioned) +"\t"+ str(createdat) +"\t"+ str(statusid)
        

def add_retweet_edge(userid, retweeted, createdat, statusid):
    edge = {}
    edge['id0'] = userid
    # edge['screen_name_0'] = 
    edge['id1'] = retweeted
    # edge['screen_name_1'] = 
    edge['relationship'] = 'retweet'
    # edge['relationship'] = 'friend'
    # this is an observation we can merge observations into weighted and time period later.
    edge['last-date'] = createdat
    edge['first-date'] = createdat
    edge['statusid'] = statusid
    #print 'retweet\t' + str(userid) +"\t"+ str(retweeted) +"\t"+ str(createdat) +"\t"+ str(statusid)
    
    try:
        mrredges.insert(edge)
    except pymongo.errors.DuplicateKeyError:
        pass
        #print "forming retweet edge Duplicate Key ERROR! this shouldn't happen..."
        #print 'retweet\t' + str(userid) +"\t"+ str(retweeted) +"\t"+ str(createdat) +"\t"+ str(statusid)
        #exit()

#progcounter = 0

# set every poi to have not been analysed.
poi.update({},{'$set':{"net_anal.mrrmined": False}}, multi=True)

while True:

    count = poi.find({'timeline_auth_error_flag':False, "net_anal.mrrmined": False}).count()	
    if count == 0:
        break
    else:
	print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") +"\t"+ str(count) + " remaining"
	
    for user in poi.find({'timeline_auth_error_flag':False, "net_anal.mrrmined": False}).limit(500):
        #progcounter += 1
        #if progcounter%1000 == 0:
        #    print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + str(progcounter)
            
        for tweet in timelines.find({'user.id': user['id']}):
            # parse the tweet for mrr edges:
            
            #tweet['text']= tweet['text'].encode('utf-8','ignore')
            #tweet['text'] = tweet['text'].replace('\n', ' ')
            #print tweet['text']
            # if it doesn't mention or retweet or reply...
            if len(tweet['entities']['user_mentions']) < 1:
                add_tweet_edge(tweet['user']['id'], tweet['created_at'], tweet['id'])
                
            else:
                for mention in tweet['entities']['user_mentions']:
                    if ('in_reply_to_user_id' in tweet) and (mention['id'] == tweet['in_reply_to_user_id']):
                        add_reply_edge(tweet['user']['id'], tweet['in_reply_to_user_id'], tweet['created_at'], tweet['id'])
                       
                    elif ('retweeted_status' in tweet) and (mention['id'] == tweet['retweeted_status']['user']['id']):
                        add_retweet_edge(tweet['user']['id'], tweet['retweeted_status']['user']['id'], tweet['created_at'], tweet['id'])
                    else:
                        add_mentions_edge(tweet['user']['id'], mention['id'], tweet['created_at'], tweet['id'])
                        
                
        poi.update({'id':user['id']},{'$set':{"net_anal.mrrmined": True}})    
                
                
            
