# -*- coding: utf-8 -*-
"""
Created on Thu May 07 12:32:49 2015

@author: home
"""

#import sys
import re
#import datetime
#import json
#import codecs
#import csv
import ConfigParser
from pymongo import MongoClient
from pymongo import Connection
#from bson.objectid import ObjectId
#from collections import Counter
#import numpy as np
#import matplotlib.mlab as mlab
#import matplotlib.pyplot as plt
#public variables

client =  None
db = None
collection = None

config = ConfigParser.ConfigParser()
config.read('scraper.cfg')

# spin up local database
networkDBNAME = config.get('networkdatabase','name')
edgeCOLLECTION = config.get('networkdatabase','edgecollection')
vertexCOLLECTION = config.get('networkdatabase','vertexcollection')

conn = Connection()
network_db = conn[networkDBNAME]
edge_data = network_db[edgeCOLLECTION]
vertex_data = network_db[vertexCOLLECTION]

#import operator

#Usi this method FIRST in order to establish a connection to a server
def connectToMongoServer(serverAddress):
    try:
        global client
        client = MongoClient(serverAddress)
    except:
        print "error"

#connec to a database
def connectoMongoDatabase(databaseName):
    try:
        global db
        db = client[databaseName]
    except Exception, e:
        print e

#connec to a database
def connectoMongoCollection(collectionName):
    try:
        global collection
        collection = db[collectionName]
    except Exception, e:
        print e

def getvertex(username):
     print "TODO: getvertex(username)"
    # Vertex	Subgraph	Color	Shape	Size	Opacity	Image File	Visibility	Label	Label Fill Color	Label Position	Tooltip	Degree	In-Degree	Out-Degree	Betweenness Centrality	Closeness Centrality	Eigenvector Centrality	PageRank	Clustering Coefficient	Reciprocated Vertex Pair Ratio	Dynamic Filter	Add Your Own Columns Here	Followed	Followers	Tweets	Favorites	Time Zone UTC Offset (Seconds)	Description	Location	Web	Time Zone	Joined Twitter Date (UTC)	Custom Menu Item Text	Custom Menu Item Action	Tweeted Search Term?	Top URLs in Tweet by Count	Top URLs in Tweet by Salience	Top Domains in Tweet by Count	Top Domains in Tweet by Salience	Top Hashtags in Tweet by Count	Top Hashtags in Tweet by Salience	Top Words in Tweet by Count	Top Words in Tweet by Salience	Top Word Pairs in Tweet by Count	Top Word Pairs in Tweet by Salience
    # Vertex	Subgraph	Color	Shape	Size	Opacity	Image File	Visibility	Label	Label Fill Color	Label Position	Tooltip	Add Your Own Columns Here	Followed	Followers	Tweets	Favorites	Time Zone UTC Offset (Seconds)	Description	Location	Web	Time Zone	Joined Twitter Date (UTC)	Custom Menu Item Text	Custom Menu Item Action	Tweeted Search Term?					

def create_basic_edge(tweet):
    print "create_basic_edge"
     # username1, username2, Relationship[Follows, Replies to, Tweet, Mentions], Relationship Date (UTC), Tweet, URLs in Tweet, Domains in Tweet, Hashtags in Tweet, Tweet Date (UTC),	Twitter Page for Tweet, Latitude,	Longitude,	Imported ID, In-Reply-To Tweet ID,
    edge = {}
    # username1 (i)
    edge['user1_name'] = tweet['interaction']['interaction']['author']['username']

    # username2 (j)
    edge['user1_id'] = tweet['interaction']['twitter']['user']['id_str']
