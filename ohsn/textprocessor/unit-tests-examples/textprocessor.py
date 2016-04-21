# -*- coding: utf-8 -*-
"""
Created on Tue Jun 16 15:59:13 2015
@author: brendan
"""
import re
import datetime
# import time
# import urllib
from operator import itemgetter
import pymongo
from collections import Counter

MIN_RESOLUTION = datetime.timedelta(seconds=86400)

KEYWORDS = ['anorexic', 
                    'anorexia',
                    'anorexia-purging',
                    'hypergymnasia',
                    'diagnosed',
                    'relapse',
                    'relapsing',
                    'recovery',
                    'recovering',
                    'inpatient',
                    'ed',
                    'eating',
                    'eating-disorder',
                    'ednos',
                    'ed-nos',
                    'bulimic',
                    'bulimia',
                    'depressed',
                    'depression',
                    'depressive',
                    'anxiety',
                    'anxieties',
                    'ocd',
                    'suicidal',
                    'skinny',
                    'thin',
                    'fat',
                    'thighs',
                    'collarbones',
                    'hips',
                    'harm',
                    'self-harm',
                    'selfharm',
                    'cutter',
                    'cutting',
                    'hate',
                    'ana',
                    'proana',
                    'mia',
                    'promia',
                    'starving',
                    'diet',
                    'fasting',
                    'purging',
                    'purge',
                    'clean',
                    'insomnia']

#DATASIFTMONGOURL = "aicvm-bjn1c13-1.ecs.soton.ac.uk"
#DATASIFTMONGOUSER = "dsUser"
#DATASIFTMONGOPWD = urllib.quote_plus('SiftLittleMentsals')
#DATASIFTDBNAME = 'datasift'
#
## DATASIFT_PROCESSED_COLNAME = "update_test"
#
#TWEETS_COLNAME = 'tweets'
#POI_COLNAME = 'poi'
##OBS_COLNAME = 'observations'
##EDGES_COLNAME = 'edges'
#
#DATASIFTMONGOAUTH = 'mongodb://' + DATASIFTMONGOUSER + ':' + DATASIFTMONGOPWD + '@' + DATASIFTMONGOURL + '/' + DATASIFTDBNAME
## connect to database
#print DATASIFTMONGOAUTH
#
##try:
#dsclient = pymongo.MongoClient(DATASIFTMONGOAUTH)
#print DATASIFTMONGOUSER +" connected to " + DATASIFTDBNAME
#dsdb = dsclient[DATASIFTDBNAME]
#
## Connect to all the collections   
#timelines = dsdb[TWEETS_COLNAME] 
#print "connected to collection: " + TWEETS_COLNAME
##timelines.create_index([("interaction.twitter.id", pymongo.DESCENDING)], unique=True)
##print "timeline unique index created on tweet id"
#
#poi = dsdb[POI_COLNAME]
#print "connected to collection: " + POI_COLNAME
##poi.create_index([("user_id", pymongo.DESCENDING)], unique=True)
##print "index created on " + POI_COLNAME + " by user_id"

VERSION = 0.01

# if there aren't any tweets that haven't been processed wait 10 minutes and check again...
# ON_COMPLETE_WAIT = 60*10

def getVersion():
    return VERSION
    
