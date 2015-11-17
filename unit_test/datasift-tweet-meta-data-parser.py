# -*- coding: utf-8 -*-
"""
Created on Tue Jun 16 09:16:05 2015
@author: brendan
"""


# backup/copy the datasift collections to the local machine
# DONE


# create a unique index on the tweet id set dropDups to True
# this will rid us of duplicate tweets
db.things.createIndex({'interaction.twitter.id' : 1}, {unique : true, dropDups : true})

# parse each collection




# Export something for R to chomp?

#  


# obs have the following structure:
# we add a list of these to every tweet we parse

# we can select * from tweets where obs = None

# copy the datasift collections to the local server...

# this is already in the tweet but replicate it and fix the id
obs['screen_name'] = screen_name
obs['id_str'] = ''
if id < 0:
obs['id'] = 
obs['tweeted_at'] =

obs['parser_version']
obs['dateparsed']
# where the text came from 
obs['obs_type'] = ['screen_name', 'description', 'tweettext']
# the text we parsed
obs['text'] = text
# observations  
obs['age'] = ''
obs['height'] = ''
obs['hw'] = ''
obs['lw'] = ''
obs['cw'] = ''
obs['gw'] = ''
obs['cw_bmi'] = ''
obs['gw_bmi'] = ''
}

# we can add to this later, we will probably rerun with different parsers as we go along.
# go through all the ones that were parsed with an out-of date version:
    
find( tweet['description_parsed']['parser_version'] < CURRRENTVERSION:)
find the ones that haven't been parsed

	for tweet in tweets:
           # fix users with mangled ids
           do that    		
            # process the description
		obs = processdescription()
    		# save obs description to the tweet
      
['interaction']['echelon']['obs']['description']

           db.foo.update({"_id" :ObjectId("4e93037bbf6f1dd3a0a9541a") },{$set : {"new_field":1}})
		# only if the content is the authors! do you parse the tweet content
		users_content = getuserscontent(tweet.text)
		obs = processtweet()
            # save obs tweet to the tweet
['interaction']['echelon']['obs']['tweettext']

           db.foo.update({"_id" :ObjectId("4e93037bbf6f1dd3a0a9541a") },{$set : {"new_field":1}})
   
   