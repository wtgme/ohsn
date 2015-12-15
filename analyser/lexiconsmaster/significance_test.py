# -*- coding: utf-8 -*-
"""
Created on 18:17, 13/12/15

@author: wt
Using Z-test to verify the LIWC difference between two groups.

"""

import sys
from os import path
import numpy as np
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
import util.db_util as dbutil
import datetime
import matplotlib.pyplot as plt




'''Connecting db and collections'''
db1 = dbutil.db_connect_no_auth('stream')
sample_poi = db1['poi_sample']

db2 = dbutil.db_connect_no_auth('echelon')
echelon_poi = db2['poi']

print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "\t" + 'Connecting POI dbs well'


def pdf(data, xmin=None, xmax=None, linear_bins=False, **kwargs):
    if not xmax:
        xmax = max(data)
    if not xmin:
        xmin = min(data)
    if linear_bins:
        # bins = range(int(xmin), int(xmax))
        bins = np.linspace(xmin, xmax, num=100)
        # bins = np.unique(
        #         np.floor(
        #             np.linspace(
        #                 xmin, xmax, num=30)))
    else:
        log_min_size = np.log10(xmin)
        log_max_size = np.log10(xmax)
        number_of_bins = np.ceil((log_max_size-log_min_size)*10)
        bins = np.unique(
                np.floor(
                    np.logspace(
                        log_min_size, log_max_size, num=number_of_bins)))
    hist, edges = np.histogram(data, bins, density=True)
    # print np.sum(hist*np.diff(edges))
    # hist = hist / hist.sum()
    bin_centers = (edges[1:]+edges[:-1])/2.0
    new_x, new_y = [], []
    filter_limit = np.amax(hist) * 0.01
    for index in xrange(len(hist)):
        if hist[index] >= filter_limit:
            new_x.append(bin_centers[index])
            new_y.append(hist[index])
    return new_x, new_y

def plot_pdf(lista, listb, field):
    min_x = min(np.amin(lista), np.amin(listb))
    max_x = max(np.amax(lista), np.amax(listb))
    list_x, list_y = pdf(lista, xmin=min_x, xmax=max_x, linear_bins=True)
    plt.plot(list_x, list_y, '--bo', label='Echelon')
    ax = plt.gca()
    list_x, list_y = pdf(listb, xmin=min_x, xmax=max_x, linear_bins=True)
    ax.plot(list_x, list_y, '--r*', label='Sample')
    ax.set_xlabel('x')
    ax.set_ylabel('p(x)')
    # ax.set_xlim(xmin=1)
    # ax.set_ylim(ymax=1)
    ax.set_title('Comparison of PDF of Echelon and Sample on '+field)
    handles, labels = ax.get_legend_handles_labels()
    leg = ax.legend(handles, labels, loc=0)
    leg.draw_frame(True)
    ax.set_autoscale_on(True)
    plt.savefig('echelon-smaple-'+field+'.eps')
    plt.clf()
    # plt.show()
#     echelon-smaple-field.eps



def store_2_array(db, flag, col_name):
    a = np.zeros(0)
    tag_names = col_name.split('.')
    for v in db.find({flag: {'$exists': True}}, {col_name: 1}):
        try:
            a = np.append(a, v[tag_names[0]][tag_names[1]][tag_names[2]])
        except KeyError:
            print v
            continue
    return a


def z_test(db1, db2, flag, col_name):
    list1 = store_2_array(db1, flag, col_name)
    list2 = store_2_array(db2, flag, col_name)
    n1, n2 = list1.shape[0], list2.shape[0]
    mu1, mu2 = np.mean(list1), np.mean(list2)
    s1, s2 = np.std(list1), np.std(list2)
    z = (mu1-mu2)/(np.sqrt(s1**2/n1 + s2**2/n2))
    from scipy.stats import norm
    pval = 2*(1 - norm.cdf(abs(z)))
    print col_name.split('.')[-1], n1, n2, mu1, mu2, s1, s2, round(z, 3), round(pval, 4)
    if mu1 and mu2:
        plot_pdf(list1, list2, col_name.split('.')[-1])
    return round(z, 3), round(pval, 4)


fields = ['liwc_anal.result.WC',
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
for field in fields:
    z_test(echelon_poi, sample_poi, 'liwc_anal.result.WC', field)
