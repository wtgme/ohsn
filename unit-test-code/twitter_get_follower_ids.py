# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 18:43:41 2015

@author: home
"""
import sys
import string
import simplejson
import sqlite3

import time
import datetime
from pprint import pprint

import sqlalchemy
from sqlalchemy.orm import mapper, sessionmaker
from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, Unicode, Float # importing Unicode is important! If not, you likely encounter data type error.
from sqlalchemy.ext.declarative import declarative_base
from types import *

from datetime import datetime, date, time

##### FIRST BLOCK OF MODIFIED CODE --> ADDED TO IMPORT TWYTHON AND ADD OAUTH AUTHENTICATION #####
from twython import Twython

import time

#%%

t = Twython(app_key='Mfm5oNdGSPMvwhZcB8N4MlsL8',       #REPLACE 'APP_KEY' WITH YOUR APP KEY, ETC., IN THE NEXT 4 LINES
    app_secret='C0rbmJP0uKbuF6xcT6aR5vFOV9fS4L1965TKOH97pSqj3NJ1mP',
    oauth_token='3034707280-wFGQAF4FGBviaiSguCUdeG36NIQG1uh8qqXTC1G',
    oauth_token_secret='HUWMfHKyPShE6nH5WXlI26izoQjNtV3US3mNpND1F9qrO')

Base = declarative_base()
class ACCOUNT(Base):
    __tablename__ = 'accounts' # this is the table name for a list of scree names to be mined. You need to go to SQLite Database browser and create a new DB (make sure that DB's name matches the one defined in this script); within that DB, create a table, make sure the table name and field names match the ones defined here. 
    rowid = Column(Integer, primary_key=True)     
    screen_name = Column(String)  
    user_type = Column(String) 

    def __init__(self, screen_name, user_type
    ):       
    
        self.screen_name = screen_name
        self.user_type = user_type


    def __repr__(self):
       return "<Company, CSR_account('%s', '%s')>" % (self.rowid, self.screen_name)




def get_data(kid):
    
    follower_count = 0
    next_cursor = -1

    while(next_cursor!=0):
        try:     
            followers = t.get_followers_list(screen_name=kid,count=200,cursor=next_cursor)
        except TwythonRateLimitError, e:        
            print "Error reading id %s, exception: %s" % (kid, e)
            print("Waiting 15 minutes YAWN!")
            time.sleep(900)
        except Exception, e:
            print "Error reading id %s, exception: %s" % (kid, e)
            raw_input("Hit Enter to Continue: ")
            #Python 3.x.x            
            #input_var = input("Hit Enter to Continue: ")
            
            
        #for key, value in  followids.iteritems() :
        #    print key, value
        for follower in followers['users']:
            print "%s,%s" %(kid, follower['screen_name'])
            follower_count=follower_count+1
                #for result in search['users']:
                #   time_zone =result['time_zone'] if result['time_zone'] != None else "N/A"
                #  print result["name"].encode('utf-8')+ ' '+time_zone.encode('utf-8')
            
        next_cursor =  followers["next_cursor"]
        print "%d Followers of id: %s, collected" % (follower_count,kid)
        time.sleep(60)
        
    print "ALL %d Followers of id: %s, collected" % (follower_count,kid)

#def get_data(kid):
#    
#    try:        
#        d = t.get_user_timeline(screen_name=kid, count="1", page="1", include_entities="true", include_rts="1")  #NEW LINE
#        
#        followeridcursor = t.get_followers_ids(screen_name=kid)
#    
#    except Exception, e:
#        
#        print "Error reading id %s, exception: %s" % (kid, e)
#        return None
#    
#    print len(d),
#    
#    return d
    
class Scrape:
    def __init__(self):    
        engine = sqlalchemy.create_engine("sqlite:///test-database.sqlite", echo=False)  # different DB name here
        Session = sessionmaker(bind=engine)
        self.session = Session()  
        Base.metadata.create_all(engine)
    
    def main(self):
    
        all_ids = self.session.query(ACCOUNT).all()
        
        keys = []
        for i in all_ids[0:]: 
            screen_name = i.screen_name
            kid = screen_name    			
            rowid = i.rowid
            user_type = i.user_type
            print "\rprocessing id %s/%s  --  %s" % (rowid, len(all_ids), screen_name),
            sys.stdout.flush()
            d = get_data(kid)

#            # do something with the data            
#            
#            if not d:
#                continue	
#            
#            if len(d)==0:    			
#                print "d==0"
#                continue
#           
#           #write_data(self, d, screen_name, user_type)
#              
#            self.session.commit()
#        

        self.session.close()


if __name__ == "__main__":
    s = Scrape()
    s.main()