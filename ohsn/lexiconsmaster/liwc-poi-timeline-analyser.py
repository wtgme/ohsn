# -*- coding: utf-8 -*-
"""
Created on Tue Jun 09 14:36:40 2015
author: home
"""

import ConfigParser
import datetime
import re
from datetime import timedelta 
# from pymongo import Connection
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt 
from lexicons.liwc import Liwc
import pymongo

MONGOURL = 'localhost'
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

    timelines = db[TIMELINES_COL]
    print  MONGOUSER +" connected to " + DBNAME  + "." + TIMELINES_COL

except Exception:
    print MONGOUSER +" FAILED to connect to " + DBNAME
    exit()


print poi.find({"liwc_anal.mined": True}).count()

# exit()

# set every poi to have not been analysed.
# poi.update({},{'$set':{"liwc_anal.mined": False}}, multi=True)

while True:

    count = poi.find({'timeline_auth_error_flag':False, "liwc_anal.mined": False}).count()	
    if count == 0:
        break
    else:
	    print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") +"\t"+ str(count) + " remaining"
	
    for user in poi.find({'timeline_auth_error_flag':False, "liwc_anal.mined": False}).limit(250):
        #progcounter += 1
        #if progcounter%1000 == 0:
        #    print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + str(progcounter)
        
	liwc = Liwc()
	textmass = ""
	
        for tweet in timelines.find({'user.id': user['id']}):
	    # is it a retweet?
 	    #if not ('retweeted_status' in tweet):
		text = tweet['text'].encode('utf8')
		# text = re.sub(r"http\S+", "", text) # this doesn't do anything
		textmass = textmass + " " + text
		# print tweet['text'].encode('utf8')

	textmass = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)"," ",textmass).split())
	textmass.lower()
	result = Liwc.summarize_document(liwc, textmass)
	#print result    	
	#exit()
	# Liwc.print_summarization(liwc, result)
        
	poi.update({'id':user['id']},{'$set':{"liwc_anal.mined": True, "liwc_anal.result":result}})
                
