# -*- coding: utf-8 -*-
"""
Created on Fri Jun 19 18:17:27 2015

@author: brendan
"""

# -*- coding: utf-8 -*-
"""
Created on Sat Jun 13 09:07:17 2015
@author: home
"""
#import datetime
import pymongo

# POI_THRESHOLD = 0
# Echelon connection    

echelon = False

if echelon:
    MONGOURL = 'aicvm-bjn1c13-1.ecs.soton.ac.uk'
    MONGOUSER =  'harold'
    DBPASSWD = 'AcKerTalksMaChine'
    DBNAME = 'echelon'
    MONGOAUTH = 'mongodb://' + MONGOUSER + ':' + DBPASSWD + '@' + MONGOURL + '/' + DBNAME
    POI_COL = 'poi'
else:
    MONGOURL = 'aicvm-bjn1c13-1.ecs.soton.ac.uk'
    MONGOUSER =  'dsUser'
    DBPASSWD = 'SiftLittleMentsals'
    DBNAME = 'datasift'
    MONGOAUTH = 'mongodb://' + MONGOUSER + ':' + DBPASSWD + '@' + MONGOURL + '/' + DBNAME
    POI_COL = 'datasift_poi'

try:
    conn = pymongo.MongoClient(MONGOAUTH)
    db = conn[DBNAME]
    echelon_poi = db[POI_COL]
    print  MONGOUSER +" connected to " + DBNAME  + "." + POI_COL
except Exception:
    print MONGOUSER +" FAILED to connect to " + DBNAME
    exit()


#for tweet in processed.find( {'qty': { '$exists': True, '$nin': [ 5, 15 ] } } ):
#    print tweet
#    print "\n"


def printPoi():
    
    for person in echelon_poi.find():
        try:
            print person
            print "\n"
        except:
            pass

#def printDescriptionsCount():
#    
#       echelon_poi.aggregate({'$project': { 'count': { '$size':"$descriptions" }}})
#    
#       for person in echelon_poi.find():
#        try:
#            print person['description']
#            for des in person['descriptions']:
#                print str(des['datetime']) + des['description']
#        except Exception:
#            pass
#        
#        print "\n"
#    

def printDescriptionsPoi():
    
    for person in echelon_poi.find():
        try:            
            print person['description']
            for des in person['descriptions']:
                print str(des['datetime']) +"\t"+ des['description']
        except Exception:
            pass
        
        print "\n"

def printGWPoi():
    
    for person in echelon_poi.find({ 'text_anal.gw': { '$exists': True} }):
        try:
            print str(person['text_anal']['gw']['value']) + "/" + str(person['text_anal']['gw']['value']*2.2) + "\t" + person['text_anal']['gw']['source'] + " " + person['description']
            try:            
                for des in person['descriptions']:
                    print str(des['datetime']) + des['description']
            except Exception:
                pass
            
            print "\n"
        except:
            pass

def summarisePoi():
    
    print str(echelon_poi.count())  + " POI in echelon poi database"
    
    print str(echelon_poi.find({ 'text_anal.gw': { '$exists': True} }).count()) + " POI have gw"
    
    print str(echelon_poi.find({ 'text_anal.cw': { '$exists': True} }).count()) + " POI have cw"
    
    print str(echelon_poi.find({ 'text_anal.a': { '$exists': True} }).count()) + " POI have age"
    
    print str(echelon_poi.find({ 'text_anal.h': { '$exists': True} }).count()) + " POI have height"
    
    print str(echelon_poi.find({ 'text_anal.edword_count.value': { '$exists': True, '$gte': 1} }).count()) + " POI have ed word count > 1"
    
    print str(echelon_poi.find({ 'lang':{'$in':['en','en-gb']}}).count()) + " POI have lang = en or en-gb"
    
    print str(echelon_poi.find({ 'ds_gender':{'$in':['male','female']}}).count()) + " POI have gender = male/female"
    
    print str(echelon_poi.find({ 'location':{ '$ne': None } }).count()) + " POI have location data"
    
    print str(echelon_poi.find({ 'coordinates.datetime':{ '$ne': None } }).count()) + " POI have coordinate data"

# printPoi()
printDescriptionsPoi()
# printGWPoi()
summarisePoi()