#    edge['username2_idstr'] = tweet[]
    # Relationship[Follows, Replies to, Tweet, Mentions]
   
    edge['relationship_date_utc'] = tweet['interaction']['interaction']['created_at']
    edge['tweet'] = tweet['interaction']['twitter']['text']
    edge['tweet_id'] = tweet['interaction']['twitter']['id']
    # language : we really want 'en'
    try:
        edge['language'] = tweet['interaction']['language']['tag']
    except Exception, e :
        print e
        
    try:
        edge['urls_in_tweet'] = tweet['interaction']['links']['normalized_url']
    except Exception, e :
        print e
        
    try:
        edge['domains_in_tweet'] = tweet['interaction']['links']['domain']
    except Exception, e :
        print e
        
    try:
        edge['hashtags_in_tweet'] = tweet['interaction']['twitter']['hashtags']
    except Exception, e :
        print e
        
    edge['tweet_date_utc'] = tweet['interaction']['interaction']['created_at']   
    edge['twitter_page_for_tweet'] = tweet['interaction']['interaction']['link']
   
    try:
        edge['author_location'] = tweet['interaction']['twitter']['user']['location']
    except Exception, e :
        print e
    try:    
        edge['latitude'] = tweet['interaction']['twitter']['geo']['latitude']
        edge['longitude'] = tweet['interaction']['twitter']['geo']['longitude']
    except Exception, e :
        print e
    # imported_id is the tweet id!!!    
    # edge['imported_id'] = tweet['interaction']['twitter']['id']
    try:  
        edge['in_reply_to_tweet_id'] = tweet['interaction']['twitter']['in_reply_to_status_id']
    except Exception, e :
        print e
    try:  
        edge['in_reply_to_screen_name'] =  tweet['interaction']['twitter']['in_reply_to_screen_name']
    except Exception, e :
        print e
    try:  
        edge['in_reply_to_user_id'] =  tweet['interaction']['twitter']['in_reply_to_user_id']
    except Exception, e :
        print e    
    # in-case we need it the other people mentioned at the same time...
    try:  
        edge['mentions_usernames'] = tweet['interaction']['interaction']['mentions']
    except Exception, e :
        print e
    try:  
        edge['mention_ids'] = tweet['interaction']['interaction']['mention_ids']
    except Exception, e :
        print e

    return edge
    
def create_mentions_edge(tweet, username2, username2idstr):
    print "TODO: create_mentions_edge"
    edge = create_basic_edge(tweet)
    edge['relationship'] = "Mentions"
    edge['user2_name'] = username2
    #users can change their username so need to use the id str.
    # This is mangled....
    print "TODO: create_mentions_edge edge['username2_idstr'] =  edge['username2_idstr'] = username2idstr comes from the mentions ids and so is mangled"
    edge['user2_id'] = username2idstr    
    # For now just make a test edge....
    return edge
    
def create_reply_edge(tweet):
    print "TODO: create_reply_edge"
    edge = create_basic_edge(tweet)
    edge['relationship'] = "Replies to"
    edge['user2_name'] = tweet['interaction']['twitter']['in_reply_to_screen_name']
    edge['user2_id'] = tweet['interaction']['twitter']['in_reply_to_user_id']
    # For now just make a test edge....
    return edge
    
def create_tweet_edge(tweet):
    print "TODO: create_tweet_edge()"
    edge = create_basic_edge(tweet)
    edge['relationship'] = "Tweet"
    # its a self connecting edge.
    edge['user2_name'] = tweet['interaction']['interaction']['author']['username']
    # its a self connecting edge.
    edge['user2_id'] = tweet['interaction']['twitter']['user']['id_str']
    # For now just make a test edge....
    return edge
    
def create_retweet_edge(tweet, username2, username2idstr):
    print "TODO: create_retweet_edge()"
    edge = create_basic_edge(tweet)
    edge['relationship'] = "Retweet"
    edge['user2_name'] = username2
    edge['user2_id'] =  username2idstr
    # For now just make a test edge....
    return edge

#def create_follows_edge(username2):
#    print "TODO: create_follows_edge()"
#    edge = create_basic_edge(tweet)
#    edge['relationship'] = "Follows"
#    edge['username2'] = username2
#    # For now just make a test edge....
#    return edge
        
