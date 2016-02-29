# -*- coding: utf-8 -*-
"""
Created on 8:15 PM, 2/27/16

@author: tw
Export data from mongodb for classification and feature analysis
"""
import sys
sys.path.append('..')
import util.db_util as dbt


def get_fields(x, fields):
    values = []
    for field in fields:
        # print x['id'], field
        if '.' in field:
            levels = field.split('.')
            t = x.get(levels[0])
            for level in levels[1:]:
                # print t
                t = t.get(level)
            values.append(t)
        else:
            values.append(x.get(field))
    return values


def liwc_feature_output(fields, file_name, dbname, label):
    with open(file_name+'.data', 'a') as fw:
        db = dbt.db_connect_no_auth(dbname)
        poi = db['com']

        index = 0
        maxsize = 3300
        exclude_set = set([4319191638L, 2627223434L, 2976822286L, 4788248335L, 3289264086L, 520847919, 439647015, 947539758, 617442479, 2481703728L, 2913311029L, 3760687289L, 2303011905L, 1712561862, 2882255303L, 261549132, 982895821, 2849269327L, 312684498, 160044558, 774072534, 330611545, 430569947, 1275228253, 3399616094L, 2924322143L, 457692129, 3006221026L, 2837359399L, 18942418, 2848241137L, 273768180, 235857269, 3315086840L])

        for x in poi.find({'liwc_anal.result.WC': {'$exists': True}},
                          ['id', 'liwc_anal.result']):
            if x['id'] not in exclude_set and index < maxsize:
                values = get_fields(x, fields)
                outstr = label + ' '
                for i in xrange(len(values)):
                    outstr += str(i+1)+':'+str(values[i])+' '
                index += 1
                fw.write(outstr+'\n')

LIWC = [
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
    'liwc_anal.result.AllPct']

# common users in random and young = set([4319191638L, 2627223434L, 2976822286L, 4788248335L, 3289264086L, 520847919, 439647015, 947539758, 617442479, 2481703728L, 2913311029L, 3760687289L, 2303011905L, 1712561862, 2882255303L, 261549132, 982895821, 2849269327L, 312684498, 160044558, 774072534, 330611545, 430569947, 1275228253, 3399616094L, 2924322143L, 457692129, 3006221026L, 2837359399L, 18942418, 2848241137L, 273768180, 235857269, 3315086840L])
# fed, random, young
liwc_feature_output(LIWC, 'data/rd-yg-liwc', 'young', '-1')


