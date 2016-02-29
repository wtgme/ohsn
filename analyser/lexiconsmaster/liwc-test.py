# -*- coding: utf-8 -*-
"""
Created on Tue Jun 09 14:36:40 2015

author: home
"""
import ConfigParser
import datetime
import re
from datetime import timedelta 
from pymongo import Connection
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt 
from lexicons.liwc import Liwc

DBNAME = 'twitter_test'
COLLECTION = 'home_timelines'

print(DBNAME)
print(COLLECTION)

conn = Connection()
db = conn[DBNAME]
tweets = db[COLLECTION]

liwc = Liwc()

print("twitter connection and database connection configured")

usernames = {'needingbones':'b-', 'tiinyterry':'g-'}

print "TODO: create your own ED dictionary..."
print "TODO: upload the LIWC analysis result to the user profile entry? No LIWC should be done on a static set"

for username in usernames:
    results = tweets.find({'user.screen_name': username})
    textmass = ""
    for result in results:
        textmass = textmass + " " + result['text'].encode('utf8')
    
    #textmass = unicode( textmass, errors='ignore')
    textmass = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)"," ",textmass).split())
#    outfile = open(username + ".txt","w")
#    outfile.write(textmass)
#    outfile.close()
    textmass.lower()
    result = Liwc.summarize_document(liwc, textmass)
    Liwc.print_summarization(liwc, result)
    
     
#infilename = "all_text_Content.txt"
#infilename = "lincoln.txt"
#
#infile = open(infilename,"r")
#sample = ""
#
#for line in infile:
#    sample = sample  + " " + line
#
#liwc = Liwc()
#result = Liwc.summarize_document(liwc, sample)
#Liwc.print_summarization(liwc, result)     
     