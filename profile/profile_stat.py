# -*- coding: utf-8 -*-
"""
Created on 13:56, 18/02/16

@author: wt

Compare the difference from their profile information


"""

# import sys
# from os import path
# sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
import sys
sys.path.append('..')
import util.plot_util as plot
from util import statis_util
import util.io_util as io


def liwc_feature_stat():
    # fields = ['followers_count', 'friends_count', 'favourites_count', 'statuses_count']
    fields = io.read_field()
    fedsa = io.get_mlvs_field_values('fed', 'liwc_anal.result.WC', 'liwc_anal.result')
    randomsa = io.get_mlvs_field_values('random', 'liwc_anal.result.WC', 'liwc_anal.result')
    youngsa = io.get_mlvs_field_values('young', 'liwc_anal.result.WC', 'liwc_anal.result')
    for field in fields:
        print '=====================', field
        keys = field.split('.')
        feds = io.get_sublevel_values(fedsa, keys[2])
        randoms = io.get_sublevel_values(randomsa, keys[2])
        youngs = io.get_sublevel_values(youngsa, keys[2])

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

        z = statis_util.z_test(randoms, feds)
        print 'z-test(Random, ED): & $n_1$: ' + str(z[0]) + ' & $n_2$: ' + str(z[1]) \
              + ' & z-value: ' + str(z[2])+ ' & p-value: ' + str(z[3])+ '\\\\'
        z = statis_util.z_test(youngs, feds)
        print 'z-test(Younger, ED): & $n_1$: ' + str(z[0]) + ' & $n_2$:' + str(z[1]) \
              + ' & z-value: ' + str(z[2])+ ' & p-value: ' + str(z[3])+ '\\\\'
        z = statis_util.z_test(youngs, randoms)
        print 'z-test(Younger, Random): & $n_1$: ' + str(z[0]) + ' & $n_2$: ' + str(z[1]) \
              + ' & z-value: ' + str(z[2])+ ' & p-value: ' + str(z[3])+ '\\\\'

        print '\\hline'
        z = statis_util.ks_test(randoms, feds)
        print 'ks-test(Random, ED): & $n_1$: ' + str(z[0]) + ' & $n_2$: ' + str(z[1]) \
              + ' & ks-value: ' + str(z[2])+ ' & p-value: ' + str(z[3])+ '\\\\'
        z = statis_util.ks_test(youngs, feds)
        print 'ks-test(Younger, ED): & $n_1$: ' + str(z[0]) + ' & $n_2$:' + str(z[1]) \
              + ' & ks-value: ' + str(z[2])+ ' & p-value: ' + str(z[3])+ '\\\\'
        z = statis_util.ks_test(youngs, randoms)
        print 'ks-test(Younger, Random): & $n_1$: ' + str(z[0]) + ' & $n_2$: ' + str(z[1]) \
              + ' & ks-value: ' + str(z[2])+ ' & p-value: ' + str(z[3])+ '\\\\'

        plot.plot_pdf_mul_data([randoms, youngs, feds], ['--bo', '--r^', '--ks'], field,  ['Random', 'Younger', 'ED'], True)


def profile_feature_stat():
    fields = ['followers_count', 'friends_count', 'favourites_count', 'statuses_count']
    for field in fields:
        print '=====================', field
        feds = io.get_field_values('fed', field)
        randoms = io.get_field_values('random', field)
        youngs = io.get_field_values('young', field)

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

        z = statis_util.z_test(randoms, feds)
        print 'z-test(Random, ED): & $n_1$: ' + str(z[0]) + ' & $n_2$: ' + str(z[1]) \
              + ' & z-value: ' + str(z[2])+ ' & p-value: ' + str(z[3])+ '\\\\'
        z = statis_util.z_test(youngs, feds)
        print 'z-test(Younger, ED): & $n_1$: ' + str(z[0]) + ' & $n_2$:' + str(z[1]) \
              + ' & z-value: ' + str(z[2])+ ' & p-value: ' + str(z[3])+ '\\\\'
        z = statis_util.z_test(youngs, randoms)
        print 'z-test(Younger, Random): & $n_1$: ' + str(z[0]) + ' & $n_2$: ' + str(z[1]) \
              + ' & z-value: ' + str(z[2])+ ' & p-value: ' + str(z[3])+ '\\\\'

        print '\\hline'
        z = statis_util.ks_test(randoms, feds)
        print 'ks-test(Random, ED): & $n_1$: ' + str(z[0]) + ' & $n_2$: ' + str(z[1]) \
              + ' & ks-value: ' + str(z[2])+ ' & p-value: ' + str(z[3])+ '\\\\'
        z = statis_util.ks_test(youngs, feds)
        print 'ks-test(Younger, ED): & $n_1$: ' + str(z[0]) + ' & $n_2$:' + str(z[1]) \
              + ' & ks-value: ' + str(z[2])+ ' & p-value: ' + str(z[3])+ '\\\\'
        z = statis_util.ks_test(youngs, randoms)
        print 'ks-test(Younger, Random): & $n_1$: ' + str(z[0]) + ' & $n_2$: ' + str(z[1]) \
              + ' & ks-value: ' + str(z[2])+ ' & p-value: ' + str(z[3])+ '\\\\'
        plot.plot_pdf_mul_data([randoms, youngs, feds], ['--bo', '--r^', '--ks'], field,  ['Random', 'Younger', 'ED'], False)



# liwc_feature_stat()



