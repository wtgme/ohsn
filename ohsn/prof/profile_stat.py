# -*- coding: utf-8 -*-
"""
Created on 13:56, 18/02/16

@author: wt

Compare the difference from their prof information


"""

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

from ohsn.util import plot_util as plot
from ohsn.util import statis_util
import ohsn.util.io_util as io
import ohsn.util.db_util as dbt
import pickle
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt


def profile_feature_stat():
    # 'favourites_count'
    fields = ['friends_count', 'followers_count', 'statuses_count']
    names = ['following', 'follower', 'tweet']

    filter = {}
    fitranges = [[(200, 100000), (1000, 100000000), (800, 10000000)],
                     [(700, 10000), (800, 10000000), (800, 1000000)],
                     [(800, 100000), (20000, 10000000), (10000, 10000000)]]
    for i in range(len(fields)):
        field = fields[i]
        print '=====================', field
        feds = np.array(io.get_values_one_field('fed', 'scom', field, filter))+1
        randoms = np.array(io.get_values_one_field('random', 'scom', field, filter))+1
        youngs = np.array(io.get_values_one_field('young', 'scom', field, filter))+1

        comm = statis_util.comm_stat(feds)
        print 'ED & ' + str(comm[0]) + ' & ' + str(comm[1]) \
              + ' & ' + str(comm[2])+ ' & ' + str(comm[3]) + '\\\\'
        comm = statis_util.comm_stat(randoms)
        print 'Random &' + str(comm[0]) + ' & ' + str(comm[1]) \
              + ' & ' + str(comm[2])+ ' & ' + str(comm[3])+ '\\\\'
        comm = statis_util.comm_stat(youngs)
        print 'Younger &' + str(comm[0]) + ' & ' + str(comm[1]) \
              + ' & ' + str(comm[2])+ ' & ' + str(comm[3])+ '\\\\'
        print '\\hline'

        # z = statis_util.z_test(randoms, feds)
        # print 'z-test(Random, ED): & $n_1$: ' + str(z[0]) + ' & $n_2$: ' + str(z[1]) \
        #       + ' & z-value: ' + str(z[2])+ ' & p-value: ' + str(z[3])+ '\\\\'
        # z = statis_util.z_test(youngs, feds)
        # print 'z-test(Younger, ED): & $n_1$: ' + str(z[0]) + ' & $n_2$:' + str(z[1]) \
        #       + ' & z-value: ' + str(z[2])+ ' & p-value: ' + str(z[3])+ '\\\\'
        # z = statis_util.z_test(youngs, randoms)
        # print 'z-test(Younger, Random): & $n_1$: ' + str(z[0]) + ' & $n_2$: ' + str(z[1]) \
        #       + ' & z-value: ' + str(z[2])+ ' & p-value: ' + str(z[3])+ '\\\\'

        z = statis_util.ks_test(randoms, feds)
        print 'ks-test(Random, ED): & $n_1$: ' + str(z[0]) + ' & $n_2$: ' + str(z[1]) \
              + ' & ks-value: ' + str(z[2])+ ' & p-value: ' + str(z[3])+ '\\\\'
        z = statis_util.ks_test(youngs, feds)
        print 'ks-test(Younger, ED): & $n_1$: ' + str(z[0]) + ' & $n_2$: ' + str(z[1]) \
              + ' & ks-value: ' + str(z[2])+ ' & p-value: ' + str(z[3])+ '\\\\'
        z = statis_util.ks_test(youngs, randoms)
        print 'ks-test(Younger, Random): & $n_1$: ' + str(z[0]) + ' & $n_2$: ' + str(z[1]) \
              + ' & ks-value: ' + str(z[2])+ ' & p-value: ' + str(z[3])+ '\\\\'

        plot.plot_pdf_mul_data([feds, randoms, youngs], names[i], ['g', 'b', 'r'], ['s', 'o', '^'], ['ED', 'Random', 'Younger'],
                               linear_bins=False, central=False, fit=True, fitranges=fitranges[i], savefile=field+'.pdf')


