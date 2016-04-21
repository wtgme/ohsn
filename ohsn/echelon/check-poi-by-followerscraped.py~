# -*- coding: utf-8 -*-
"""
Created on Tue Jun 23 15:07:48 2015

@author: brendan
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Jun 23 13:19:30 2015

@author: brendan
"""
import pymongo
import datetime
import time
import subprocess


def check_disk_space_and_wait(maxpercent=95, sleeptime=60, filename = "disk-space-check.file"):
    df = subprocess.Popen(["df", filename], stdout=subprocess.PIPE)
    output = df.communicate()[0]
    device, size, used, available, percent, mountpoint = output.split("\n")[1].split()
    percent = float(percent[:-1])
    
    while percent > maxpercent:
        print "Disk utilisation ("+ str(percent) +"%) is above " + str(maxpercent) + "% waiting till it is reduced"
        time.sleep(sleeptime)           
        df = subprocess.Popen(["df", filename], stdout=subprocess.PIPE)
        output = df.communicate()[0]
        device, size, used, available, percent, mountpoint = output.split("\n")[1].split()
        percent = float(percent[:-1])
    
# MONGOURL = 'bjn1c13-desktop.ecs.soton.ac.uk'               
MONGOURL = 'localhost'
MONGOUSER =  'harold'
DBPASSWD = 'AcKerTalksMaChine'
DBNAME = 'echelon'
MONGOAUTH = 'mongodb://' + MONGOUSER + ':' + DBPASSWD + '@' + MONGOURL + '/' + DBNAME
POI_COL = 'poi'
FOLLOWEREDGES_COL = 'followfriendedges'

try:
    conn = pymongo.MongoClient(MONGOAUTH)
    db = conn[DBNAME]
    echelon_poi = db[POI_COL]
    print  MONGOUSER +" connected to " + DBNAME  + "." + POI_COL
    followfriendedges = db[FOLLOWEREDGES_COL]
    print  MONGOUSER +" connected to " + DBNAME  + "." + FOLLOWEREDGES_COL
except Exception:
    print MONGOUSER +" FAILED to connect to " + DBNAME
    exit()

start = datetime.datetime(2015, 7, 6, 15, 0, 0, 0)
end = datetime.datetime(2015, 7, 25, 15, 0, 0, 0)

poi_scraped = echelon_poi.find({'datetime_last_follower_scrape': {'$gte': start, '$lt': end}}).count()
print "total scraped: " + str(poi_scraped)

poi_scraped = echelon_poi.find({'datetime_last_follower_scrape': {'$gte': start, '$lt': end}, 'timeline_auth_error_flag':False}).count()
print "users scraped with no auth_error: " + str(poi_scraped)

tweet_count = followfriendedges.find().count()
print "edges scraped: " + str(tweet_count)

#tweet = echelon_timelines.find().limit(1)[0]
#print tweet

# print db.command("collstats", FOLLOWEREDGES_COL)

#check_disk_space_and_wait()
#print "ah thats better thanks, it was getting crowded in here"

# poi_scraped = echelon_poi.find({'datetime_last_timeline_scrape': {'$gte': start, '$lt': end}})
#for person in poi_scraped:
#    print person


