# -*- coding: utf-8 -*-
"""
Created on 16:55, 19/04/16

@author: wt

retweet, mention, reply behaviour analysis
hashtag, retweet analysis
"""

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

from ohsn.util import db_util as dbt
import ohsn.util.plot_util as plot
from ohsn.util import statis_util
import ohsn.util.io_util as io
import pickle
import numpy as np


def get_one_value(diclist, field):
    values = []
    for data in diclist:
        value = data.get(field, 0.0)
        values.append(value)
    return values


def feature_stat(dumped=False):
    fields = io.read_fields()
    print len(fields)
    assert isinstance(fields, object)
    for field in fields:
        keys = field.split('.')
        filter = {field: {'$exists': True}}
        eds = io.get_values_one_field('fed', 'scom', field, filter)
        randoms = io.get_values_one_field('random', 'scom', field, filter)
        youngs = io.get_values_one_field('young', 'scom', field, filter)
        compore_distribution(keys[-1], eds, randoms, youngs)

    # field_name = 'liwc_anal.result'
    # filter = {'liwc_anal.result.WC': {'$exists': True}}
    # if dumped:
    #     edsa = pickle.load(open('data/fed_'+field_name+'.pick', 'r'))
    #     randomsa = pickle.load(open('data/random_'+field_name+'.pick', 'r'))
    #     youngsa = pickle.load(open('data/young_'+field_name+'.pick', 'r'))
    # else:
    #     edsa = io.get_values_one_field('fed', 'scom', field_name, filter)
    #     randomsa = io.get_values_one_field('random', 'scom', field_name, filter)
    #     youngsa = io.get_values_one_field('young', 'scom', field_name, filter)
    #     pickle.dump(edsa, open('data/fed_'+field_name+'.pick', 'w'))
    #     pickle.dump(randomsa, open('data/random_'+field_name+'.pick', 'w'))
    #     pickle.dump(youngsa, open('data/young_'+field_name+'.pick', 'w'))
    #
    # print len(edsa), len(randomsa), len(youngsa)
    # for field in fields:
    #     keys = field.split('.')
    #     eds = get_one_value(edsa, keys[-1])
    #     randoms = get_one_value(randomsa, keys[-1])
    #     youngs = get_one_value(youngsa, keys[-1])
    #     compore_distribution(keys[-1], eds, randoms, youngs)


def beh_stat(dbname, comname, colname, filename):
    db = dbt.db_connect_no_auth(dbname)
    com = db[comname]
    timeline = db[colname]
    tweet_all, retweet_all, dmention_all, udmention_all, reply_all, hashtag_all, url_all, quota_all, count_sum_all = \
        0, 0, 0, 0, 0, 0, 0, 0, 0
    user_staits = {}
    for user in com.find({}, ['id'], no_cursor_timeout=True):
        tweet, retweet, dmention, udmention, reply, hashtag, url, quota, count_sum = 0, 0, 0, 0, 0, 0, 0, 0, 0
        for status in timeline.find({'user.id': user['id']}, no_cursor_timeout=True):
            count_sum += 1
            count_sum_all += 1
            if 'retweeted_status' in status:
                retweet += 1
                retweet_all += 1
            else:
                tweet += 1
                tweet_all += 1
            if len(status['entities']['user_mentions']) > 0:
                udmention_list = []
                replyf, udmentionf, dmentionf = False, False, False
                # get user mentions in retweet
                if ('retweeted_status' in status) and len(status['retweeted_status']['entities']['user_mentions'])>0:
                    for udmention_item in status['retweeted_status']['entities']['user_mentions']:
                        udmention_list.append(udmention_item['id'])

                for mention in status['entities']['user_mentions']:
                    if ('in_reply_to_user_id' in status) and (mention['id'] == status['in_reply_to_user_id']): # reply
                        replyf = True
                    elif mention['id'] in udmention_list:  # mentions in Retweet content; undirected mention
                        udmentionf = True
                    else:  # original mentions; directed mention
                        dmentionf = True
                if replyf:
                    reply += 1
                    reply_all += 1
                if udmentionf:
                    udmention += 1
                    udmention_all += 1
                if dmentionf:
                    dmention += 1
                    dmention_all += 1
            if len(status['entities']['hashtags']) > 0:
                hashtag += 1
                hashtag_all += 1
            if len(status['entities']['urls']) > 0:
                url += 1
                url_all += 1
            if 'quoted_status' in status:
                quota += 1
                quota_all += 1
        user_staits[user['id']] = (tweet, retweet, dmention,
                                   udmention, reply, hashtag, url, quota, count_sum)
    user_staits[-1] = (tweet_all, retweet_all, dmention_all, udmention_all,
                       reply_all, hashtag_all, url_all, quota_all, count_sum_all)
    pickle.dump(user_staits, open('data/'+filename+'.pick', 'w'))
        # print tweet, retweet, dmention, udmention, reply, hashtag, url, quota, count_sum
        # print 'Tweet Ratio, ', tweet, float(tweet)/count_sum
        # print 'Rtweet Ratio, ', retweet, float(retweet)/count_sum
        # print 'DMention Ratio, ', dmention, float(dmention)/count_sum
        # print 'UDMention Ratio, ', udmention, float(udmention)/count_sum
        # print 'Reply Ratio, ', reply, float(reply)/count_sum
        # print 'Hashtag Ratio, ', hashtag, float(hashtag)/count_sum
        # print 'URL Ratio, ', url, float(url)/count_sum
        # print 'Quota Ratio, ', quota, float(quota)/count_sum