def profile_feature_dependence():
    fields = ['friends_count', 'statuses_count', 'followers_count']
    names = ['following', 'tweet', 'follower']

    for i in xrange(len(fields)):
        fi = fields[i]
        ni = names[i]
        for j in xrange(i+1, len(fields)):
            fj = fields[j]
            nj = names[j]
            print '=========================Dependence :', fi, fj
            plt.rcParams['legend.fontsize'] = 20
            plt.rcParams['axes.labelsize'] = 20
            ax = plt.gca()
            i = 0
            for db, color, mark, label in [('fed', 'g', 's', 'ED'),
                                           ('random', 'b', 'o', 'Random'),
                                           ('young', 'r', '^', 'Younger')]:
                print '++++++++++++++++++++++++++Dependence :', fi, fj, db
                fivalue = np.array(io.get_values_one_field(db, 'scom', fi))
                fjvalue = np.array(io.get_values_one_field(db, 'scom', fj))
                fivalue += 1
                fjvalue += 1
                xmeans, ymeans = plot.mean_bin(fivalue, fjvalue)
                ax.scatter(xmeans, ymeans, s=50, c=color, marker=mark, label=label)
                fit_start = min(fivalue)
                fit_end = max(fivalue)
                # fit_start = np.percentile(fivalue, 2.5)
                # fit_end = np.percentile(fivalue, 97.5)
                xfit, yfit, cof = plot.lr_ls(xmeans, ymeans, fit_start, fit_end)
                ax.plot(xfit, yfit, c=color, linewidth=2, linestyle='--')
                ax.annotate(r'$k_y \propto {k_x}^{'+str(round(cof, 2))+'}$',
                 xy=(xfit[-15], yfit[-15]),  xycoords='data',
                 xytext=(28+(i)*10, -30-(i)*10), textcoords='offset points', fontsize=20,
                 arrowprops=dict(arrowstyle="->"))
                i += 1
            ax.set_xscale("log")
            ax.set_yscale("log")
            ax.set_ylabel('k('+nj+')')
            ax.set_xlabel('k('+ni+')')
            ax.set_xlim(xmin=1)
            ax.set_ylim(ymin=1)
            handles, labels = ax.get_legend_handles_labels()
            leg = ax.legend(handles, labels, loc=4)
            leg.draw_frame(True)
            plt.savefig(fi+'-'+fj+'.pdf')
            plt.clf()


def gagement(dbname, colname):
    db = dbt.db_connect_no_auth(dbname)
    com = db[colname]
    for user in com.find({'status': {'$exists': True}}):
        engage = {}
        ts = datetime.strptime(user['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
        tts = datetime.strptime(user['status']['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
        delta = tts.date() - ts.date()
        days = delta.days+1
        try:
            status_count = abs(float(user['statuses_count']))
            friend_count = abs(float(user['friends_count']))
            follower_count = abs(float(user['followers_count']))
        except KeyError:
            continue
        # try:

        engage['statuses_day'] = status_count/days
        engage['friends_day'] = friend_count/days
        engage['followers_day'] = follower_count/days
        engage['friend_count'] = friend_count
        engage['status_count'] = status_count
        engage['follower_count'] = follower_count
        engage['active_day'] = days
        # engage['social_contribution'] = np.log(max(1, follower_count)/max(1, friend_count))
        # engage['information_productivity'] = np.log(1 + status_count/max(1, friend_count))
        # engage['information_attractiveness'] = np.log(1 + follower_count/max(1, status_count))
        # engage['information_influence'] = np.log(1 + follower_count*status_count/max(1, friend_count))
        # engage['statuses_day'] = np.log(1 + status_count/days)
        # engage['friends_day'] = np.log(1 + friend_count/days)
        # engage['followers_day'] = np.log(1 + follower_count/days)
        # engage['friend_count'] = np.log(friend_count + 1)
        # engage['status_count'] = np.log(status_count + 1)
        # engage['follower_count'] = np.log(follower_count + 1)
        # engage['social_contribution'] = np.log(max(1, follower_count)/max(1, friend_count))
        # engage['information_productivity'] = np.log(1 + status_count/max(1, friend_count))
        # engage['information_attractiveness'] = np.log(1 + follower_count/max(1, status_count))
        # engage['information_influence'] = np.log(1 + follower_count*status_count/max(1, friend_count))
        com.update_one({'id': user['id']}, {'$set': {'engage': engage}}, upsert=False)
        # except ZeroDivisionError:
        #     continue


if __name__ == '__main__':
    # profile_feature_stat()
    # profile_feature_dependence()
    gagement('www', 'com')
    # gagement('fed', 'com')
    # gagement('random', 'scom')
    # gagement('younger', 'scom')

    # ts = datetime.strptime('Sat Jul 04 06:23:37 +0000 2015', '%a %b %d %H:%M:%S +0000 %Y')
    # tts = datetime.strptime('Sun Mar 13 23:44:56 +0000 2016', '%a %b %d %H:%M:%S +0000 %Y')
    # delta = tts.date() - ts.date()
    # days = delta.days+1
    # print days



