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
import pickle


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




def most_retweet(dbname, colname):
    '''find most frequently retweeted tweets'''
    db = dbt.db_connect_no_auth(dbname)
    timeline = db[colname]
    retweets, retweeters = {}, {}
    for status in timeline.find({'retweeted_status':{'$exists': True}}, ['retweeted_status']):
        twid = status['retweeted_status']['id']
        tweeid = status['retweeted_status']['user']['id']
        count = retweets.get(twid, 0)
        count += 1
        retweets[twid] = count
        count = retweeters.get(tweeid, 0)
        count += 1
        retweeters[tweeid] = count
    return retweets, retweeters


def most_entities(dbname, colname):
    '''find popular hashtag'''
    db = dbt.db_connect_no_auth(dbname)
    timeline = db[colname]
    tags, mentions = {}, {}
    for status in timeline.find():
        hashtags = status['entities']['hashtags']
        mens = status['entities']['user_mentions']
        # us = status['entities']['urls']
        if len(hashtags) > 0:
            for hashtag in hashtags:
                count = tags.get(hashtag['text'], 0)
                count += 1
                tags[hashtag['text']] = count
        if len(mens) > 0:
            for men in mens:
                count = mentions.get(men['id'], 0)
                count += 1
                mentions[men['id']] = count
    return tags, mentions



if __name__ == '__main__':
    '''how many tweets with each bahaviour'''
    # beh_stat('sed', 'timeline')
    # beh_stat('srd', 'timeline')
    # beh_stat('syg', 'timeline')

    '''retweet IDs and publishers' IDs of retweets'''
    edrt, edrte = most_retweet('sed', 'timeline')
    rdrt, rdrte = most_retweet('srd', 'timeline')
    ygrt, ygrte = most_retweet('syg', 'timeline')
    pickle.dump((edrt, edrte), open('data/edrt.pick', 'w'))
    pickle.dump((rdrt, rdrte), open('data/rdrt.pick', 'w'))
    pickle.dump((ygrt, ygrte), open('data/ugrt.pick', 'w'))
    edrt, edrte = pickle.load(open('data/edrt.pick', 'r'))
    rdrt, rdrte = pickle.load(open('data/rdrt.pick', 'r'))
    ygrt, ygrte = pickle.load(open('data/ugrt.pick', 'r'))
    print len(edrt), len(rdrt), len(ygrt)
    print sum(edrt.values()), sum(rdrt.values()), sum(ygrt.values())
    print float(sum(edrt.values()))/len(edrt), float(sum(rdrt.values()))/len(rdrt), float(sum(ygrt.values()))/len(ygrt)
    print len(edrte), len(rdrte), len(ygrte)
    print sum(edrte.values()), sum(rdrte.values()), sum(ygrte.values())
    print float(sum(edrte.values()))/len(edrte), float(sum(rdrte.values()))/len(rdrte), float(sum(ygrte.values()))/len(ygrte)

    plot.plot_pdf_mul_data([edrt.values(), rdrt.values(), ygrt.values()], ['--bo', '--r^', '--ks'], 'retweets',  ['ED', 'Random', 'Young'], False)
    plot.plot_pdf_mul_data([edrte.values(), rdrte.values(), ygrte.values()], ['--bo', '--r^', '--ks'], 'publishers of retweets',  ['ED', 'Random', 'Young'], False)

    # '''Hashtags in tweets'''
    # edtags, edments = most_entities('sed', 'timeline')
    # rdtags, rdments = most_entities('srd', 'timeline')
    # ygtags, ygments = most_entities('syg', 'timeline')
    # pickle.dump((edtags, edments), open('data/edtags.pick', 'w'))
    # pickle.dump((rdtags, rdments), open('data/rdtags.pick', 'w'))
    # pickle.dump((ygtags, ygments), open('data/ygtags.pick', 'w'))
    # print len(edtags), len(rdtags), len(ygtags)
    # print sum(edtags.values()), sum(rdtags.values()), sum(ygtags.values())
    # plot.plot_pdf_mul_data([edtags.values(), rdtags.values(), ygtags.values()], ['--bo', '--r^', '--ks'], 'Hashtags',  ['ED', 'Random', 'Young'], False)
    # plot.plot_pdf_mul_data([edments.values(), rdments.values(), ygments.values()], ['--bo', '--r^', '--ks'], 'Mentions',  ['ED', 'Random', 'Young'], False)