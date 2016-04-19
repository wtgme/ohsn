# -*- coding: utf-8 -*-
"""
Created on 16:55, 19/04/16

@author: wt

retweet, mention, reply behaviour analysis
hashtag, retweet analysis
"""

import sys
sys.path.append('..')
import util.db_util as dbt
import util.plot_util as plot



def beh_stat(dbname, colname):
    db = dbt.db_connect_no_auth(dbname)
    timeline = db[colname]
    count_sum = timeline.count()
    tweet, retweet, mention, reply = 0, 0, 0, 0
    for status in timeline.find({}):
        if 'retweeted_status' in status:
            retweet += 1
        else:
            tweet += 1
        if status['in_reply_to_user_id']:
            reply += 1
        if len(status['entities']['user_mentions']) > 0:
            mention += 1
    print tweet, retweet, mention, reply, count_sum
    print float(tweet)/count_sum, float(retweet)/count_sum, float(mention)/count_sum, float(reply)/count_sum




def most_retweet():
    '''find most frequently retweeted tweets'''



def most_hashtag():
    '''find popular hashtag'''



def most_mention():
    '''find popular users'''

beh_stat('sed', 'timeline')
beh_stat('srd', 'timeline')
beh_stat('syg', 'timeline')