def get_network_from_tweets():
    
    vertexes = set()
    # vertexes.add('joe')

    ## Vertex 1	Vertex 2	Color	Width	Style	Opacity Visibility	Label	Label Text Color	Label Font Size	Reciprocated?	Add Your Own Columns Here	Relationship	Relationship Date (UTC)	Tweet	URLs in Tweet	Domains in Tweet	Hashtags in Tweet	Tweet Date (UTC)	Twitter Page for Tweet	Latitude	Longitude	Imported ID	In-Reply-To Tweet ID
    # username1, username2, Relationship[Follows, Replies to, Tweet, Mentions], Relationship Date (UTC), Tweet, URLs in Tweet, Domains in Tweet, Hashtags in Tweet, Tweet Date (UTC),	Twitter Page for Tweet, Latitude,	Longitude,	Imported ID, In-Reply-To Tweet ID,

    for tweet in collection.find().limit(100): 
        
            #Hmmmm.... a tweet can create many relationships...
            #it might be a retweet, and a mentions...   
        
#            @drbre this is a new message.... if in_reply_to fields are empty...            
#            
#            @drbre this is a reply to your message...
#
#            Retweets:
#                
#            I think we neeed to find these ourselves...
#            
#            RT @brdre drbres message
#            
#            my opinion RT @drbre drbres message
#
#            Mentions:            
#            
#            joes happy @drbre this is a mentions
        
            #There is a heirarchy to this......        
    
            # a follows edge is seperate from any of the others...            
            # edge['relationship'] = "Follows"

            # if its just a tweet its just a tweet, its a self connecting edge...
            # edge['relationship'] = "Tweet"
                # obviously these are sub catagories of tweets...
            #     edge['relationship'] = "Mentions"
             #        # These are sub catagories of Mentions... I think...                   
              #       edge['relationship'] = "Replies to"
               #      edge['relationship'] = "Retweet"
#           
#            if tweet['interaction']['interaction']['mentions'] is None:               
#                be = create_tweet_edge(tweet)
#                print "TODO add tweet edge to DB"
            
#            else:
                # We now have a problem...
                # it can be n simple metions...
                # it can be n mentions and a Reply
                # it can be n mentions and a retweet
            
            # @Fact: Our Society: Skinny = anorexic, thick = obese, virgin = too good, non-virgin = slut, friendly = fake, quiet = rude.
            # this has mentions = [Fact]
            # in_reply_to_screen_name = Fact
            # in_reply_to_user_id = 342723432
            # IT does not have an in reply to status value....
            
            # ReplyTo duplicates the Replyied to user in mentions...
            
