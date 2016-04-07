# -*- coding: utf-8 -*-
"""
Created on 18:29, 01/02/16

@author: wt

"""

import matplotlib.pyplot as plt
import numpy as np
from networkx import *
from sklearn.metrics import mean_squared_error
from matplotlib import cm
import matplotlib as mpl


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


def dependence(listx, listy, l, xlabel, ylabel, start=1, end=1000, savefile=None):
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
    if savefile is None:
        plt.show()
    else:
        plt.savefig(savefile)
        plt.clf()


def drop_zeros(list_a):
    # discard the zeros in a list
    return [i for i in list_a if i>0]


def rmse(predict, truth):
    # calculate RMSE of a prediction
    RMSE = mean_squared_error(truth, predict)**0.5
    return RMSE


def pdf_ada_bin(data, xmin=None, xmax=None, linear_bins=False, **kwargs):
    if not xmax:
        xmax = max(data)
    if not xmin:
        xmin = min(data)
    if linear_bins:
        print xmin, xmax
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


def pdf_fix_bin(data, xmin=None, xmax=None, linear_bins=False, **kwargs):
    if not xmax:
        xmax = max(data)
    if not xmin:
        xmin = min(data)
    if linear_bins:
        # bins = range(int(xmin), int(xmax))
        bins = np.linspace(xmin, xmax, num=50)
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


def pdf_plot_one_data(data, name, xmin=None, xmax=None, fit_start=1, fit_end=1, savefile=None):
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
    if fit_start!=fit_end:
        list_fit_x, list_fit_y = lr_ls(list_x, list_y, fit_start, fit_end)
        ax.plot(list_fit_x, list_fit_y, 'r--', label='Fitted '+name)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel('k')
    ax.set_ylabel('p(k)')
    ax.set_xlim(xmin=1)
    ax.set_ylim(ymax=1)
    handles, labels = ax.get_legend_handles_labels()
    leg = ax.legend(handles, labels, loc=0)
    leg.draw_frame(True)
    if savefile is None:
        plt.show()
    else:
        plt.savefig(savefile)
        plt.clf()


def plot_pdf_mul_data(lists, denots, field, labels=None, linear_bins=True, min_x=None, max_x=None, savefile=None):
    lists = [drop_zeros(a) for a in lists]
    if labels is None:
        labels = ['x'+str(i+1) for i in xrange(len(lists))]
    if not max_x:
        max_x = max([np.percentile(lista, 97.5) for lista in lists])
    if not min_x:
        min_x = min([np.percentile(lista, 2.5) for lista in lists])

    list_x, list_y = pdf_fix_bin(lists[0], xmin=min_x, xmax=max_x, linear_bins=linear_bins)
    plt.plot(list_x, list_y, denots[0], label=labels[0])

    for i in xrange(len(lists[1:])):
        ax = plt.gca()
        list_x, list_y = pdf_fix_bin(lists[i+1], xmin=min_x, xmax=max_x, linear_bins=linear_bins)
        ax.plot(list_x, list_y, denots[i+1], label=labels[i+1])
    if linear_bins == False:
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlim(xmin=1)
        ax.set_ylim(ymax=1)
    ax.set_xlabel('k')
    ax.set_ylabel('p(k)')

    ax.set_title('Comparison of probability density function on '+field)
    handles, labels = ax.get_legend_handles_labels()
    leg = ax.legend(handles, labels, loc=0)
    leg.draw_frame(True)
    ax.set_autoscale_on(True)
    # plt.savefig('echelon-smaple-'+field+'.pdf')
    # plt.clf()
    if savefile is None:
        plt.show()
    else:
        plt.savefig(savefile)
        plt.clf()


def network_top(DG, savefile=None):
    # pos = random_layout(DG)
    # pos = shell_layout(DG)
    pos = spring_layout(DG)
    # pos = circular_layout(DG)
    # pos = fruchterman_reingold_layout(DG)
    # pos = spectral_layout(DG)
    # plt.title('Plot of Network')
    draw(DG, pos)
    if savefile is None:
        plt.show()
    else:
        plt.savefig(savefile)
        plt.clf()


def color_wheel(savefile=None):
    fig = plt.figure()
    display_axes = fig.add_axes([0.1,0.1,0.8,0.8], projection='polar')
    display_axes._direction = 2*np.pi ## This is a nasty hack - using the hidden field to
                                      ## multiply the values such that 1 become 2*pi
                                      ## this field is supposed to take values 1 or -1 only!!
    norm = mpl.colors.Normalize(0.0, 2*np.pi)
    # Plot the colorbar onto the polar axis
    # note - use orientation horizontal so that the gradient goes around
    # the wheel rather than centre out
    quant_steps = 2056
    cb = mpl.colorbar.ColorbarBase(display_axes, cmap=cm.get_cmap('hsv',quant_steps),
                                       norm=norm,
                                       orientation='horizontal')
    # aesthetics - get rid of border and axis labels
    cb.outline.set_visible(False)
    display_axes.set_axis_off()
    display_axes.set_rlim([-1,1])
    # plt.show() # Replace with plt.savefig if you want to save a file
    if savefile is None:
        plt.show()
    else:
        plt.savefig(savefile)
        plt.clf()


def color_bars(colorlist, colorcounts, savefile=None):
    countsum = 0.0
    statis = [0.0]*len(colorlist)
    for i in colorcounts:
        countsum += 1
        statis[i-1] += 1
    list_y = np.array([value/countsum for value in statis])
    list_x = np.array([i for i in xrange(len(colorlist))])
    fig, ax = plt.subplots()
    bars = ax.bar(list_x+0.1, list_y, 0.8)
    for i in xrange(len(colorlist)):
        bars[i].set_color(colorlist[i])
        bars[i].set_linewidth(1)
        bars[i].set_edgecolor('k')
    ax.set_xticks(list_x + 0.5)
    # plt.xticks(list_x + 0.5)
    ax.set_xticklabels([str(i+1) for i in list_x], fontsize = 10, rotation=90)
    #Set descriptions:
    ax.set_title("Color Choice Preference( No." +str(len(colorcounts)) +')')
    ax.set_ylabel('Color choice (%)')
    ax.set_xlabel('Color ID')
    ax.set_xlim(xmax=len(colorlist))
    # ax.grid(True)
    ax.yaxis.grid()
    if savefile is None:
        plt.show()
    else:
        plt.savefig(savefile)
        plt.clf()


def hist2d(x, y, nx, ny):
    # fig, ax = plt.subplots()
    # im = ax.hexbin(x, y, gridsize=20)
    # fig.colorbar(im, ax=ax)
    # x, y = np.random.normal(size=(2, 10000))
    fig, ax = plt.subplots()
    H = ax.hist2d(x, y, bins=[nx, ny])
    fig.colorbar(H[3], ax=ax)
    plt.show()