#def mineTweet(tweet):
#
#    meta = {}
#    meta['status_id'] = tweet['interaction']['twitter']['id']
#
#    if tweet['interaction']['twitter']['id'] < 0:
#                tweet['interaction']['twitter']['id'] = long(tweet['interaction']['twitter']['user']['id_str'])
#    
#    meta['user_id'] = tweet['interaction']['twitter']['user']['id']           
#    meta['user_id_str'] = tweet['interaction']['twitter']['user']['id_str']
#    meta['screen_name'] = tweet['interaction']['twitter']['user']['screen_name']
#    meta['lang'] = tweet['interaction']['twitter']['user']['lang']
#    
#    # e.g. 'Thu, 15 Jan 2015 07:00:29 +0000'
#    # meta['tweeted_at'] = datetime.datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
#    meta['tweeted_at'] = datetime.datetime.strptime(tweet['interaction']['twitter']['created_at'], '%a, %d %b %Y %H:%M:%S +0000')
#    meta['parser_version'] = VERSION
#    meta['dateparsed'] = datetime.datetime.now()
#
#    print "-------" + meta['screen_name'] + "----------"
#    try:
#        meta['description'] = mineUserDescription(tweet['interaction']['twitter']['user']['description'])
#        meta['description']['date_time'] = meta['tweeted_at']
#    except KeyError:
#        print "KeyError: on user description"
#        
#    # if its an official retweet ignore the tweet itself
#    if not (identifyRetweet(tweet)):
#        meta['tweettext'] = mineTweetText(tweet['interaction']['twitter']['text'])
#        meta['tweettext']['date_time'] = meta['tweeted_at']
#    
#    print meta
#    return meta
    
def identifyManualRetweet(text):
    #r'\b(?:#|@|)[0-9]*%s[0-9]*\b'
    pattern = re.compile('\s*(RT|retweet|MT|via)\s*@', re.IGNORECASE)
    match = pattern.search(text)
    if match is None:
        return False
    else:
        return True

def identifyRetweet(tweet):
# if its an official retweet ignore the tweet itself
    try:
        orig = tweet['interaction']['twitter']['retweeted_status']
        return True           
    except Exception:
        # remember it may still be a manual retweet so look out for that in mineTweetText!!
        return identifyManualRetweet(tweet['interaction']['twitter']['text'])
 
#def splitReTweet(text):
#    print "WARNING: THIS IS WRONG"
#    bits = re.split('\s*(RT|retweet|MT|via)\s+@', text, 1)
#    return bits[0]
    
#def mineTweetText(text):
#    # Still check if its a manual retweet
#    # Need to strip out what the tweeter actually added, i.e. not a quote/retweet
#    # text = splitReTweet(text)    
#    obs = mineText(text)
#    obs['source'] = 'tweettext'
#    return obs

#def mineUserDescription(text):
#    obs = mineText(text)
#    # meta['source'] = ['screen_name', 'description', 'tweettext']
#    obs['source'] = 'description'
#    return obs

#def mineText(text):
#    text.encode('utf-8')
#    text.replace('\n', '')
#    print text.encode('utf-8','ignore')
#    obs = {}
#    obs['text'] = text
#    obs['age'] = getAge(text)
#    obs['height'] = getHeight(text)
#    obs['LW'], obs['LW-UG'] = getLowWeightKG(text)        
#    obs['HW'], obs['HW-UG'] = getHighWeightKG(text)
#    obs['CW'], obs['CW-UG'] = getCurrentWeightKG(text)            
#    obs['GW'], obs['GW-UG'] = getGoalWeight(text)
#    
#    print "AGE=" + str(obs['age']) + " HEIGHT=" + str(obs['height']) + " CW=" + str(obs['CW']) + "(" + str(obs['CW-UG']) +") GW=" + str(obs['GW']) + "(" + str(obs['GW-UG']) +")\n"
#
#    #obs['hw'] = ''
#    #obs['lw'] = ''
#    #obs['cw_bmi'] = ''
#    #obs['gw_bmi'] = ''
#    return obs
    
def getAge(text):

    # This assumes they are between the age of 10 and 89
    pattern = re.compile("(?P<age>[1-8][0-9])\syear", re.IGNORECASE)
    match = pattern.search(text)
    if match is not None:
        #print match.group('age') +"\t"+ text 
        return match.group('age')
    
    pattern = re.compile("(?P<age>[1-8][0-9])year", re.IGNORECASE)
    match = pattern.search(text)
    if match is not None:
        #print match.group('age') +"\t"+ text 
        return match.group('age')
    
    pattern = re.compile("(?P<age>[1-8][0-9])\sy/o", re.IGNORECASE)
    match = pattern.search(text)
    if match is not None:
        #print match.group('age') +"\t"+ text 
        return match.group('age')

    pattern = re.compile("(?P<age>[1-8][0-9])y/o", re.IGNORECASE)
    match = pattern.search(text)
    if match is not None:
        #print match.group('age') +"\t"+ text 
        return match.group('age')
       
    pattern = re.compile("^(?P<age>[1-8][0-9])\s*[,\:;\s-]", re.IGNORECASE)
    match = pattern.search(text)
    if match is not None:
        #print match.group('age') +"\t"+ text 
        return match.group('age')
    
