# -*- coding: utf-8 -*-
"""
Created on 16:54, 21/04/16

@author: wt
1. active.py split timeline by years
2. time_series.py split timelines (as well as the users posting timelines) into sperate collection
    processing with LIWC, behaviour network extaction, and bio information extraction
3. keyplay.py calculte centrality
4. description_minier.py calculate cbmi and gbmi
6. nets_agg.py calculate network statistics
5. export_csv.py output files
"""


import pymongo
from ohsn.util import db_util as dbt
import pickle
import ohsn.lexiconsmaster.liwc_timeline_processor as liwcp
import ohsn.networkminer.timeline_network_miner as netp
import ohsn.textprocessor.description_miner as textp
from datetime import datetime, timedelta


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


def process(dbname, colname, range, index, filename):
    yearsplit = pickle.load(open(filename, 'r'))
    processlist = []
    for key in yearsplit:
        if key in range:
            processlist += (yearsplit[key])
    db = dbt.db_connect_no_auth(dbname)
    timelines = db[colname]

    '''Create tempt collections'''
    tmpcom, tmptimeline, tmpbnet = 'com_t'+str(index), 'timeline_t'+str(index), 'bnet_t'+str(index)
    comtem = db[tmpcom]
    comtem.create_index("id", unique=True)
    timetem = db[tmptimeline]
    timetem.create_index([('user.id', pymongo.ASCENDING),
                              ('id', pymongo.DESCENDING)])
    timetem.create_index([('id', pymongo.ASCENDING)], unique=True)

    for tid in processlist:
        # print tid
        status = timelines.find_one({'id': tid})
        # print status
        try:
            timetem.insert(status)
        except pymongo.errors.DuplicateKeyError:
            pass
        user = status['user']
        user['level'] = 1
        user['timeline_count'] = timetem.count({'user.id': user['id']})
        comtem.replace_one({'id': user['id']}, user, upsert=True)

    liwcp.process_db(dbname, tmpcom, tmptimeline)
    netp.process_db(dbname, tmpcom, tmptimeline, tmpbnet, 10000)
    textp.process_poi(dbname, tmpcom)


if __name__ == '__main__':
    # process('fed', 'stimeline', [2009, 2010, 2011], 1)
    # process('fed', 'stimeline', [2012], 2)
    # process('fed', 'stimeline', [2013], 3)
    # process('fed', 'stimeline', [2014], 4)
    # process('fed', 'stimeline', [2015, 2016], 5)

    process('tyg', 'timeline', [2009, 2010, 2011], 1, 'data/ygtyear.pick')
    process('tyg', 'timeline', [2012], 2, 'data/ygtyear.pick')
    process('tyg', 'timeline', [2013], 3, 'data/ygtyear.pick')
    process('tyg', 'timeline', [2014], 4, 'data/ygtyear.pick')
    process('tyg', 'timeline', [2015, 2016], 5, 'data/ygtyear.pick')

    # tlist = timeline('fed', 'stimeline')
    # transform_data('dyg', 'timeline', 'tyg', 'timeline', max(tlist))



