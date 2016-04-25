# -*- coding: utf-8 -*-
"""
Created on 15:51, 19/11/15
CSV cannot recognize dic{{}}, this module is discarded, using mongochef to export
@author: wt
"""

import db_util as dbutil
import csv


def csv_output(fields, file_name, data):
    with open(file_name+'.csv', 'wb') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(fields)
        for x in data:
            values = []
            for field in fields:
                # print field
                if '.' in field:
                    levels = field.split('.')
                    t = x.get(levels[0])
                    for level in levels[1:]:
                        # print t
                        t = t.get(level)
                        if t is None:
                            break
                    values.append(t)
                else:
                    values.append(x.get(field))
            proce_values = []
            for s in values:
                s = unicode(s).encode("utf-8").replace('\t', ' ').replace(';', ' ').replace(',', ' ').replace('\n', ' ').replace('\r', ' ').replace('\r\n', ' ').replace('\n\r', ' ')
                if s == 'None':
                    s = ''
                proce_values.append(s)
            writer.writerow(proce_values)


def export_poi(dbname, colname, file_name, lev=1):
    db = dbutil.db_connect_no_auth(dbname)
    poidb = db[colname]
    fields = ['id',
              'name',
              "screen_name",
              'created_at',
              'timeline_count',
              'lang',
              'location',
              'level',
              'geo_enabled',
              'followers_count',
              'friends_count',
              'statuses_count',
              'retweet_count',
              'favourites_count',
              'dc',
              'ng',
              'time_zone',
              'verified',
              'description',
              'text_anal.gw.value',
              'text_anal.cw.value',
              'text_anal.lw.value',
              'text_anal.hw.value',
              'text_anal.h.value',
              'text_anal.a.value',
              'text_anal.bmi.value',
              'text_anal.cbmi.value',
              'text_anal.gbmi.value',
              'text_anal.edword_count.value',
              'liwc_anal.result.WC',
              'liwc_anal.result.WPS',
              'liwc_anal.result.Sixltr',
              'liwc_anal.result.Dic',
              'liwc_anal.result.Numerals',
              'liwc_anal.result.funct',
              'liwc_anal.result.pronoun',
              'liwc_anal.result.ppron',
              'liwc_anal.result.i',
              'liwc_anal.result.we',
              'liwc_anal.result.you',
              'liwc_anal.result.shehe',
              'liwc_anal.result.they',
              'liwc_anal.result.ipron',
              'liwc_anal.result.article',
              'liwc_anal.result.verb',
              'liwc_anal.result.auxverb',
              'liwc_anal.result.past',
              'liwc_anal.result.present',
              'liwc_anal.result.future',
              'liwc_anal.result.adverb',
              'liwc_anal.result.preps',
              'liwc_anal.result.conj',
              'liwc_anal.result.negate',
              'liwc_anal.result.quant',
              'liwc_anal.result.number',
              'liwc_anal.result.swear',
              'liwc_anal.result.social',
              'liwc_anal.result.family',
              'liwc_anal.result.friend',
              'liwc_anal.result.humans',
              'liwc_anal.result.affect',
              'liwc_anal.result.posemo',
              'liwc_anal.result.negemo',
              'liwc_anal.result.anx',
              'liwc_anal.result.anger',
              'liwc_anal.result.sad',
              'liwc_anal.result.cogmech',
              'liwc_anal.result.insight',
              'liwc_anal.result.cause',
              'liwc_anal.result.discrep',
              'liwc_anal.result.tentat',
              'liwc_anal.result.certain',
              'liwc_anal.result.inhib',
              'liwc_anal.result.incl',
              'liwc_anal.result.excl',
              'liwc_anal.result.percept',
              'liwc_anal.result.see',
              'liwc_anal.result.hear',
              'liwc_anal.result.feel',
              'liwc_anal.result.bio',
              'liwc_anal.result.body',
              'liwc_anal.result.health',
              'liwc_anal.result.sexual',
              'liwc_anal.result.ingest',
              'liwc_anal.result.relativ',
              'liwc_anal.result.motion',
              'liwc_anal.result.space',
              'liwc_anal.result.time',
              'liwc_anal.result.work',
              'liwc_anal.result.achieve',
              'liwc_anal.result.leisure',
              'liwc_anal.result.home',
              'liwc_anal.result.money',
              'liwc_anal.result.relig',
              'liwc_anal.result.death',
              'liwc_anal.result.assent',
              'liwc_anal.result.nonfl',
              'liwc_anal.result.filler',
              'liwc_anal.result.Period',
              'liwc_anal.result.Comma',
              'liwc_anal.result.Colon',
              'liwc_anal.result.SemiC',
              'liwc_anal.result.QMark',
              'liwc_anal.result.Exclam',
              'liwc_anal.result.Dash',
              'liwc_anal.result.Quote',
              'liwc_anal.result.Apostro',
              'liwc_anal.result.Parenth',
              'liwc_anal.result.OtherP',
              'liwc_anal.result.AllPct'
              ]
    data = [x for x in poidb.find({'timeline_count':{'$gt':0}}, projection=fields)]
    csv_output(fields, file_name, data)