#def getGender(tweet):
#    # We can search the description for gender cues
#    # We can use the meta-data
#     print "TODO"
#    
#def getSexuality(text):
#    print "TODO"
#    
#    
#def getLocation(tweet):
#     print "TODO"
#    
#
#def getLanguage(tweet):
#     print "TODO"
    
        
def getHeight(text):

    #Height Matching
    pattern = re.compile("(?P<feet>[4-6])\s*('|f(oo)?t)\s*(?P<inches>1[0-1]|[0-9])?\s*(\"|in(ches)?)?", re.IGNORECASE)
    #pattern = re.compile("(?P<feet>[4-6])'\s*(?P<inches>[1-9]|1[0-2])\"?", re.IGNORECASE)
    match = pattern.search(text)
    if match is not None:
        inches =  int(match.group('feet'))*12
        if match.group('inches') is not None:
             inches = inches + int(match.group('inches'))
        height = inches*2.54
        return height
#        print user_stats['username'].encode('utf-8') +":"+ user_stats['age'] +":"+ match.group('feet') +"'" + match.group('inches')+ "\"=" + str(user_stats['height']) #+'\n'
    else:
        pattern = re.compile("(?P<metres>[1-2])m\s*(?P<cmetres>[0-9][0-9]?)\s*(cm)?|(?P<ctmetres>[1-2][0-9][0-9])\s*(cm)", re.IGNORECASE)
        #pattern = re.compile("(?P<feet>[4-6])'\s*(?P<inches>1[01]|\d)\"?", re.IGNORECASE)
        match = pattern.search(text)
        if match is not None:
            if match.group('ctmetres') is not None:
                return float(match.group('ctmetres'))
            else:
                return float(int(match.group('metres'))*100 + int(match.group('cmetres')))
        else:
            pattern = re.compile("(?P<metres>\d\.\d*)\s*m[,\.:;=\s-]", re.IGNORECASE)
            match = pattern.search(text)
            if match is not None:
                return float(match.group('metres'))*100

def getHighWeightKG(text):
    
    pattern = re.compile("hw[:;=\s-]+(?P<mass>\d+\.?\d*)\s*(?P<units>kg|lb|pounds)*", re.IGNORECASE)
    match = pattern.search(text)
    if match is not None:
        mass = float(match.group('mass'))
        if match.group('units') is not None:
            #print match.group('mass') + match.group('units') #user_stats[
            if match.group('units') in ("lb","pounds"):
                weight_kg = mass * 0.453592
                unitsguessed = False
                        #bmi = weight_kg/(height_cm^2)
            else: # i.e. it matches kilos
                weight_kg = mass
                unitsguessed = False
        else:
            # search for units elsewhere in the description
            pattern = re.compile("(lb|lbs|kg|pounds)", re.IGNORECASE)
            match = pattern.search(text)
            if match is not None:
                 if match.group(0) in ("lb","lbs","pounds"):
                        weight_kg = mass * 0.453592
                        unitsguessed = True
                 else: # i.e. it matches kilos
                        weight_kg = mass
                        unitsguessed = True
                #print mass + match.group(0) + "(Unit Deduction)"
            #Lets assume that if the cw is greater than 70 then its in pounds.    
            elif float(mass) < 70:
                weight_kg = mass
                unitsguessed = True
                # print mass + "kg" + "(Unit Probable)"
            else: # if in doubt guess lbs?
                weight_kg = mass * 0.453592
                unitsguessed = True
                #print mass + "lb" + "(Unit Guess)"
            # check location? i.e. USA = lbs, rest = kg
        
        return (weight_kg, unitsguessed)
    else:
        return (None, None)