def store_ratio_behavoir(dbname, colname, filename):
    db = dbt.db_connect_no_auth(dbname)
    com = db[colname]
    stats = pickle.load(open('data/'+filename+'.pick', 'r'))
    del stats[-1]
    for id in stats.keys():
        values = stats[id]
        data = com.find_one({'id': id})
        behaviors = data.get('behavior', {})
        try:
            behaviors['tweet_pro'] = float(values[0])/values[-1]
            behaviors['retweet_pro'] = float(values[1])/values[-1]
            behaviors['dmention_pro'] = float(values[2])/values[-1]
            behaviors['udmention_pro'] = float(values[3])/values[-1]
            behaviors['reply_pro'] = float(values[4])/values[-1]
            behaviors['hashtag_pro'] = float(values[5])/values[-1]
            behaviors['url_pro'] = float(values[6])/values[-1]
            behaviors['quote_pro'] = float(values[7])/values[-1]
            com.update_one({'id': id}, {'$set': {'behavior': behaviors}}, upsert=False)
        except ZeroDivisionError:
            continue


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


def plot_distribution(edbev, rdbev, ygbev):
    eds = pickle.load(open('data/'+edbev+'.pick', 'r'))
    rds = pickle.load(open('data/'+rdbev+'.pick', 'r'))
    ygs = pickle.load(open('data/'+ygbev+'.pick', 'r'))
    print 'All statistics values, and ratios'
    print eds[-1]
    print rds[-1]
    print ygs[-1]
    print np.asarray(eds[-1], float)/eds[-1][-1]
    print np.asarray(rds[-1], float)/rds[-1][-1]
    print np.asarray(ygs[-1], float)/ygs[-1][-1]
    '''Remove overall statistics'''
    del eds[-1]
    del rds[-1]
    del ygs[-1]
    edvalues, rdvalues, ygvalues = np.asarray(eds.values(), float), \
                                   np.asarray(rds.values(), float), \
                                   np.asarray(ygs.values(), float)

    print edvalues.shape, rdvalues.shape, ygvalues.shape
    print 'Non zero values in all tweet numbers'
    print np.count_nonzero(edvalues[:, -1])
    print np.count_nonzero(rdvalues[:, -1])
    print np.count_nonzero(ygvalues[:, -1])

    print 'Remove all zero values'
    edvalues = edvalues[~np.all(edvalues == 0, axis=1)]
    rdvalues = rdvalues[~np.all(rdvalues == 0, axis=1)]
    ygvalues = ygvalues[~np.all(ygvalues == 0, axis=1)]

    print 'Calculate ratios for each behavior (column)'
    edvalues = edvalues/(edvalues[:, -1][:, None])
    rdvalues = rdvalues/(rdvalues[:, -1][:, None])
    ygvalues = ygvalues/(ygvalues[:, -1][:, None])

    # edvalues[~np.isfinite(edvalues)] = 0.0
    # rdvalues[~np.isfinite(rdvalues)] = 0.0
    # ygvalues[~np.isfinite(ygvalues)] = 0.0

    print edvalues.shape, rdvalues.shape, ygvalues.shape
    row, col = edvalues.shape
    fields = ['Tweet', 'Retweet', 'Mention', 'UDmention', 'Reply', 'Hashtag', 'URL', 'Quota']
    for i in xrange(col-1):
        feds = edvalues[:, i]
        randoms = rdvalues[:, i]
        youngs = ygvalues[:, i]
        field = fields[i]
        compore_distribution(field, feds, randoms, youngs)


def pvalue(p):
    s = ''
    if p < 0.01/97:
        s = '*'
    if p < 0.001/97:
        s = '**'
    if p < 0.0001/97:
        s = '***'
    return s


