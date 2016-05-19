# -*- coding: utf-8 -*-
"""
Created on 16:54, 21/04/16

@author: wt
1. active.py split timeline by years
2. time_series.py split timelines (as well as the users posting timelines) into sperate collection
    processing with LIWC, behaviour network extaction, and bio information extraction
3. keyplay.py obtain subnets (behavior and friendship) within the coms. calculte centrality included in nets_agg.py
4. description_minier.py calculate cbmi and gbmi
5. nets_agg.py calculate network statistics
6. friend_pro.py calcuate how many friends are ED
5. export_csv.py output files
"""

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import pymongo
from ohsn.util import db_util as dbt
import pickle
import ohsn.lexiconsmaster.liwc_timeline_processor as liwcp
import ohsn.networkminer.timeline_network_miner as netp
import ohsn.textprocessor.description_miner as textp
import ohsn.networkminer.keyplay as keyp
import ohsn.networkminer.nets_agg as netagg
import ohsn.networkminer.friend_pro as fridp
import activity
from datetime import datetime


def timeline(dbname, colname):
    db = dbt.db_connect_no_auth(dbname)
    timeline = db[colname]
    tlist = []
    for status in timeline.find():
        ts = datetime.strptime(status['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
        tlist.append(ts)
    return tlist


def transform_data(dbname, colname, newdbname, newcolname, timeend):
    dbo = dbt.db_connect_no_auth(dbname)
    timeo = dbo[colname]
    dbn = dbt.db_connect_no_auth(newdbname)
    timen = dbn[newcolname]
    timen.create_index([('user.id', pymongo.ASCENDING),
                          ('id', pymongo.DESCENDING)])
    timen.create_index([('id', pymongo.ASCENDING)], unique=True)
    for status in timeo.find():
        ts = datetime.strptime(status['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
        if ts <= timeend:
            timen.insert(status)


def transform_net_data(dbname, colname, newdbname, newcolname):
    dbo = dbt.db_connect_no_auth(dbname)
    neto = dbo[colname]
    dbn = dbt.db_connect_no_auth(newdbname)
    netn = dbn[newcolname]
    netn.create_index([("user", pymongo.ASCENDING),
                    ("follower", pymongo.ASCENDING),
                     ("type", pymongo.ASCENDING)],
                            unique=True)
    for status in neto.find({'scraped_times':1}):
        netn.insert(status)


def process(dbname, colname, range, index, f=''):
    yearsplit = pickle.load(open('data/fedtyear.pick', 'r'))
    processlist = []
    for key in yearsplit:
        if key in range:
            processlist += (yearsplit[key])

    db = dbt.db_connect_no_auth(dbname)
    timelines = db[colname]

    '''Create tempt collections'''
    tmpcom, tmptimeline, tmpbnet, tmpsfnet, tmpsbnet = f+'com_t'+str(index), f+'timeline_t'+str(index), \
                                                     f+'bnet_t'+str(index), f+'snet_t'+str(index), f+'sbnet_t'+str(index)

    comtem = db[tmpcom]
    comtem.create_index("id", unique=True)
    tmptimeline = 'temp_timeline'
    timetem = db[tmptimeline]
    if timetem.count() != 0:
        timetem.drop()
        timetem = db[tmptimeline]
    timetem.create_index([('user.id', pymongo.ASCENDING),
                              ('id', pymongo.DESCENDING)])
    timetem.create_index([('id', pymongo.ASCENDING)], unique=True)

    for tid in processlist:
        # print tid
        status = timelines.find_one({'id': tid}, timeout=False)
    #     # print status
    # for status in timelines.find({}, no_cursor_timeout=True):
        ts = datetime.strptime(status['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
        if ts.year in range:
            try:
                timetem.insert(status)
            except pymongo.errors.DuplicateKeyError:
                pass
            user = status['user']
            user['level'] = 1
            user['timeline_count'] = timetem.count({'user.id': user['id']})
            comtem.replace_one({'id': user['id']}, user, upsert=True)

    analysis(dbname, tmpbnet, tmpcom, tmpsbnet, tmpsfnet, tmptimeline)


def analysis(dbname, tmpbnet, tmpcom, tmpsbnet, tmpsfnet, tmptimeline):
    liwcp.process_db(dbname, tmpcom, tmptimeline)
    netp.process_db(dbname, tmpcom, tmptimeline, tmpbnet, 10000)
    textp.process_poi(dbname, tmpcom)
    keyp.subnetworks(dbname, tmpcom, 'net', tmpbnet, tmpsfnet, tmpsbnet)
    netagg.nets_stats(dbname, tmpcom, tmpsfnet, tmpsbnet)


if __name__ == '__main__':
    # dbname, tmpcom, tmptimeline, tmpbnet = 'tyg', 'com', 'timeline', 'bnet'
    # liwcp.process_db(dbname, tmpcom, tmptimeline)
    # netp.process_db(dbname, tmpcom, tmptimeline, tmpbnet, 10000)
    # textp.process_poi(dbname, tmpcom)

    '''Core ED'''
    yearsplit = activity.timeline_split('fed', 'timeline')
    pickle.dump(yearsplit, open('data/fedtyear.pick', 'w'))
    # dbname, tmpcom, tmptimeline, tmpbnet = 'fed', 'com', 'timeline', 'fedbnet'
    # analysis(dbname, tmpbnet, tmpcom, 'fedsbnet', 'fedsnet', tmptimeline)
    # fridp.ed_pro(dbname, 'scom', tmpcom, 'net')
    # process('fed', 'timeline', [2009, 2010, 2011], 1, 'fed')
    process('fed', 'timeline', [2012], 2, 'fed')
    process('fed', 'timeline', [2013], 3, 'fed')
    process('fed', 'timeline', [2014], 4, 'fed')
    process('fed', 'timeline', [2015, 2016], 5, 'fed')

    '''YG data'''
    # process('tyg', 'timeline', [2009, 2010, 2011], 1, 'data/ygtyear.pick')
    # process('tyg', 'timeline', [2012], 2, 'data/ygtyear.pick')
    # process('tyg', 'timeline', [2013], 3, 'data/ygtyear.pick')
    # process('tyg', 'timeline', [2014], 4, 'data/ygtyear.pick')
    # process('tyg', 'timeline', [2015, 2016], 5, 'data/ygtyear.pick')

    # transform_net_data('dyg', 'net', 'tyg', 'net')
    # tlist = timeline('fed', 'stimeline')
    # transform_data('dyg', 'timeline', 'tyg', 'timeline', max(tlist))