def getLowWeightKG(text):   
    
    pattern = re.compile("lw[:;=\s-]+(?P<mass>\d+\.?\d*)\s*(?P<units>kg|lb|pounds)*", re.IGNORECASE)
    match = pattern.search(text)
    if match is not None:
        mass = float(match.group('mass'))
        if match.group('units') is not None:
            #print match.group('mass') + match.group('units') #user_stats[
            if match.group('units') in ("lb","pounds"):
                weight_kg = mass * 0.453592
                unitsguessed = False
                        #bmi = weight_kg/(height_cm^2)
            else: # i.e. it matches kilos
                weight_kg = mass
                unitsguessed = False
        else:
            # search for units elsewhere in the description
            pattern = re.compile("(lb|lbs|kg|pounds)", re.IGNORECASE)
            match = pattern.search(text)
            if match is not None:
                 if match.group(0) in ("lb","lbs","pounds"):
                        weight_kg = mass * 0.453592
                        unitsguessed = True
                 else: # i.e. it matches kilos
                        weight_kg = mass
                        unitsguessed = True
                #print mass + match.group(0) + "(Unit Deduction)"
            #Lets assume that if the cw is greater than 70 then its in pounds.    
            elif float(mass) < 70:
                weight_kg = mass
                unitsguessed = True
                # print mass + "kg" + "(Unit Probable)"
            else: # if in doubt guess lbs?
                weight_kg = mass * 0.453592
                unitsguessed = True
                #print mass + "lb" + "(Unit Guess)"
            # check location? i.e. USA = lbs, rest = kg
        
        return (weight_kg, unitsguessed)
    else:
        return (None, None)


def getCurrentWeightKG(text):

    pattern = re.compile("cw[:;=\s-]+(?P<mass>\d+\.?\d*)\s*(?P<units>kg|lb|pounds)*", re.IGNORECASE)
    match = pattern.search(text)
    if match is not None:
        mass = float(match.group('mass'))
        if match.group('units') is not None:
            #print match.group('mass') + match.group('units') #user_stats[
            if match.group('units') in ("lb","pounds"):
                weight_kg = mass * 0.453592
                unitsguessed = False
                        #bmi = weight_kg/(height_cm^2)
            else: # i.e. it matches kilos
                weight_kg = mass
                unitsguessed = False
        else:
            # search for units elsewhere in the description
            pattern = re.compile("(lb|lbs|kg|pounds)", re.IGNORECASE)
            match = pattern.search(text)
            if match is not None:
                 if match.group(0) in ("lb","lbs","pounds"):
                        weight_kg = mass * 0.453592
                        unitsguessed = True
                 else: # i.e. it matches kilos
                        weight_kg = mass
                        unitsguessed = True
                #print mass + match.group(0) + "(Unit Deduction)"
            #Lets assume that if the cw is greater than 70 then its in pounds.    
            elif float(mass) < 70:
                weight_kg = mass
                unitsguessed = True
                # print mass + "kg" + "(Unit Probable)"
            else: # if in doubt guess lbs?
                weight_kg = mass * 0.453592
                unitsguessed = True
                #print mass + "lb" + "(Unit Guess)"
            # check location? i.e. USA = lbs, rest = kg
        
        return (weight_kg, unitsguessed)
    else:
        return (None, None)

        
        
