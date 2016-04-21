# -*- coding: utf-8 -*-
"""
Created on Sat Jun 13 09:07:17 2015
@author: home
"""

#import datetime
import pymongo
import urllib

# POI_THRESHOLD = 0

DATASIFTMONGOURL = "localhost"
DATASIFTMONGOUSER = "dsUser"
DATASIFTMONGOPWD = urllib.quote_plus('SiftLittleMentsals')
DATASIFTDBNAME = 'datasift'

DATASIFT_PROCESSED_COLNAME = "datasift_all"
# DATASIFTCOLNAMES = ["twitter_obesity_profile_GW_2015_01",'twitter_obesity_profile_GW_2015_02',"twitter_obesity_profile_GW_2015_03"]
# DATASIFTCOLNAMES = ["twitter_obesity_profile_GW_2015_01"]

DATASIFTMONGOAUTH = 'mongodb://' + DATASIFTMONGOUSER + ':' + DATASIFTMONGOPWD + '@' + DATASIFTMONGOURL + '/' + DATASIFTDBNAME
# connect to database
#print DATASIFTMONGOAUTH

try:
    dsclient = pymongo.MongoClient(DATASIFTMONGOAUTH)
    print DATASIFTMONGOUSER +" connected to " + DATASIFTDBNAME
    dsdb = dsclient[DATASIFTDBNAME]
    processed = dsdb[DATASIFT_PROCESSED_COLNAME]
except Exception:
    print DATASIFTMONGOUSER +" FAILED to connect to " + DATASIFTDBNAME
    exit()


#for tweet in processed.find( {'qty': { '$exists': True, '$nin': [ 5, 15 ] } } ):
#    print tweet
#    print "\n"

for tweet in processed.find():
    try:
        print tweet
        print "\n"
    except:
        pass