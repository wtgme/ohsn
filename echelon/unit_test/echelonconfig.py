# -*- coding: utf-8 -*-
"""
Created on Fri Jun 12 08:40:07 2015

@author: home
"""
## 
#poi-datasift-miner
#    # mine the user descriptions for cw-gw data
#    cw-ugw-datasift-description-miner
#
#    # mine the actual tweets for cw-gw data
#    cw-ugw-datasift-tweet-miner

class Script_to_Initialise_Echelon(object):
    # run 
    # identify POI and save to POI_COL

    # start TAPI_TimelineHarvester
    # start FollowerHavester


class TAPI_TimelineHarvester_Config(object):
   
    # "mongodb://brendan:password123@mdb-001.ecs.soton.ac.uk:27017"
    # connectToMongoServer("mongodb://dsUser:webobservatory@ec2-54-228-51-114.eu-west-1.compute.amazonaws.com:27017/datasift");
    # connectoMongoDatabase("datasift")
    # connectoMongoCollection("twitter_obesity_profile_GW_2015_02")
    
    # date = datetime.datetime.now()    
    
    DBURL = 'aicvm-bjn1c13-1'
    dblogin = 'bjn1c13'
    dbpassword = ''
    
    DBNAME = 'node1'
    Config_COL = 'config_col'
    POI_COL = 'poi_col'
    Timelines_COL = 'timelines_col'
    
    APP_KEY    = config.get('credentials','app_key')
    APP_SECRET = config.get('credentials','app_secret')
    OAUTH_TOKEN        = config.get('credentials','oath_token')
    OAUTH_TOKEN_SECRET = config.get('credentials','oath_token_secret')
    
    timeline_poi_classification_threshold = 0
    get_timeline_images = False
    images_poi_classification_threshold = 0
    get_user_timeline_count = 200
    # wait for 15 minutes if an exception occurs
    on_exception_waittime = 60*15
    # if a non-rate-limit or authorisation error occurs log it here....    
    error_log_file = 'TAPI_TimelineHarvester_ErrorLog_' + datetime.datetime.now() + '.log'


class TAPI_MRREdgeNetworkHarvester_Config(object):

    # This can be run either 
    # on demand, at analysis time as it works off of the RAW timeline data
  
    # Integrate with the TAPI_TimelineHarvester so that as tweets come in they are processed into the MRR network
    # If we don't like how that works we can change it and re-run at analysis stage.
    date = datetime.datetime.now()
    version = '0_0'
  
    DBNAME = 'node1'
    MRREdgeNetwork_COL = 'mmr_edge_network'

##   This is not required as it runs off the timelines...
##   Unless we need to lookup other data/dynamic poi adding etc
##   That would be furtherwork...

#    APP_KEY    = config.get('credentials','app_key')
#    APP_SECRET = config.get('credentials','app_secret')
#    OAUTH_TOKEN        = config.get('credentials','oath_token')
#    OAUTH_TOKEN_SECRET = config.get('credentials','oath_token_secret')
    
    # settings that determine how the network is formed?
    print "TODO: sort out final method for this!!!!"
    
class TAPI_FollowerNetworkHarvester_Config(object):
    
    # MongoDB database config and credentials
    dblogin = 'bjn1c13'
    dbpassword = ''    
    
    DBFOLLOWERURL = aicvm-bjn1c13-2
    DBNAME_N2 = 'node2'
    FollowerNetwork_COL = 'follower_edge_network'
    
    DBURL = 'aicvm-bjn1c13-1'
    DBNAME = 'node1'
    Config_COL = 'config_col'
    POI_COL = 'poi_col'
    
    print "TODO: get echelon app key"
    
    # get these by registering an application with twitter
    APP_KEY    = config.get('credentials','app_key')
    APP_SECRET = config.get('credentials','app_secret')
    OAUTH_TOKEN        = config.get('credentials','oath_token')
    OAUTH_TOKEN_SECRET = config.get('credentials','oath_token_secret')

    # only get followers for poi with classification less than this:
    # -1 is get no-one, 0 is the highest real classification.
    # Not implemented yet...
    follower_poi_classification_threshold = -1

    # only check the echelon/followee network at most every 1 weeks...
    # we have data limits after-all
    min_resolution = timedelta(1*604800)

    """
        Psuedocode    
    """
        
    while True:
    
        nextpoi = poi.find{poi_classification < follower_poi_classification_threshold} sort by datetime_last_follower_scrape ASC limit 1
        if datetime.datetime.now() - nextpoi['datetime_last_follower_scrape'] > min_resolution:
            auth_error = scape(nextpoi['id'])
            if auth_error:
                update poi db with follower_auth_error
                
            update poi_db with datetime_last_follower_scrape = datetime.datetime.now()
                
        else:    
            time_next_scrape = datetime_last_follower_scrape + min_resolution
            time.wait(time_next_scrape)


class TAPI_Streaming_Config(object):
    
    aicvm-bjn1c13-3
    DBNAME_N3 = 'node3'
    Stream_COL = 'stream'
    
    APP_KEY    = config.get('credentials','app_key')
    APP_SECRET = config.get('credentials','app_secret')
    OAUTH_TOKEN        = config.get('credentials','oath_token')
    OAUTH_TOKEN_SECRET = config.get('credentials','oath_token_secret')
    
class Config(object):

    # SERVERS/NODES
    
    # A1 datasift server address

    # N1 - Config_COL and POI_COL and Timelines_COL and MRREdgeNetwork_COL and TAPI_TimelineHarvester and A_NetworkHarvester
    # aicvm-bjn1c13-1
    # 
               
    
    # N2 - FollowerNetwork_COL TAPI_Follower_Followee_Network_Harvester
    #        - This will access Config_COL and POI_COL on N1
    # aicvm-bjn1c13-2


    # N3 - Stream_COL and TAPI_KeywordStream server
    #        - This will access Config_COL
    #        - This is standalone till datasift dies
    # aicvm-bjn1c13-3

    
    # L1 - Backup and Analysis
    #        - This will access all the above for daily backups
    #        - This will access all of the above for analysis dumps
    