def getGoalWeight(text):

    pattern = re.compile("gw\w?[:;=\s-]+(?P<mass>\d+\.?\d*)\s*(?P<units>kg|lb|pounds)*", re.IGNORECASE)    
    match = pattern.findall(text)
    if match: 
        weight_gw_kg = []
        for m in match:
            mass = float(m[0]) #print m[0] +":"+ m[1] #user_stats[
            # print m
            if m[1] is not u'':  
                if m[1] in ("lb","pounds"):
                    weight_gw_kg.append((mass * 0.453592, False))
                    #print "matched lb"
                        #bmi = weight_kg/(height_cm^2)
                else: # i.e. it matches kilos
                    weight_gw_kg.append((mass, False))
                    #print "matched kg (1)"
            else:
                # search for units elsewhere in the description
                pattern = re.compile("(lb|lbs|kg|pounds)", re.IGNORECASE)
                match = pattern.search(text)
                if match is not None:
                    if match.group(0) in ("lb","lbs","pounds"):
                            weight_gw_kg.append((mass * 0.453592, True))
                            #print "guessing pounds based on units elsewhere"
                    else: # i.e. it matches kilos
                            weight_gw_kg.append((mass, True))
                            #print "guessing kgs based on units elsewhere"
                elif float(mass) < 70:
                   weight_gw_kg.append((mass,True))
                   #print "guessing kilos based on magnitude"
                else: # if in doubt guess lbs?
                   weight_gw_kg.append((mass * 0.453592, True))
                   #print "guessing pounds"
            # print mass + "lb" + "(Unit Guess)"
            # check location? i.e. USA = lbs, rest = kg
            # print mass + match + "(GUESS)"
    
        #sort the list of goal weights
        weight_gw_kg = sorted(weight_gw_kg, key=itemgetter(0))
        #select the lowest
        if  len(weight_gw_kg) > 1:
            if weight_gw_kg[0][0] == 0:
                #print "RETURNING NEXT LOWEST GOAL WEIGHT LOWEST=0"
                return (weight_gw_kg[1][0], weight_gw_kg[1][1] )

        return (weight_gw_kg[0][0], weight_gw_kg[0][1])
    else:
        return (None,None)

#def create_poi_from_api_tweet(api_tweet):
#    print "WARNING THIS IS NOT RIGHT!!!! create_poi_api_tweet()"
#    newpoi = dict()               
#    newpoi['id'] = api_tweet['interaction']['twitter']['user']['id']
#    newpoi['id_str'] = api_tweet['interaction']['twitter']['user']['id_str']
#    newpoi['screen_name'] = api_tweet['interaction']['twitter']['user']['screen_name']
#    newpoi['datetime_joined_twitter'] = datetime.datetime.strptime(api_tweet['interaction']['twitter']['user']['created_at'], '%a, %d %b %Y %H:%M:%S +0000')
#    # newpoi['poi_classification'] = poiclassifier.getPoiClassification(api_tweet)
#    newpoi['lang'] = api_tweet['interaction']['twitter']['lang']
#    newpoi['poi_classification'] = 0
#    newpoi['datetime_last_timeline_scrape'] = datetime.datetime.now()
#    newpoi['datetime_last_follower_scrape'] = datetime.datetime.now()
#    newpoi['timeline_auth_error_flag']  = False
#    newpoi['follower_auth_error_flag']  = False
#    try:
#        poi.insert(newpoi)
#    except pymongo.errors.DuplicateKeyError, e:
#        print "Duplicate POI"
#   
#    return newpoi


def create_poi_from_tweet(tweet, poi):
    print "TODO"


def create_poi_from_datasift_tweet(ds_tweet, poi):
    newpoi = dict()

    # fix the mangled id number
    if ds_tweet['interaction']['twitter']['user']['id'] < 0:
                ds_tweet['interaction']['twitter']['user']['id'] = long(ds_tweet['interaction']['twitter']['user']['id_str'])
      
    newpoi['id'] = ds_tweet['interaction']['twitter']['user']['id']
    newpoi['id_str'] = ds_tweet['interaction']['twitter']['user']['id_str']
    newpoi['screen_name'] = ds_tweet['interaction']['twitter']['user']['screen_name']
    newpoi['datetime_joined_twitter'] = datetime.datetime.strptime(ds_tweet['interaction']['twitter']['user']['created_at'], '%a, %d %b %Y %H:%M:%S +0000')
    # newpoi['poi_classification'] = poiclassifier.getPoiClassification(ds_tweet)
    newpoi['lang'] = ds_tweet['interaction']['twitter']['lang']
    newpoi['description'] = ds_tweet['interaction']['twitter']['user']['description']
    newpoi['descriptions'] = []
    newpoi['poi_classification'] = 0
    newpoi['datetime_last_timeline_scrape'] = datetime.datetime.now() - MIN_RESOLUTION
    newpoi['datetime_last_follower_scrape'] = datetime.datetime.now() - MIN_RESOLUTION
    newpoi['timeline_auth_error_flag']  = False
    newpoi['follower_auth_error_flag']  = False
    
    try:    
        newpoi['location'] =  ds_tweet['interaction']['twitter']['user']['location']
    except Exception:
        pass

    try:    
        newpoi['ds_gender'] = ds_tweet['interaction']['demographic']['gender']
    except Exception:
        pass
    
    try:
        poi.insert(newpoi)
    except pymongo.errors.DuplicateKeyError:
        print "Duplicate POI"
   
    return newpoi
        
