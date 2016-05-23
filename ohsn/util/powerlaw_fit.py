# -*- coding: utf-8 -*-
"""
Created on 3:59 PM, 5/22/16

@author: tw
"""
import powerlaw
import numpy as np
import plot_util as pltt
import io_util as io
import pickle
import pylab


def fit_powerlaw(data):
    fit = powerlaw.Fit(data)
    print 'Fitting alpha', fit.power_law.alpha
    print 'Fitting sigma', fit.power_law.sigma
    print 'Fitting Likehood, pvalue', fit.distribution_compare('power_law', 'exponential')
    print 'Minx', fit.xmin
    return fit.xmin
    # print 'Fixed minx', fit.fixed_xmin
    # print 'Alpha', fit.alpha
    # print 'Devision', fit.D
    # fit = powerlaw.Fit(data, xmin=fit.xmin)
    # print 'Minx', fit.xmin
    # print 'Fixed minx', fit.fixed_xmin
    # print 'Alpha', fit.alpha
    # print 'Devision', fit.D
    figCCDF = fit.plot_pdf(color='b', linewidth=2)
    # fit.power_law.plot_pdf(color='b', linestyle='--', ax=figCCDF)
    # pylab.show()

if __name__ == '__main__':
    # followers = io.get_values_one_field(dbname='random', colname='scom', fieldname='followers_count', filt={})
    # pickle.dump(followers, open('data/follower.pick', 'w'))
    followers = pickle.load(open('data/follower.pick', 'r'))



    # print s
    min = fit_powerlaw(followers)

    pltt.pdf_plot_one_data(followers, 'test', linear_bins=False, fit_start=min, fit_end=max(followers))