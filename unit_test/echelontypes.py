# -*- coding: utf-8 -*-
"""
Created on Sat Jun 13 09:13:32 2015

@author: home
"""
import datetime

class POI(object):
        
    def __init__(self, userid, screen_name, datetime_joined_twitter, poi_classification=0):
        self.userid = userid
        # as back_up and human-readability
        self.screen_name = screen_name
        self.datetime_joined_twitter = datetime_joined_twitter
        # datetime_nextfollower_scape_due
        # 0 = first-order, 1 = second-order etc...
        self.poi_classification = poi_classification
#        
#        self.datetime_last_timeline_scrape = datetime_last_timeline_scrape
#        self.datetime_last_follower_scrape = datetime_last_follower_scrape
#        
#        self.timeline_auth_error_flag = timeline_auth_error_flag
#        self.follower_auth_error_flag = follower_auth_error_flag 
        
        self.datetime_last_timeline_scrape = datetime.datetime.now()
        self.datetime_last_follower_scrape = datetime.datetime.now()
#    
        self.timeline_auth_error_flag = False
        self.follower_auth_error_flag = False
        
        this is defunked, need to use dict objects for mongodb
        
        
        