def compore_distribution(field, feds, randoms, youngs):
    # print '---------------Compare ' + field + '---------------------'
    edcomm = statis_util.comm_stat(feds)
    rdcomm = statis_util.comm_stat(randoms)
    ygcomm = statis_util.comm_stat(youngs)
    ed_rdz = statis_util.ks_test(randoms, feds)
    ed_ygz = statis_util.ks_test(youngs, feds)
    yg_rdz = statis_util.ks_test(youngs, randoms)
    # if min(ed_rdz[2], ed_ygz[2])>yg_rdz[2]:
    print '%s & %.2f($\sigma$=%.2f) & %.2f($\sigma$=%.2f) & %.2f($\sigma$=%.2f) & %.2f%s & %.2f%s & %.2f%s \\\\' \
          % (field, edcomm[2], edcomm[3], rdcomm[2], rdcomm[3], ygcomm[2], ygcomm[3], ed_rdz[2],
             pvalue(ed_rdz[3]), ed_ygz[2], pvalue(ed_ygz[3]), yg_rdz[2], pvalue(yg_rdz[3]))

    # print 'ED & ' + str(edcomm[0]) + ' & ' + str(edcomm[1]) \
    #       + ' & ' + str(edcomm[2]) + ' & ' + str(edcomm[3]) + '\\\\'
    # print 'Random &' + str(rdcomm[0]) + ' & ' + str(rdcomm[1]) \
    #       + ' & ' + str(rdcomm[2]) + ' & ' + str(rdcomm[3]) + '\\\\'
    # print 'Younger &' + str(ygcomm[0]) + ' & ' + str(ygcomm[1]) \
    #       + ' & ' + str(ygcomm[2]) + ' & ' + str(ygcomm[3]) + '\\\\'
    # print '\\hline'
    # print 'ks-test(Random, ED): & $n_1$: ' + str(ed_rdz[0]) + ' & $n_2$: ' + str(ed_rdz[1]) \
    #       + ' & ks-value: ' + str(ed_rdz[2]) + ' & p-value: ' + str(ed_rdz[3]) + '\\\\'
    # print 'ks-test(Younger, ED): & $n_1$: ' + str(ed_ygz[0]) + ' & $n_2$: ' + str(ed_ygz[1]) \
    #       + ' & ks-value: ' + str(ed_ygz[2]) + ' & p-value: ' + str(ed_ygz[3]) + '\\\\'
    # print 'ks-test(Younger, Random): & $n_1$: ' + str(yg_rdz[0]) + ' & $n_2$: ' + str(yg_rdz[1]) \
    #       + ' & ks-value: ' + str(yg_rdz[2]) + ' & p-value: ' + str(yg_rdz[3]) + '\\\\'

    plot.plot_pdf_mul_data([feds, randoms, youngs], field, ['--g', '--b', '--r'], ['s', 'o', '^'],
                           ['ED', 'Random', 'Younger'],
                           linear_bins=True, central=True, fit=False, fitranges=None, savefile=field + '.pdf')


if __name__ == '__main__':
    '''how many tweets with each bahaviour'''
    # beh_stat('fed', 'com', 'timeline', 'fedbev')
    # beh_stat('random', 'scom', 'timeline', 'rdbev')
    # beh_stat('young', 'scom', 'timeline', 'ygbev')

    # store_ratio_behavoir('fed', 'com', 'fedbev')
    # store_ratio_behavoir('random', 'scom', 'rdbev')
    # store_ratio_behavoir('young', 'scom', 'ygbev')

    '''Plot distribution of bahavior ratio'''
    # plot_distribution('edbev', 'rdbev', 'ygbev')

    '''retweet IDs and publishers' IDs of retweets'''
    # edrt, edrte = most_retweet('sed', 'timeline')
    # rdrt, rdrte = most_retweet('srd', 'timeline')
    # ygrt, ygrte = most_retweet('syg', 'timeline')
    # pickle.dump((edrt, edrte), open('data/edrt.pick', 'w'))
    # pickle.dump((rdrt, rdrte), open('data/rdrt.pick', 'w'))
    # pickle.dump((ygrt, ygrte), open('data/ugrt.pick', 'w'))
    # edrt, edrte = pickle.load(open('data/edrt.pick', 'r'))
    # rdrt, rdrte = pickle.load(open('data/rdrt.pick', 'r'))
    # ygrt, ygrte = pickle.load(open('data/ugrt.pick', 'r'))
    # print len(edrt), len(rdrt), len(ygrt)
    # print sum(edrt.values()), sum(rdrt.values()), sum(ygrt.values())
    # print float(sum(edrt.values()))/len(edrt), float(sum(rdrt.values()))/len(rdrt), float(sum(ygrt.values()))/len(ygrt)
    # print len(edrte), len(rdrte), len(ygrte)
    # print sum(edrte.values()), sum(rdrte.values()), sum(ygrte.values())
    # print float(sum(edrte.values()))/len(edrte), float(sum(rdrte.values()))/len(rdrte), float(sum(ygrte.values()))/len(ygrte)
    #
    # plot.plot_pdf_mul_data([edrt.values(), rdrt.values(), ygrt.values()], ['--bo', '--r^', '--ks'], 'retweets',  ['ED', 'Random', 'Young'], False)
    # plot.plot_pdf_mul_data([edrte.values(), rdrte.values(), ygrte.values()], ['--bo', '--r^', '--ks'], 'publishers of retweets',  ['ED', 'Random', 'Young'], False)

    '''Hashtags in tweets'''
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

    # '''compare Distributions of LIWC features'''
    feature_stat()