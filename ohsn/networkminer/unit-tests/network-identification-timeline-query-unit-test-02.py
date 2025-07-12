# -*- coding: utf-8 -*-
"""
Created on Thu Jun 04 10:24:15 2015

this one does replies to and mentions...

@author: home
"""


#import ConfigParser
import datetime
import time
#from datetime import timedelta 
from pymongo import Connection
#import numpy as np
#import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
#import pygraphviz as pgv
from collections import Counter


import networkx as nx
 

#config = ConfigParser.ConfigParser()
#config.read('scraper.cfg')
 
# spin up database
#DBNAME = config.get('database', 'name')
#COLLECTION = config.get('database', 'collection')

DBNAME = 'twitter_test'
COLLECTION = 'home_timelines'

print(DBNAME)
print(COLLECTION)

conn = Connection()
db = conn[DBNAME]
tweets = db[COLLECTION]

print("twitter connection and database connection configured")

def makeEdge(v0,v1,rel,created_at):
    return (v0, v1, rel, created_at)

freq = Counter()
userfreq = Counter()
poi_retweet = 0

mentions_count = 0
usermentionsfreq = Counter()
poi_mentions = 0

edges = set()

#edge = makeEdge('drbnev','manos','retweet',datetime.datetime.now())
#
#edges.add(edge)
#
#time.sleep(2)
#
#timenow = datetime.datetime.now()
#
#edge = makeEdge('drbnev','manos','retweet',timenow)
#edges.add(edge)
#edge = makeEdge('drbnev','manos','retweet',timenow)
#edges.add(edge)
#edge = makeEdge('drbnev','manos','mention',timenow)
#edges.add(edge)
#edge = makeEdge('drbnev','markus','mention',timenow)
#edges.add(edge)
#edge = makeEdge('manos','markus','mention',timenow)
#edges.add(edge)

#for edge in edges:
#    print edge

usernames = ['anasecretss', 'needingbones', 'tiinyterry']
#usernames = ['anasecretss']
#usernames = ['needingbones']
#usernames = ['tiinyterry']

for username in usernames:
    results = tweets.find({'user.screen_name': username})
    for result in results:
        # print result['text'].encode('utf-8')
        # print result['retweet_count']
    
        #Is it a reply
        try:
            replyname = result['in_reply_to_screen_name']
            # its a RT using the official button
            edge = makeEdge(result['user']['screen_name'], result['in_reply_to_screen_name'],'reply', result['created_at'])
            edges.add(edge)
            # make an overall count
            freq[result['retweet_count']] += 1
            # make a count for each user retweeted
            userfreq[result['in_reply_to_screen_name']] += 1
            # if its a poi count it....
            if result['in_reply_to_screen_name'] in usernames:
                poi_retweet += 1
        except KeyError:   
            pass
        
        # We can capture manual retweets with mentions...
        # This also captures replies to...
#        try:        
#            for usermention in result['entities']['user_mentions']:
#                if usermention['screen_name'] != replyname:
#                    mentions_count += 1
#                    usermentionsfreq[usermention['screen_name']] += 1                    
#                    edge = makeEdge(result['user']['screen_name'],  usermention['screen_name'], 'mention', result['created_at'])
#                    edges.add(edge)
#                    if usermention['screen_name'] in usernames:
#                        poi_mentions = 0            
#        
#        except KeyError:   
#            pass   
            # usermention['id']
    
    
         #"(RT|via)((?:\b\W*@\w+)+)"
#    
#    OR    
#    
#    if result['retweeted_status']['user']['screen_name'] is not None:
#    
#    poster = 
#    retweeter = result['screen_name']
#        
#    
#    poster = str_extract_all(twit$getText(),"(RT|via)((?:\b\W*@\w+)+)")
#    #remove ':'
#    poster = gsub(":", "", unlist(poster))
#    # name of retweeted user
#    who_post[[i]] = gsub("(RT @|via @)", "", poster, ignore.case=TRUE)
#    # name of retweeting user
#    who_retweet[[i]] = rep(twit$getScreenName(), length(poster))
#    
#    edges
    
#        try:
#            if result['retweeted_status']['user']['screen_name'] is not None:
#
#        except KeyError:   
#            pass

print "REPLY COUNTS"
print userfreq            
print freq
print poi_retweet

#print "Mention COUNTS"
#print mentions_count
#print usermentionsfreq
#print poi_mentions

G=nx.DiGraph()
#A=pgv.AGraph()

for edge in edges:
    G.add_edge(edge[0],edge[1])
    #A.add_edge(edge[0],edge[1])

#A.layout() # layout with default (neato)
#A.draw('simple.png') # draw png

#export so you can use gephi
nx.write_graphml(G,'ed-test-replies-to.graphml')
nx.write_gexf(G, 'ed-test-replies-to.gexf')

# nx.draw_spring(G)
# nx.draw_shell(G)
nx.draw_random(G)

plt.show()