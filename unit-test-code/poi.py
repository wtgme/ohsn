# -*- coding: utf-8 -*-
"""
Created on Sat Jun 13 09:13:32 2015

@author: home
"""

import datetime

class POI(object):
    # WE aim to mimic the nodeXL structure for a node.
    # but allow for longitudinal observation data

#    # remember the id is sometimes mangled by datasift so if discovering from datasift 
#    # lets look this up from screen_name using the T-API
#    userid
#    # as back_up and human-readability
#    screen_name
#    datetime_joined_twitter
#    # datetime_nextfollower_scape_due
#    # 0 = first-order, 1 = second-order etc...
#    poi_classification
#    
#    datetime_last_timeline_scrape = datetime.datetime.min()
#    datetime_last_follower_scrape = datetime.datetime.min()
#    
#    timeline_auth_error_flag = False
#    follower_auth_error_flag = False
        
    def __init__(self, userid, screen_name, datetime_joined_twitter, poi_classification=0, datetime_last_timeline_scrape = datetime.datetime.min(), datetime_last_follower_scrape = datetime.datetime.min(), timeline_auth_error_flag = False, follower_auth_error_flag = False ):
        self.userid = userid
        # as back_up and human-readability
        self.screen_name = screen_name
        self.datetime_joined_twitter = datetime_joined_twitter
        # datetime_nextfollower_scape_due
        # 0 = first-order, 1 = second-order etc...
        self.poi_classification = poi_classification
        
        self.datetime_last_timeline_scrape = datetime_last_timeline_scrape
        self.datetime_last_follower_scrape = datetime_last_follower_scrape
        
        self.timeline_auth_error_flag = timeline_auth_error_flag
        self.follower_auth_error_flag = follower_auth_error_flag 
        print "TODO: set up poi_col unique key = id  !!! "
        
        
        