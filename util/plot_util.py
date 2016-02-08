# -*- coding: utf-8 -*-
"""
Created on 18:29, 01/02/16

@author: wt

"""

import math
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import mean_squared_error


def pdf_ada_bin(data, xmin=None, xmax=None, linear_bins=False, **kwargs):
    if not xmax:
        xmax = max(data)
    if not xmin:
        xmin = min(data)
    if linear_bins:
        bins = range(int(xmin), int(xmax))
    else:
        log_min_size = np.log10(xmin)
        log_max_size = np.log10(xmax)
        number_of_bins = np.ceil((log_max_size-log_min_size)*10)
        bins = np.unique(
                np.floor(
                    np.logspace(
                        log_min_size, log_max_size, num=number_of_bins)))
    hist, edges = np.histogram(data, bins, density=True)
    bin_centers = (edges[1:]+edges[:-1])/2.0
    new_x, new_y = [], []
    # filter_limit = np.amax(hist) * 0.01
    for index in xrange(len(hist)):
        if hist[index] != 0:
            new_x.append(bin_centers[index])
            new_y.append(hist[index])
    return new_x, new_y


def pearson(x, y):
    # calculate the pearson correlation of two list
    n = len(x)
    avg_x = float(sum(x))/n
    avg_y = float(sum(y))/n
    print 'The means of two lists:', avg_x, avg_y
    diffprod = 0.0
    xdiff2 = 0.0
    ydiff2 = 0.0
    for idx in range(n):
        xdiff = x[idx] - avg_x
        ydiff = y[idx] - avg_y
        diffprod += xdiff*ydiff
        xdiff2 += xdiff*xdiff
        ydiff2 += ydiff*ydiff
    return diffprod/math.sqrt(xdiff2*ydiff2)

def mean_bin(list_x, list_y, linear_bins=False):
    # the returned values are raw values, not logarithmic values
    size = len(list_x)
    xmin = min(list_x)
    xmax = max(list_x)
    if linear_bins:
        bins = range(int(xmin), int(xmax+1))
    else:
        log_min_size = np.log10(xmin)
        log_max_size = np.log10(xmax+1)
        number_of_bins = np.ceil((log_max_size-log_min_size)*10)
        bins = np.unique(
                np.floor(
                    np.logspace(
                        log_min_size, log_max_size, num=number_of_bins)))

    new_bin_meanx_x, new_bin_means_y = [], []
    hist_x = np.histogram(list_x, bins)[0]
    hist_x_w = np.histogram(list_x, bins, weights=list_x)[0].astype(float)
    for index in xrange(len(bins)-1):
        if hist_x[index] != 0:
            new_bin_meanx_x.append(hist_x_w[index]/hist_x[index])
            range_min, range_max = bins[index], bins[index+1]
            sum_y = 0.0
            for i in xrange(size):
                key = list_x[i]
                if (key >= range_min) and (key < range_max):
                    sum_y += list_y[i]
            new_bin_means_y.append(sum_y/hist_x[index])
    return new_bin_meanx_x, new_bin_means_y


def cut_lists(list_x, list_y, fit_start=-1, fit_end=-1):
    if fit_start != -1:
        new_x, new_y = [], []
        for index in xrange(len(list_x)):
            if list_x[index] >= fit_start:
                new_x.append(list_x[index])
                new_y.append(list_y[index])
        list_x, list_y = new_x, new_y
    if fit_end != -1:
        new_x, new_y = [], []
        for index in xrange(len(list_x)):
            if list_x[index] < fit_end:
                new_x.append(list_x[index])
                new_y.append(list_y[index])
        list_x, list_y = new_x, new_y
    return (list_x, list_y)


def lr_ls(list_x, list_y, fit_start=-1, fit_end=-1):
    list_x, list_y = cut_lists(list_x, list_y, fit_start, fit_end)
    X = np.asarray(list_x, dtype=float)
    Y = np.asarray(list_y, dtype=float)
    logX = np.log10(X)
    logY = np.log10(Y)
    coefficients = np.polyfit(logX, logY, 1)
    polynomial = np.poly1d(coefficients)
    print 'Polynomial(', fit_start, fit_end, '):',  polynomial
    logY_fit = polynomial(logX)
    print 'Fitting RMSE(log):', rmse(logY, logY_fit)
    print 'Fitting RMSE(raw):', rmse(Y, np.power(10, logY_fit))
    # print Y
    return (list_x, np.power(10, logY_fit))
    # return logX, logY_fit


def lr_ml(list_x, list_y, fit_start=-1, fit_end=-1):
    # TODO
    list_x, list_y = cut_lists(list_x, list_y, fit_start, fit_end)
    X = np.asarray(list_x, dtype=float)
    Y = np.asarray(list_y, dtype=float)
    logX = np.log10(X)
    logY = np.log10(Y)