#            They are clearly able to be a combination...
#
#            drbre tweets -> brownies are good
#
#            EDGE: drbre drbre  Tweet  brownies are good
#            
#            drmarkus tweets ->   @joe @eric RT @drebre: brownies are good
#            
#            EDGE: drmarkus drbre "Mentions" and "Retweet" mentions=[drbre,joe,eric] 
#            EDGE: drmarkus joe   "Mentions" and "Reply to" mentions=[drbre,joe,eric] but what is it a reply to ??? drbre OR joe ??? if joe what would the reply_to_staus_id be???
#            EDGE: drmarkus eric  "Mentions" mentions=[drbre,joe,eric]
#            
#            Really is joe any different to eric in this instance? Why?
#            
#            The datasift data doesn't split this up like this nor does NODEXL....
#            
#            A replies to (according to nodeXL) doesn't have to be in reply to a status by j, 
#            its just a message aimed at a user j so it begins with @username
#
#            retweets are treated as mentions...
#
#            tweets can be in reply to another tweet !!!            
#
#
#SO @sam might do any of the following: 
#
#['Tweet']: I had a good day
#['Retweet']: RT @drbre I had a good day      
#['Reply-to']: @joe I had a good day
#['Mentions']: I know @joe had a good day 
#
#['Tweet', 'Retweet']: Im happy RT @drbre Had a good day
#['Tweet', 'Reply-to']:  @joe I had a good day # This is the same as ['Reply-to']
#['Tweet', 'Mentions']: I know @joe had a good day #(This is the same as ['Mentions'])
#
#['Retweet', 'Reply-to']:  @mark RT @drbre I know @joe had a good day #Is this a mentions as well?
#['Retweet', 'Mentions']: I think @eric would like RT @drbre I know @joe had a good day // RT @drbre I know @joe had a good day
#
#['Reply-to', 'Mentions']: @mark I know @joe had a good day
#
#['Tweet', 'Retweet', 'Reply-to']: @mark This made my day RT @drbre I had a good day #
#['Tweet', 'Retweet', 'Mentions']: I think @eric would like RT @drbre I know @joe had a good day # same as ['Retweet', 'Mentions']
#['Tweet', 'Reply-to', 'Mentions']: @mark I know @joe had a good day #same as ['Reply-to', 'Mentions']?
#
#['Retweet', 'Reply-to', 'Mentions']: @mark RT @drbre I know @joe had a good day # Does this count as a mentions?
#
#['Tweet', 'Retweet', 'Reply-to', 'Mentions']: @mark @eric This made my day RT @drbre I know @joe had a good day
#            
#
#Confusing I know... Looking at how NodeXL works shows it dumps information about the relationships to simplify, for example:
#
#@httplxwley @jckmr le mélange de plusieurs genre littéraire notamment le vaudeville, le burlesque l'absurde ou bien la farce.
#
#This counts as a mentions for  @jckmr and as a Reply-to for @httplxwley
#
#Tweets are not recorded as tweets if they are also something else, so all tweets in NodeXL are circular edges and so the following is recorded as 5 mentions...
#
#On a crazy weekend for #burlesque, which shows do you want to see? @TrixMinx @bustoutburlesq @TheBenWisdom @XenaZeitgeist @AShanksEsq
#
#Retweets are recorded as a mentions... NodeXL doesn't treat it as special... for example the following is recorded as 5 mentions:
#
#RT @davidlee504: On a crazy weekend for #burlesque, which shows do you want to see? @TrixMinx @bustoutburlesq @TheBenWisdom @XenaZeitgeist …
#
#Note because of the 140 character limit @AShanksEsq was cropped, otherwise it would have been 6 mention edges. 
#
#OK so in conclusion...
            
            
            
            # set a boolean flag
            b_simple_tweet = True
            # get the mentions array up front...
            #TODO change user_mentions and user_mentions_ids into a tuple....
            user_mention_ids = dict()
            try:
                for mention_id in tweet['interaction']['interaction']['mention_ids']: 
                    print mention_id
                    # get the user id for the tweet originator
                    # get the index of the match.group('user_retweeted') in mentions username
                    name_index = tweet['interaction']['interaction']['mention_ids'].index(mention_id)
                    user_mention_ids[mention_id] =  tweet['interaction']['interaction']['mentions'][name_index]

                    print "TODO: user_mentions_ids are mangled"
                    print "TODO: check order is same for both arrays...." 

            except Exception, e :
                 print e
                 
            # Add the author and all the mentions to the set of vertexes...
            vertexes.add(tweet['interaction']['interaction']['author']['username'])
            try:
                for username in tweet['interaction']['interaction']['mentions']:
                    vertexes.add(username)
                    print "TODO : Fix this 0 p2"
            except Exception, e :
                 print e
            #A Reply-to is established by checking if the tweet begins with an "@" simples, I think... This will then remove the @\w+ from the mentions array, so it isn't counted twice.
            
            # print "TODO fix reply-to identifing code"   
            
            if tweet['interaction']['twitter']['in_reply_to_user_id'] is not None:
                print tweet['interaction']['twitter']['text']
                b_simple_tweet = False
                reply_edge = create_reply_edge(tweet)#, tweet['interaction']['twitter']['in_reply_to_screen_name'])
                edge_data.insert(reply_edge)
                # remove match.group('user_retweeted') from the tweets mentions... so it doesn;t get added during mentions check
                user_mention_ids.pop(reply_edge['user2_id'], None)
            
