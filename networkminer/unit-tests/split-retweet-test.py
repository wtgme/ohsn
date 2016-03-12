# -*- coding: utf-8 -*-
"""
Created on Thu Jun 18 12:59:09 2015

@author: brendan
"""

# 'ascii' codec can't encode characters in position 91-92: ordinal not in range(128)

import re

def splitReTweetREGEX(text):
    pattern = re.compile('(.*)\s*RT\s*(.*):\s*(.*)', re.IGNORECASE)    
    #pattern = re.compile('/RT +@[^ :]+:?(.*)/ui', re.IGNORECASE)    
    match = pattern.match(text)
    print match.group(0)
    print match.group(1)
    print match.group(2)
    if match:
        # text = splitReTweet(match[0])
        return text        
    else:
        return text
        
def splitReTweet(text):
    bits = re.split('\s*(RT|retweet|MT|via)\s+@', text, 1)
    return bits[0]
#    try:
#        splitReTweet(bits)
#    except:
    
def splitReTweetMeh(text):
    pattern = re.compile('/RT +@[^ :]+:?(.*)/ui', re.IGNORECASE)    
    match = pattern.findall(text)
    print match
    if match: 
        return text        
    else:
        return text
        

def identifyManualRetweet(text):
    #r'\b(?:#|@|)[0-9]*%s[0-9]*\b'
    pattern = re.compile('\s*(RT|retweet|MT|via)\s*@', re.IGNORECASE)
    match = pattern.search(text)
    if match is None:
        return False
    else:
        print "SKIPPING RETWEET: " + text
        return True

def identifyRetweet(tweet):
# if its an official retweet ignore the tweet itself
    if tweet['interaction']['twitter']['retweeted_status'] is None:        
        # remember it may still be a manual retweet so look out for that in mineTweetText!!
        return identifyManualRetweet(tweet['interaction']['twitter']['text'])
    else:
            print "SKIPPING RETWEET: "
            print tweet
            return True
    
#tweettext = "RT HammerOfFacts: Our Society: Skinny = anorexic, thick = obese, virgin = too good, non-virgin = slut, friendly = fake, quiet = rude."
#
#print splitReTweet(tweettext)

tweettexts = [
"I hate using RT flappy",
"I hate this RT @flappy: fatty be like",
"@joe Our Society Skinny = anorexic, thick = obese, virgin = too good, non-virgin = slut, friendly = fake, quiet = rude via @frank",
]

for text in tweettexts:
    if identifyManualRetweet(text):
        # this doesn't work with via coming after....
        print splitReTweet(text)
    else:
        print text
    
#tweettext = "RT HammerOfFacts: Our Society Skinny = anorexic, thick = obese, virgin = too good, non-virgin = slut, friendly = fake, quiet = rude."
#
#splitReTweet(tweettext)

#def splitReTweet(text):
#    print "TODO"    
#    pattern = re.compile('/RT +@[^ :]+:?(.*)/ui', re.IGNORECASE)    
#    match = pattern.findall(text)
#    
#    if count($retweets) > 0:
#      # we have re-tweets
#      # $original = preg_replace("/^RT +@[^ :]+:? */ui", "", $tweet)
#    else:
#        return text;
#    
#      
#$id_str = false;
#        $id_str = db_result(db_query("SELECT id_str FROM tweets WHERE text = '%s'", $original));
#        $tag = ($id_str != false) ? '{RT:' . $id_str . '}' : '{RT}';
#        return preg_replace("/^RT/ui", $tag, $tweet);