def export_net_agg(dbname, comname, colname, file_name):
    db = dbutil.db_connect_no_auth(dbname)
    net = db[colname]
    fields = ['id0', 'id1', 'type', 'count']
    ttypes = {1: 'retweet', 2: 'reply', 3: 'mention'}

    '''Only include poi users'''
    data = []
    tems = {}
    for re in net.find({"type": {'$in': [1, 2, 3]}}):
        id0 = re['id0']
        id1 = re['id1']
        typeid = re['type']
        if id0 != id1:
            count = tems.get((id0, id1, typeid), 0)
            tems[(id0, id1, typeid)] = count+1

    for id0, id1, typeid in tems.keys():
        data.append({'id0': id0, 'id1': id1, 'type': ttypes[typeid], 'count': tems[(id0, id1, typeid)]})
    csv_output(fields, file_name, data)


def export_poi_echelon(dbname,colname, file_name):
    db = dbutil.db_connect_no_auth(dbname)
    poidb = db[colname]
    fields = ['id',
            'screen_name',
            'datetime_joined_twitter',
            'description',
            'follower_auth_error_flag',
            'timeline_auth_error_flag',
            'lang',
            'location',
            'ds_gender',
            'text_anal.gw.value',
            'text_anal.cw.value',
            'text_anal.edword_count.value',
            'text_anal.h.value',
            'text_anal.a.value',
            'text_anal.lw.value',
            'text_anal.hw.value',
            'rliwc_anal.result.WC',
            'rliwc_anal.result.WPS',
            'rliwc_anal.result.Sixltr',
            'rliwc_anal.result.Dic',
            'rliwc_anal.result.Numerals',
            'rliwc_anal.result.funct',
            'rliwc_anal.result.pronoun',
            'rliwc_anal.result.ppron',
            'rliwc_anal.result.i',
            'rliwc_anal.result.we',
            'rliwc_anal.result.you',
            'rliwc_anal.result.shehe',
            'rliwc_anal.result.they',
            'rliwc_anal.result.ipron',
            'rliwc_anal.result.article',
            'rliwc_anal.result.verb',
            'rliwc_anal.result.auxverb',
            'rliwc_anal.result.past',
            'rliwc_anal.result.present',
            'rliwc_anal.result.future',
            'rliwc_anal.result.adverb',
            'rliwc_anal.result.preps',
            'rliwc_anal.result.conj',
            'rliwc_anal.result.negate',
            'rliwc_anal.result.quant',
            'rliwc_anal.result.number',
            'rliwc_anal.result.swear',
            'rliwc_anal.result.social',
            'rliwc_anal.result.family',
            'rliwc_anal.result.friend',
            'rliwc_anal.result.humans',
            'rliwc_anal.result.affect',
            'rliwc_anal.result.posemo',
            'rliwc_anal.result.negemo',
            'rliwc_anal.result.anx',
            'rliwc_anal.result.anger',
            'rliwc_anal.result.sad',
            'rliwc_anal.result.cogmech',
            'rliwc_anal.result.insight',
            'rliwc_anal.result.cause',
            'rliwc_anal.result.discrep',
            'rliwc_anal.result.tentat',
            'rliwc_anal.result.certain',
            'rliwc_anal.result.inhib',
            'rliwc_anal.result.incl',
            'rliwc_anal.result.excl',
            'rliwc_anal.result.percept',
            'rliwc_anal.result.see',
            'rliwc_anal.result.hear',
            'rliwc_anal.result.feel',
            'rliwc_anal.result.bio',
            'rliwc_anal.result.body',
            'rliwc_anal.result.health',
            'rliwc_anal.result.sexual',
            'rliwc_anal.result.ingest',
            'rliwc_anal.result.relativ',
            'rliwc_anal.result.motion',
            'rliwc_anal.result.space',
            'rliwc_anal.result.time',
            'rliwc_anal.result.work',
            'rliwc_anal.result.achieve',
            'rliwc_anal.result.leisure',
            'rliwc_anal.result.home',
            'rliwc_anal.result.money',
            'rliwc_anal.result.relig',
            'rliwc_anal.result.death',
            'rliwc_anal.result.assent',
            'rliwc_anal.result.nonfl',
            'rliwc_anal.result.filler',
            'rliwc_anal.result.Period',
            'rliwc_anal.result.Comma',
            'rliwc_anal.result.Colon',
            'rliwc_anal.result.SemiC',
            'rliwc_anal.result.QMark',
            'rliwc_anal.result.Exclam',
            'rliwc_anal.result.Dash',
            'rliwc_anal.result.Quote',
            'rliwc_anal.result.Apostro',
            'rliwc_anal.result.Parenth',
            'rliwc_anal.result.OtherP',
            'rliwc_anal.result.AllPct',
            ]
    cursor = poidb.find({}, projection=fields)
    csv_output(fields, file_name, cursor)


