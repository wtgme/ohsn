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


MONGOURL = 'localhost'
MONGOUSER = 'harold'
DBPASSWD = 'AcKerTalksMaChine'
DBNAME = 'echelon'
MONGOAUTH = 'mongodb://' + MONGOUSER + ':' + DBPASSWD + '@' + MONGOURL + '/' + DBNAME
POI_COL = 'poi'

try:
    conn = pymongo.MongoClient(MONGOAUTH)
    db = conn[DBNAME]
    echelon_poi = db[POI_COL]
    print  MONGOUSER +" connected to " + DBNAME  + "." + POI_COL
except Exception:
    print MONGOUSER +" FAILED to connect to " + DBNAME
    exit()

user_id = 2582709833
user_id = 2655297658
user_id = 2382568416
user_id = 905312215

person = echelon_poi.find({'id':user_id}).limit(1)[0]
print person
