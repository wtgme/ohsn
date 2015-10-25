# -*- coding: utf-8 -*-
"""
Created on Tue Jun 16 15:59:13 2015
@author: brendan
"""
import re
import datetime
from operator import itemgetter

VERSION = 0.01

def getVersion():
    return VERSION

def mineTweet(tweet):

    meta = {}
    meta['status_id'] = tweet['interaction']['twitter']['id']

    if tweet['interaction']['twitter']['id'] < 0:
                tweet['interaction']['twitter']['id'] = long(tweet['interaction']['twitter']['user']['id_str'])
    
    meta['user_id'] = tweet['interaction']['twitter']['id']           
    meta['user_id_str'] = tweet['interaction']['twitter']['user']['id_str']
    meta['screen_name'] = tweet['interaction']['twitter']['user']['screen_name']
    meta['lang'] = tweet['interaction']['twitter']['user']['lang'] 
    
    # e.g. 'Thu, 15 Jan 2015 07:00:29 +0000'
    # meta['tweeted_at'] = datetime.datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
    meta['tweeted_at'] = datetime.datetime.strptime(tweet['interaction']['twitter']['created_at'], '%a, %d %b %Y %H:%M:%S +0000')
    meta['parser_version'] = VERSION
    meta['dateparsed'] = datetime.datetime.now()

    print "-------" + meta['screen_name'] + "----------"
    try:
        meta['description'] = mineUserDescription(tweet['interaction']['twitter']['user']['description'])
    except KeyError:
        print "KeyError: on user description"
        
    # if its an official retweet ignore the tweet itself
    if not (identifyRetweet(tweet)):
        meta['tweettext'] = mineTweetText(tweet['interaction']['twitter']['text'])
            
    return meta
    
def identifyManualRetweet(text):
    #r'\b(?:#|@|)[0-9]*%s[0-9]*\b'
    pattern = re.compile('\s*(RT|retweet|MT|via)\s+@', re.IGNORECASE)
    match = pattern.search(text)
    if match is None:
        return False
    else:
        return True

def identifyRetweet(tweet):
# if its an official retweet ignore the tweet itself
    if tweet['interaction']['twitter']['retweeted_status'] is None:        
        # remember it may still be a manual retweet so look out for that in mineTweetText!!
        return identifyManualRetweet(tweet['interaction']['twitter']['text'])
    else:
        return True

#def splitReTweet(text):
#    print "WARNING: THIS IS WRONG"
#    bits = re.split('\s*(RT|retweet|MT|via)\s+@', text, 1)
#    return bits[0]
    
def mineTweetText(text):
    # Still check if its a manual retweet
    # Need to strip out what the tweeter actually added, i.e. not a quote/retweet
    # text = splitReTweet(text)    
    obs = mineText(text)
    obs['source'] = 'tweettext'
    return obs

def mineUserDescription(text):
    obs = mineText(text)
    # meta['source'] = ['screen_name', 'description', 'tweettext']
    obs['source'] = 'description'
    return obs

def mineText(text):
    text.encode('utf-8')
    text.replace('\n', '')
    print text.encode('utf-8','ignore')
    obs = {}
    obs['text'] = text
    obs['age'] = getAge(text)
    obs['height'] = getHeight(text)
    obs['LW'], obs['LW-UG'] = getLowWeightKG(text)        
    obs['HW'], obs['HW-UG'] = getHighWeightKG(text)
    obs['CW'], obs['CW-UG'] = getCurrentWeightKG(text)            
    obs['GW'], obs['GW-UG'] = getGoalWeight(text)
    
    print "AGE=" + str(obs['age']) + " HEIGHT=" + str(obs['height']) + " CW=" + str(obs['CW']) + "(" + str(obs['CW-UG']) +") GW=" + str(obs['GW']) + "(" + str(obs['GW-UG']) +")\n"

    #obs['hw'] = ''
    #obs['lw'] = ''
    #obs['cw_bmi'] = ''
    #obs['gw_bmi'] = ''
    return obs
    
def getAge(text):
    
    # This assumes they are between the age of 10 and 89
    pattern = re.compile("(?P<age>[1-8][0-9])\syear", re.IGNORECASE)
    match = pattern.search(text)
    if match is not None:
        print match.group('age') +"\t"+ text 
        return match.group('age')
    
    pattern = re.compile("(?P<age>[1-8][0-9])year", re.IGNORECASE)
    match = pattern.search(text)
    if match is not None:
        print match.group('age') +"\t"+ text 
        return match.group('age')
    
    pattern = re.compile("(?P<age>[1-8][0-9])\sy/o", re.IGNORECASE)
    match = pattern.search(text)
    if match is not None:
        print match.group('age') +"\t"+ text 
        return match.group('age')

    pattern = re.compile("(?P<age>[1-8][0-9])y/o", re.IGNORECASE)
    match = pattern.search(text)
    if match is not None:
        print match.group('age') +"\t"+ text 
        return match.group('age')
       
    pattern = re.compile("^(?P<age>[1-8][0-9])\s*[,\:;\s-]", re.IGNORECASE)
    match = pattern.search(text)
    if match is not None:
        print match.group('age') +"\t"+ text 
        return match.group('age')
    
def getGender(tweet):
    # We can search the description for gender cues
    # We can use the meta-data
     print "TODO"
    
def getSexuality(text):
    print "TODO"
    
    
def getLocation(tweet):
     print "TODO"
    

def getLanguage(tweet):
     print "TODO"
    
        
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
        sorted(weight_gw_kg,key=itemgetter(0))
        #select the lowest
        if  len(weight_gw_kg) > 1:
            if weight_gw_kg[0][0] == 0:
                #print "RETURNING NEXT LOWEST GOAL WEIGHT LOWEST=0"
                return (weight_gw_kg[1][0], weight_gw_kg[1][1] )

        return (weight_gw_kg[0][0], weight_gw_kg[0][1])
    else:
        return (None,None)