if __name__ == '__main__':
    export_poi('fed', 'scom', 'poi')
    export_poi('fed', 'com_t1', 'poi_t1')
    export_poi('fed', 'com_t2', 'poi_t2')
    export_poi('fed', 'com_t3', 'poi_t3')
    export_poi('fed', 'com_t4', 'poi_t4')
    export_poi('fed', 'com_t5', 'poi_t5')
    # export_net_agg('fed', 'com_t1', 'sbnet_t1', 'bnet_t1')
    # export_net_agg('fed', 'com_t2', 'sbnet_t2', 'bnet_t2')
    # export_net_agg('fed', 'com_t3', 'sbnet_t3', 'bnet_t3')
    # export_net_agg('fed', 'com_t4', 'sbnet_t4', 'bnet_t4')
    # export_net_agg('fed', 'com_t5', 'sbnet_t5', 'bnet_t5')

    # export_poi_echelon('echelon', 'poi', 're_echelon_poi')
    # export_poi('ed', 'poi_ed', 'ed_poi', 9)
    # export_poi('stream', 'poi_track', 'track_poi')

    # export_net_agg('echelon', 'mrredges_aggregated', 're_echelon_reply_mention')
    # export_net_agg('stream', 'net_track_aggregated', 'track_reply_mention')
    # export_net_agg('stream', 'net_track_aggregated', 'track_reply_mention')



    # db = dbutil.db_connect_no_auth('echelon')
    # poidb = db['mrredges_aggregated']
    # print poidb.count({"relationship": {'$in': ['mentioned', 'reply-to']}})
    # print poidb.count({"relationship": 'mentioned'}) + poidb.count({"relationship":  'reply-to'})

    # data = poidb.find({},{'id':1,
    #                             'screen_name':1,
    #                             'datetime_joined_twitter':1,
    #                             'text_anal.gw.value':1}).limit(2)
    # print data
