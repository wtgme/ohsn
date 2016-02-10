# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 12:29:37 2015

Initial code purloined from the example at: https://unsupervisedlearning.wordpress.com/

@author: home

Its been modified to collect a users friends and followers

"""

import ConfigParser
import datetime
from datetime import timedelta 
from pymongo import Connection
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt 
 
 
#config = ConfigParser.ConfigParser()
#config.read('scraper.cfg')
 
# spin up database
#DBNAME = config.get('database', 'name')
#COLLECTION = config.get('database', 'collection')

DBNAME = 'twitter_test'
COLLECTION = 'stream'

print(DBNAME)
print(COLLECTION)

conn = Connection()
db = conn[DBNAME]
tweets = db[COLLECTION]

print("twitter connection and database connection configured")

def print_tweets_date_period(start, end):
    results = tweets.find({'created_at': {'$gte': start, '$lt': end}})
    for doc in results:
        print str(doc['created_at']) + "\t" + doc['user']['screen_name'].encode('utf-8') +"\t"+ doc['text'].encode('utf-8').replace('\n', '')    
    print "Total_Printed = " + str(results.count())     
  
# print(tweets.find_one()['created_at'])
def tweet_rate(start, end, rate):
    
    period_start = start
    period_end = period_start + timedelta(minutes=rate)
   
    time = []
    tweet_count = []
         
    while end > period_end:
        time.append(period_start)
        the_count = tweets.find({'created_at': {'$gte': period_start, '$lt': period_end}}).count()    
        # the_count = 0        
        tweet_count.append(the_count)
        # print str(period_start) +"\t"+ str(the_count)
        period_start = period_end
        period_end = period_end + timedelta(minutes=rate)
        
    return (time,tweet_count)


start = datetime.datetime(2015, 6, 3, 15, 30, 0, 0)
end = datetime.datetime(2015, 6, 3, 16, 0, 0, 0)
#
print_tweets_date_period(start, end)

total_tweets = tweets.find().count()
print "TOTAL_TWEETS=" + str(total_tweets)

first_time = tweets.find(None, sort=[('created_at',1)]).limit( 1 )[0]
print "Start=" + str(first_time['created_at'])
last_time = tweets.find(None, sort=[('created_at',-1)]).limit( 1 )[0]
print "Last =" + str(last_time['created_at'])

duration = last_time['created_at'] - first_time['created_at']


duration_seconds = float(duration.days*86400) + duration.seconds
print "Duration (days) = " + str(float(duration_seconds/86400))
rate_second = float(total_tweets/duration_seconds)
rate_day = float(86400*rate_second)
print "rate_day = " + str(rate_day)
total_tweets_in_thirty_days = float(30*rate_day)
print "total tweets_in_30days = " + str(total_tweets_in_thirty_days) 


#use all tweets in the db
rate = 15
start = first_time['created_at']
end = last_time['created_at']

#use a small section
rate = 3
start = datetime.datetime(2015, 6, 3, 15, 30, 0, 0)
end = datetime.datetime(2015, 6, 3, 16, 30, 0, 0)

period_count = tweet_rate(start, end,rate)
#
#print period_count[0]
#print period_count[1]
#
plt.plot_date(x=period_count[0], y=period_count[1], fmt="r-")
plt.title("Tweets returned in " + str(rate) + "minute period")
plt.ylabel("# Tweets")
plt.grid(True)
plt.show()