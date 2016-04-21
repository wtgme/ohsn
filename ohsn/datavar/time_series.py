# -*- coding: utf-8 -*-
"""
Created on 16:54, 21/04/16

@author: wt
"""


import pymongo
from ohsn.util import db_util as dbt
import pickle
import ohsn.lexiconsmaster.liwc_timeline_processor as liwcp
import ohsn.networkminer.timeline_network_miner as netp
import ohsn.textprocessor.description_miner as textp


def process(dbname, colname, range, index):
    yearsplit = pickle.load(open('data/tyear.pick', 'r'))
    processlist = []
    for key in yearsplit:
        if key in range:
            processlist += (yearsplit[key])
    db = dbt.db_connect_no_auth(dbname)
    timelines = db[colname]

    '''Create tempt collections'''
    tmpcom, tmptimeline, tmpnet, tmpbnet = 'com_t'+str(index), 'timeline_t'+str(index), 'net_t'+str(index), 'bnet_t'+str(index)
    comtem = db[tmpcom]
    comtem.create_index("id", unique=True)
    timetem = db[tmptimeline]
    timetem.create_index([('user.id', pymongo.ASCENDING),
                              ('id', pymongo.DESCENDING)])
    timetem.create_index([('id', pymongo.ASCENDING)], unique=True)
    nettem = db[tmpnet]
    nettem.create_index([("id0", pymongo.ASCENDING),
                                 ("id1", pymongo.ASCENDING),
                                 ("type", pymongo.ASCENDING),
                                 ("statusid", pymongo.ASCENDING)],
                                unique=True)

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
    process('fed', 'stimeline', [2009, 2010, 2011], 1)
    process('fed', 'stimeline', [2012], 2)
    process('fed', 'stimeline', [2013], 3)
    process('fed', 'stimeline', [2014], 4)
    process('fed', 'stimeline', [2015, 2016], 5)