def lr_ks(list_x, list_y, fit_start=-1, fit_end=-1):
    # TODO
    list_x, list_y = cut_lists(list_x, list_y, fit_start, fit_end)
    X = np.asarray(list_x, dtype=float)
    Y = np.asarray(list_y, dtype=float)
    logX = np.log10(X)
    logY = np.log10(Y)


def dependence(listx, listy, l, xlabel, ylabel, start=1, end=1000):
    plt.clf()
    plt.scatter(listx, listy, s=20, c='#fee8c8', marker='+', label='raw '+l)
    ax = plt.gca()
    xmeans, ymeans = mean_bin(listx, listy)
    ax.scatter(xmeans, ymeans, s=50, c='#fdbb84', marker='o', label='binned '+l)
    xfit, yfit = lr_ls(xmeans, ymeans, start, end)
    ax.plot(xfit, yfit, c='#e34a33', linewidth=2, linestyle='--', label='Fitted '+l)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.set_xlim(xmin=1)
    ax.set_ylim(ymin=1)
    handles, labels = ax.get_legend_handles_labels()
    leg = ax.legend(handles, labels, loc=4)
    leg.draw_frame(True)
    plt.show()


def drop_zeros(list_a):
    # discard the zeros in a list
    return [i for i in list_a if i>0]


def rmse(predict, truth):
    # calculate RMSE of a prediction
    RMSE = mean_squared_error(truth, predict)**0.5
    return RMSE


'''Plot PDF'''
def pdf_plot_one_data(data, name, xmin=None, xmax=None, fit_start=1, fit_end=1):

    data = drop_zeros(data)
    # plt.gcf()
    # data = outstrength
    if not xmax:
        xmax = max(data)
    if not xmin:
        xmin = min(data)
    list_x, list_y = pdf_ada_bin(data, xmin=xmin, xmax=xmax, linear_bins=True)
    plt.plot(list_x, list_y, 'k+', label='Raw '+name)
    ax = plt.gca()
    list_x, list_y = pdf_ada_bin(data, xmin=xmin, xmax=xmax)
    ax.plot(list_x, list_y, '--bo', label='Binned '+name)
    # list_fit_x, list_fit_y = lr_ls(list_x, list_y, 1, 100)
    # ax.plot(list_fit_x, list_fit_y, 'b--', label='Fitted outstrength')
    if fit_start!=fit_end:
        list_fit_x, list_fit_y = lr_ls(list_x, list_y, fit_start, fit_end)
        ax.plot(list_fit_x, list_fit_y, 'r--', label='Fitted '+name)
    # data = outstrength
    # list_x, list_y = pdf(data, linear_bins=True)
    # ax.plot(list_x, list_y, 'b+', label='Raw outstrength')
    # ax = plt.gca()
    # list_x, list_y = pdf(data)
    # ax.plot(list_x, list_y, 'bo', label='Binned outstrength')
    # list_fit_x, list_fit_y = lr_ls(list_x, list_y, 50)
    # ax.plot(list_fit_x, list_fit_y, 'b--', label='Fitted outstrength')
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel('k')
    ax.set_ylabel('p(k)')
    ax.set_xlim(xmin=1)
    ax.set_ylim(ymax=1)
    handles, labels = ax.get_legend_handles_labels()
    leg = ax.legend(handles, labels, loc=0)
    leg.draw_frame(True)
    plt.show()


def pdf_fix_bin(data, xmin=None, xmax=None, linear_bins=False, **kwargs):
    if not xmax:
        xmax = max(data)
    if not xmin:
        xmin = min(data)
    if linear_bins:
        # bins = range(int(xmin), int(xmax))
        bins = np.linspace(xmin, xmax, num=40)
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


def plot_pdf_two_data(lista, listb, min_x=None, max_x=None, label1='x_1', label2='x_2'):
    lista = drop_zeros(lista)
    listb = drop_zeros(listb)
    if not max_x:
        max_x = max(np.amax(lista), np.amax(listb))
    if not min_x:
        min_x = min(np.amin(lista), np.amin(listb))
    list_x, list_y = pdf_fix_bin(lista, xmin=min_x, xmax=max_x, linear_bins=True)
    plt.plot(list_x, list_y, '--bo', label=label1)
    ax = plt.gca()
    list_x, list_y = pdf_fix_bin(listb, xmin=min_x, xmax=max_x, linear_bins=True)
    ax.plot(list_x, list_y, '--r*', label=label2)
    ax.set_xlabel('x')
    ax.set_ylabel('p(x)')
    # ax.set_xlim(xmin=1)
    # ax.set_ylim(ymax=1)
    # ax.set_title('Comparison of PDF of Echelon and Sample on '+field)
    handles, labels = ax.get_legend_handles_labels()
    leg = ax.legend(handles, labels, loc=0)
    leg.draw_frame(True)
    ax.set_autoscale_on(True)
    # plt.savefig('echelon-smaple-'+field+'.eps')
    # plt.clf()
    plt.show()
