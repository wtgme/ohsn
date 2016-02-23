# -*- coding: utf-8 -*-
"""
Created on 13:56, 18/02/16

@author: wt

Compare the difference from their profile information


Background color ----> "profile_background_color": "EBEBEB"
Theme color ----> "profile_link_color": "990000"
"""

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
import util.db_util as dbt
import pymongo
import networkx as nx
import util.plot_util as plot
import math
from colormath.color_objects import LabColor, sRGBColor, AdobeRGBColor
from colormath.color_diff import delta_e_cie2000
from colormath.color_conversions import convert_color
import pickle
from util import statis_util


def get_field_values(db_name, field):
    db = dbt.db_connect_no_auth(db_name)
    poi = db['com']
    counts = []
    for user in poi.find({'level': 1}, [field]):
        counts.append(user[field])
    return counts


def get_mlvs_field_values(db_name, flag, field):
    db = dbt.db_connect_no_auth(db_name)
    poi = db['com']
    counts = []
    tag_names = field.split('.')
    for v in poi.find({'level': 1, flag: {'$exists': True}}, [field]):
        # print v
        counts.append(v[tag_names[0]][tag_names[1]])
    return counts


def get_sublevel_values(results, field):
    values = []
    for result in results:
        values.append(result[field])
    return values


def color_wheel():
    color_list = []
    with open('color.list') as fo:
        lines = fo.readlines()
        for i in xrange(len(lines)/3):
            color_list.append(labc([float(line.strip()) for line in lines[3*i:3*i+3]]))
    return color_list


def labc(clist):
    return LabColor(clist[0], clist[1], clist[2], illuminant='d50')


def srgbc(rgbv):
    return sRGBColor(float(int(rgbv[0:2], 16)), float(int(rgbv[2:4], 16)), float(int(rgbv[4:6], 16)), is_upscaled=True)


def cate_color(colors, standards):
    color_index = []
    for color in colors:
        rgb = srgbc(color)
        lab = convert_color(rgb, LabColor, target_illuminant='d50')
        mindis, minindex = 10000, 0
        for index in xrange(len(standards)):
            distance = delta_e_cie2000(lab, standards[index])
            if distance < mindis:
                mindis = distance
                minindex = index + 1
        # print mindis, minindex
        color_index.append(minindex)
    return color_index


def most_common(lst):
    return max(set(lst), key=lst.count)


def rgbstandards(standards):
    rgblist = []
    for lab in standards:
        rgb = convert_color(lab, sRGBColor, target_illuminant='d50')
        rgblist.append(rgb.get_rgb_hex())
    return rgblist


def rmdefault(clist):
    # Theme color: 0084B4 Background color: C0DEED
    return [co for co in clist if co!='0084B4']


def color_dis(dbname, colorname):
    background = get_field_values(dbname, colorname)
    print most_common(background)
    standers = color_wheel()
    return cate_color(background, standers)


def color_compare():
    standers = color_wheel()
    # print cate_color(['C0DEED'], standers)
    rgbstan = rgbstandards(standers)
    rgbstan[-1] = '#FFFFFF'

    # randomc = get_field_values('random', 'profile_link_color')
    # youngc = get_field_values('young', 'profile_link_color')
    # fedc = get_field_values('fed', 'profile_link_color')
    # pickle.dump(randomc, open("randomc.p", "wb"))
    # pickle.dump(youngc, open("youngc.p", "wb"))
    # pickle.dump(fedc, open("fedc.p", "wb"))

    randomc = pickle.load(open("randomc.p", "rb"))
    youngc = pickle.load(open("youngc.p", "rb"))
    fedc = pickle.load(open("fedc.p", "rb"))

    randomc = rmdefault(randomc)
    youngc = rmdefault(youngc)
    fedc = rmdefault(fedc)

    randomci = cate_color(randomc, standers)
    youngci = cate_color(youngc, standers)
    fedci = cate_color(fedc, standers)

    plot.color_bars(rgbstan, fedci)

    # plot.plot_pdf_two_data(randomc, fedc)

    # plot.plot_pdf_mul_data([randomc, youngc, fedc], ['--bo', '--r*', '--k+'], ['random', 'younger', 'ed'])

    # http://stackoverflow.com/questions/14095849/calculating-the-analogous-color-with-python


def feature_stat():
    fields = ['followers_count', 'friends_count', 'favourites_count', 'statuses_count']
    fields = ['liwc_anal.result.WC',
              'liwc_anal.result.WPS',
              'liwc_anal.result.Sixltr',
              'liwc_anal.result.Dic',
              # 'liwc_anal.result.Numerals',
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
    fedsa = get_mlvs_field_values('fed', 'liwc_anal.result.WC', 'liwc_anal.result')
    randomsa = get_mlvs_field_values('random', 'liwc_anal.result.WC', 'liwc_anal.result')
    youngsa = get_mlvs_field_values('young', 'liwc_anal.result.WC', 'liwc_anal.result')
    for field in fields:
        print '=====================', field
        keys = field.split('.')
        feds = get_sublevel_values(fedsa, keys[2])
        randoms = get_sublevel_values(randomsa, keys[2])
        youngs = get_sublevel_values(youngsa, keys[2])

        comm = statis_util.comm_stat(feds)
        print 'ED & ' + str(comm[0]) + ' & ' + str(comm[1]) \
              + ' & ' + str(comm[2])+ ' & ' + str(comm[3]) + '\\\\'
        comm = statis_util.comm_stat(randoms)
        print 'Random &' + str(comm[0]) + ' & ' + str(comm[1]) \
              + ' & ' + str(comm[2])+ ' & ' + str(comm[3])+ '\\\\'
        comm = statis_util.comm_stat(youngs)
        print 'Younger &' + str(comm[0]) + ' & ' + str(comm[1]) \
              + ' & ' + str(comm[2])+ ' & ' + str(comm[3])+ '\\\\'

        z = statis_util.z_test(randoms, feds)
        print 'z-test(Random, ED): & $n_1$: ' + str(z[0]) + ' & $n_2$: ' + str(z[1]) \
              + ' & z-value: ' + str(z[2])+ ' & p-value: ' + str(z[3])+ '\\\\'
        z = statis_util.z_test(youngs, feds)
        print 'z-test(Younger, ED): & $n_1$: ' + str(z[0]) + ' & $n_2$:' + str(z[1]) \
              + ' & z-value: ' + str(z[2])+ ' & p-value: ' + str(z[3])+ '\\\\'
        z = statis_util.z_test(youngs, randoms)
        print 'z-test(Younger, Random): & $n_1$: ' + str(z[0]) + ' & $n_2$: ' + str(z[1]) \
              + ' & z-value: ' + str(z[2])+ ' & p-value: ' + str(z[3])+ '\\\\'
        plot.plot_pdf_mul_data([randoms, youngs, feds], ['--bo', '--r^', '--ks'], field,  ['Random', 'Younger', 'ED'], True)

feature_stat()


# get_field_values('fed', 'friends_count')
# get_field_values('fed', 'favourites_count')
# get_field_values('fed', 'statuses_count')