##            teststring = "@flack"
##            if  teststring[0] == '@':
#            if tweet['interaction']['twitter']['text'][0] == '@':
#                print tweet['interaction']['twitter']['text']
#                b_simple_tweet = False
#                reply_edge = create_reply_edge(tweet, tweet['interaction']['twitter']['text'][1:].split()[0])
#                edge_data.insert(reply_edge)
#                # remove match.group('user_retweeted') from the tweets mentions... so it doesn;t get added during mentions check
#                user_mentions.remove(reply_edge['username2'])
                            
                            
            #A Retweet will be where we can match "RT @\w+" we can then use the match group to remove the Retweeted user from the mentions array so they aren;t counted as a mentions edge.
            rt_p = re.compile(r"RT @(?P<user_retweeted>\w+)", re.IGNORECASE)
            match = rt_p.search(tweet['interaction']['twitter']['text'])
            if match is not None:
                b_simple_tweet = False
                inv_map = {v: k for k, v in user_mention_ids.items()}
                # inverted_dict = dict([v,k] for k,v in mydict.iteritems())                
                retweet_edge = create_retweet_edge(tweet, match.group('user_retweeted'),  user_mention_ids.values[match.group('user_retweeted')] this won't work)
                edge_data.insert(retweet_edge)
                # remove match.group('user_retweeted') from the tweets mentions... so it doesn't get added during mentions check
                user_mention_ids.pop(retweet_edge['user2_id'], None)                
                
                
            # Anything left in the mentions array will count as a normal mentions.
            for mention in user_mentions:
                b_simple_tweet = False
                mentions_edge = create_mentions_edge(tweet, mention, user_mentions[mention])  #create a "Mentions" edge
                edge_data.insert(mentions_edge)
            #Tweets will simply be a self-connected edge where no others are mentioned, be it RT or reply or mention, 
            #it is the last thing we add if nothing else above matches.
            
            if b_simple_tweet:
                 tweet_edge = create_tweet_edge(tweet)
                 edge_data.insert(tweet_edge)

            # So are Retweets and Reply-to's always mentions? 
            # Well Retweets always mention the original tweeter, 
            # and Reply-to always mention the target twit.
#            
#            So Mention network would include mentions, retweets and reply-to edges ???
#            
#            A retweet network would include just retweet edges.
#
#            A reply-to network would include just the reply-to twit edges  
#            
#            What about hashtags as vertex ??? so we have mentions of hashtags...
            
#        try:
#        except Exception, e :
#            print e
    
    print "edges collected and catagorized..."
    print "TODO: GET VERTEX DATA"
    for vertex in vertexes: 
        print vertex
        vertex_data.insert(vertex)
        
    
def getfriendfollowernetwork():
    print "TODO: getfriendfollowernetwork()"
    # edge_data.insert(tweet_edge)
#main run module
if __name__ == '__main__':
    
    connectToMongoServer("mongodb://dsUser:webobservatory@ec2-54-228-51-114.eu-west-1.compute.amazonaws.com:27017/datasift");
    #connectToMongoServer("mongodb://justin:password123@mdb-001.ecs.soton.ac.uk:27017/twitter_immigration");
    connectoMongoDatabase("datasift")
    connectoMongoCollection("twitter_obesity_tweet_ana_2015_02")
    #datasift.twitter_obesity_profile_GW_2015_02
    #do a check to see if you can found the collection and records.
    
    #print "TODO: not all urls are being captured?"
    #crossfit #vegan #anorexia #gym http://t.co/QHODdovVx2
        
    
    print "TODO: need a method to mirror NodeXL's vertex format."
    print "TODO: need to check if all retweet have 'RT @' as a norm"
    print "TODO: integration with igraph"
    
    print "connected"
    
    get_network_from_tweets()
    
    print "finished"