def processDatasiftTweet(tweet, poi, timelines):
    # this will be called by the datasift-collection-processor 
    # as a way of populating the poi
    # if a user doesn't exist, create one....
    # else it will simply warn...
    
    # fix the mangled id number
    if tweet['interaction']['twitter']['user']['id'] < 0:
                tweet['interaction']['twitter']['user']['id'] = long(tweet['interaction']['twitter']['user']['id_str'])
            
    create_poi_from_datasift_tweet(tweet, poi)
    # this_poi = poi.find({ "id": tweet['interaction']['twitter']['user']['id']}).limit(1)[0]
    
    person = poi.find({ "id": tweet['interaction']['twitter']['user']['id']}).limit(1)[0]
    
    tweeted_at = datetime.datetime.strptime(tweet['interaction']['twitter']['created_at'], '%a, %d %b %Y %H:%M:%S +0000')    
    
    # WARNING THIS ASSUMES THE TWEETS ARRIVE IN TIME ORDER OLDEST FIRST
    
    if (person['description'] != tweet['interaction']['twitter']['user']['description']):
        # print "FOUND A NEW DESCRIPTION #COOL"
        poi.update({ "id": tweet['interaction']['twitter']['user']['id']}, {'$set':{'description':tweet['interaction']['twitter']['user']['description']}})
        poi.update({ "id": tweet['interaction']['twitter']['user']['id']}, {'$push':{'descriptions':{'datetime':tweeted_at,'source':person['description']}}})
        # poi.update({ "id": tweet['interaction']['twitter']['user']['id']}, {'$push':{'text_anal.edword_count':{'datetime':tweeted_at,'source':source, 'value':edword_count}}})
        
        try:
            # if this_poi['description'] != tweet['interaction']['twitter']['user']['description']:
            # parse the description
            text = tweet['interaction']['twitter']['user']['description']
            text.encode('utf-8')
            text.replace('\n', '')
            print text.encode('utf-8','ignore')
            source = 'description'
                    
            cnt = Counter()
            words = re.findall('\w+', text.lower())
            for word in words:
                if word in KEYWORDS:
                    cnt[word] += 1
            
            print cnt
            edword_count = sum(cnt.values())
            poi.update({ "id": tweet['interaction']['twitter']['user']['id']}, {'$set':{'text_anal.edword_count.datetime':tweeted_at,'text_anal.edword_count.source':source, 'text_anal.edword_count.value':edword_count}})
                            
    #        fix this the tags aren't showing up on the tweets
    #        and we need to embed the obsevations behind a tag on the poi
        
            gw, gw_ug = getGoalWeight(text)
            if gw is not None:
                # obs = (tweeted_at, source, gw_ug, gw)
                # push the observsation onto the timeseries:
                # user['text_anal']['cw'] = {(datetime, source, unit-conf, value),(datetime, source, unit-conf, value), .... (datetime, source, unit-conf, value)}
                poi.update({ "id": tweet['interaction']['twitter']['user']['id']}, {'$set':{'text_anal.gw.datetime':tweeted_at,'text_anal.gw.source':source, 'text_anal.gw.ug':gw_ug, 'text_anal.gw.value':gw}})
                
                
            cw, cw_ug = getCurrentWeightKG(text)
            if cw is not None:
                # obs = (tweeted_at, source, cw_ug, cw)
                # push the observsation onto the timeseries:
                # user['text_anal']['cw'] = {(datetime, source, unit-conf, value),(datetime, source, unit-conf, value), .... (datetime, source, unit-conf, value)}
                poi.update({ "id": tweet['interaction']['twitter']['user']['id']}, {'$set':{'text_anal.cw.datetime':tweeted_at,'text_anal.cw.source':source, 'text_anal.cw.ug':cw_ug, 'text_anal.cw.value':cw}})
                
                
            hw, hw_ug = getHighWeightKG(text)
            if hw is not None:
                # obs = (tweeted_at, source, hw_ug, hw)
                # push the observsation onto the timeseries:
                # user['text_anal']['cw'] = {(datetime, source, unit-conf, value),(datetime, source, unit-conf, value), .... (datetime, source, unit-conf, value)}
                poi.update({ "id": tweet['interaction']['twitter']['user']['id']}, {'$set':{'text_anal.hw.datetime':tweeted_at,'text_anal.hw.source':source, 'text_anal.hw.ug':hw_ug, 'text_anal.hw.value':hw}})
                   
            lw, lw_ug = getLowWeightKG(text)
            if lw is not None:
                # obs = (tweeted_at, source, lw_ug, lw)
                # push the observsation onto the timeseries:
                # user['text_anal']['cw'] = {(datetime, source, unit-conf, value),(datetime, source, unit-conf, value), .... (datetime, source, unit-conf, value)}
                poi.update({ "id": tweet['interaction']['twitter']['user']['id']}, {'$set':{'text_anal.lw.datetime':tweeted_at,'text_anal.lw.source':source, 'text_anal.lw.ug':lw_ug, 'text_anal.lw.value':lw}})
                        
            h = getHeight(text)
            if h is not None:
                # obs = (tweeted_at, source, h)
                # push the observsation onto the timeh
                # user['text_anal']['cw'] = {(datetime, source, unit-conf, value),(datetime, source, unit-conf, value), .... (datetime, source, unit-conf, value)}
                poi.update({ "id": tweet['interaction']['twitter']['user']['id']}, {'$set':{'text_anal.h.datetime':tweeted_at,'text_anal.h.source':source, 'text_anal.h.value':h}})
                            
            a = getAge(text)
            if a is not None:
                # obs = (tweeted_at, source, a)
                # push the observsation onto the timeseries:
                # user['text_anal']['cw'] = {(datetime, source, unit-conf, value),(datetime, source, unit-conf, value), .... (datetime, source, unit-conf, value)}
                poi.update({ "id": tweet['interaction']['twitter']['user']['id']}, {'$set':{'text_anal.a.datetime':tweeted_at,'text_anal.a.source':source, 'text_anal.a.value':a}})
        except Exception:
           print "missing user description"
   
   # process the tweet text
   # if its an official retweet ignore the tweet itself
    if not (identifyRetweet(tweet)):
        text = tweet['interaction']['twitter']['text']
        text.encode('utf-8')
        text.replace('\n', '')
        print text.encode('utf-8','ignore')    
        source = 'tweet_text'
    
    gw, gw_ug = getGoalWeight(text)
    if gw is not None:
        # obs = (tweeted_at, source, gw_ug, gw)
        # push the observsation onto the timeseries:
        # user['text_anal']['cw'] = {(datetime, source, unit-conf, value),(datetime, source, unit-conf, value), .... (datetime, source, unit-conf, value)}
        poi.update({ "id": tweet['interaction']['twitter']['user']['id']}, {'$set':{'text_anal.gw.datetime':tweeted_at,'text_anal.gw.source':source, 'text_anal.gw.ug':gw_ug, 'text_anal.gw.value':gw}})
        
        
    cw, cw_ug = getCurrentWeightKG(text)
    if cw is not None:
        # obs = (tweeted_at, source, cw_ug, cw)
        # push the observsation onto the timeseries:
        # user['text_anal']['cw'] = {(datetime, source, unit-conf, value),(datetime, source, unit-conf, value), .... (datetime, source, unit-conf, value)}
        poi.update({ "id": tweet['interaction']['twitter']['user']['id']}, {'$set':{'text_anal.cw.datetime':tweeted_at,'text_anal.cw.source':source, 'text_anal.cw.ug':cw_ug, 'text_anal.cw.value':cw}})
        
        
    hw, hw_ug = getHighWeightKG(text)
    if hw is not None:
        # obs = (tweeted_at, source, hw_ug, hw)
        # push the observsation onto the timeseries:
        # user['text_anal']['cw'] = {(datetime, source, unit-conf, value),(datetime, source, unit-conf, value), .... (datetime, source, unit-conf, value)}
        poi.update({ "id": tweet['interaction']['twitter']['user']['id']}, {'$set':{'text_anal.hw.datetime':tweeted_at,'text_anal.hw.source':source, 'text_anal.hw.source.ug':hw_ug, 'text_anal.hw.source.value':hw}})
           
    lw, lw_ug = getLowWeightKG(text)
    if lw is not None:
        # obs = (tweeted_at, source, lw_ug, lw)
        # push the observsation onto the timeseries:
        # user['text_anal']['cw'] = {(datetime, source, unit-conf, value),(datetime, source, unit-conf, value), .... (datetime, source, unit-conf, value)}
        poi.update({ "id": tweet['interaction']['twitter']['user']['id']}, {'$set':{'text_anal.lw.datetime':tweeted_at,'text_anal.lw.source':source, 'text_anal.lw.ug':lw_ug, 'text_anal.lw.value':lw}})
        
    
    h = getHeight(text)
    if h is not None:
        # obs = (tweeted_at, source, h)
        # push the observsation onto the timeh
        # user['text_anal']['cw'] = {(datetime, source, unit-conf, value),(datetime, source, unit-conf, value), .... (datetime, source, unit-conf, value)}
        poi.update({ "id": tweet['interaction']['twitter']['user']['id']}, {'$set':{'text_anal.h.datetime':tweeted_at,'text_anal.h.source':source, 'text_anal.h.value':h}})
        
        
    a = getAge(text)
    if a is not None:
        # obs = (tweeted_at, source, a)
        # push the observsation onto the timeseries:
        # user['text_anal']['cw'] = {(datetime, source, unit-conf, value),(datetime, source, unit-conf, value), .... (datetime, source, unit-conf, value)}
        poi.update({ "id": tweet['interaction']['twitter']['user']['id']}, {'$set':{'text_anal.a.datetime':tweeted_at,'text_anal.a.source':source, 'text_anal.a.value':a}})
        
    # save the last coordinates for a user.... might be useful ???    
    try:
        coordinates = tweet['interaction']['twitter']['coordinates']      
        poi.update({ "id": tweet['interaction']['twitter']['user']['id']}, {'$set':{'coordinates.datetime':tweeted_at,'coordinates':coordinates}})
        print "Coordinates Found!"
    except Exception:
        pass         
     
    # tweet['interaction']['twitter']['user']['id'] 
    # poi.update({'id': tweet['interaction']['twitter']['user']['id']}, {'$set' : {'meta':poi['meta']}}, upsert=False)

    # Tag the tweet so you know you have done it....
    tweet_tag = {}
    tweet_tag['text_anal'] = {}
    tweet_tag['text_anal']['version'] = VERSION
    tweet_tag['text_anal']['dateparsed'] = datetime.datetime.now()
    try:
        timelines.update({'interaction.twitter.id': tweet['interaction']['twitter']['id']} ,{'$set':{'interaction.echelon':tweet_tag}}, upsert=False)
    except Exception:
        print "ERROR: timeline update failed"
        
        
def processTweet(tweet):
    print "TODO: textprocessor.processTweet()"

#if __name__ == "__main__":
#    # This is for constantly updating the incoming tweets from the timeline harvester/streaming api....
#    while True:
#        # process any tweets that haven't been processed.
#        new_tweet = timelines.find( { 'echelon.text_anal' : { '$exists' : False } } ).limit(1)[0]
#        if new_tweet is not None:        
#            processTweet(new_tweet)
#        else:
#            time.sleep(ON_COMPLETE_WAIT)