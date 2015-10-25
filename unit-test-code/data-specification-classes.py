# -*- coding: utf-8 -*-
"""
Created on Fri Jun 12 14:29:58 2015

@author: home
"""

class POI(object):
    # WE aim to mimic the nodeXL structure for a node.
    # but allow for longitudinal observation data

    # remember the id is sometimes mangled by datasift so if discovering from datasift 
    # lets look this up from screen_name using the T-API
    id
    # as back_up and human-readability
    screen_name
    datetime_joined_twitter
    datetime_last_timeline_scrape
    datetime_last_follower_scrape
    
    timeline_auth_error_flag
    follower_auth_error_flag
    # datetime_nextfollower_scape_due
    # 0 = first-order, 1 = second-order etc...
    poi_classification
    
    print "TODO: set up poi_col unique key = id  !!! "

class EdgeOBS(object):
    id0
    screen_name_0
    id1
    screen_name_1
    relationship
    # this is an observation we can merge observations into weighted and time period later.
    date
    # a copy of the status that established it: this will contain all that is needed for export to NodeXL or otherwise.
    status
    
class Edge(object):
    id0
    screen_name_0
    id1
    screen_name_1
    relationship    
    # date    
    date_start
    date_end
    weight    
    # a copy of the status that established it: this will contain all that is needed for export to NodeXL or otherwise.
    status
        
"""
Analysis Stage Vertex

"""

class Vertex(object):
    # WE aim to mimic the nodeXL structure for a node.
    # but allow for longitudinal observation data

    # remember the id is sometimes mangled by datasift so if discovering from datasift 
    # lets look this up from screen_name using the T-API
    id
    datetime_joined_twitter
    datetime_last_timeline_scrape
    
    # 0 = first-order, 1 = second-order etc...
    POI_classification

    # This stuff is subject to change!!! what to do???    
    observations
        TwitterObs
        PhysicalObs
        LIWCScores
     


     
"""
Analysis Stage

Collection measurement_observations
infered from tweets/descriptions
Should be a list of observations of type PhysicalObs

"""
class TwitterObs(object):
           datetime_observation
            screen_name        
            userdescription
            statuses_count
            followers_count
            friends_count
            favourites_count            
            time_zone
            time_zone_utc_offset
            geo_enabled
            location        
            web    
            klout_score
            profile_image_url


class PhysicalObs(object):
    datetime_observation
    id            
    age
    height
    hw
    lw
    cw
    gw
    cw_bmi
    gw_bmi

"""
Analysis Stage

Collection measurement_observations
infered from tweets/descriptions
Should be a list of observations of type PhysicalObs
"""
    
class LIWCScores(object):
    # a LIWC profile occurs over a time period.
    datetime_begin_observation
    datetime_end_observation
    id
    # the rest ...
    # create your own dictionary for ED terms...
    