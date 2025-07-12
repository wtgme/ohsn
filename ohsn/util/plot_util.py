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
import pylab
import powerlaw_fit
import seaborn as sns
sns.reset_orig()
import scipy.stats as stats
from scipy import optimize


def significant(data, observed, name):
    absobserved = abs(observed)
    pval = (np.sum(data > absobserved) +
            np.sum(data < -absobserved))/float(len(data))
    print pval
    tmax = np.percentile(data, (1-np.sum(data > absobserved)/float(len(data)))*100)
    tmin = np.percentile(data, 100 * np.sum(data > absobserved)/float(len(data)))
    print 'Test pvalue', tmin, tmax, observed
    xmax = np.percentile(data, 97.5)
    xmin = np.percentile(data, 2.5)
    pylab.title('Empirical assortativity distribution of ' + name.split('.')[1].upper())
    pylab.hist(data, bins=100, histtype='step', normed=True)
    pylab.axvline(observed, c='green', linewidth=3, label='Observed')
    # pylab.axvline(-observed, c='green', linewidth=3, label='-Observed')
    pylab.axvline(xmax, c='red', linestyle='-.', linewidth=3, label='p=0.05')
    pylab.axvline(xmin, c='red', linestyle='-.', linewidth=3)
    strx = 'p '+str(round(pval, 3))
    print strx
    pylab.text(2, 30, strx, fontsize=15)
    pylab.legend()
    pylab.grid(True)
    pylab.show()
    # pylab.savefig('examples/permutation.png')


def mean_bin(list_x, list_y, linear_bins=False):
    # the returned values are raw values, not logarithmic values
    size = len(list_x)
    xmin = min(list_x)
    xmax = max(list_x)
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
    return (np.array(list_x), np.array(list_y))



def lr_ls(list_x, list_y, fit_start=-1, fit_end=-1):
    #Least square fit
    list_x, list_y = cut_lists(list_x, list_y, fit_start, fit_end)
    X = np.asarray(list_x, dtype=float)
    Y = np.asarray(list_y, dtype=float)
    logX = np.log10(X)
    logY = np.log10(Y)
    idx = np.isfinite(logX) & np.isfinite(logY)
    coefficients = np.polyfit(logX[idx], logY[idx], 1)
    polynomial = np.poly1d(coefficients)
    print 'Polynomial(', fit_start, fit_end, '):',  polynomial
    logY_fit = polynomial(logX[idx])
    print 'Fitting RMSE(log):', rmse(logY[idx], logY_fit)
    print 'Fitting RMSE(raw):', rmse(Y[idx], np.power(10, logY_fit))
    # print Y
    return (list_x[idx], np.power(10, logY_fit), coefficients[0])
    # return logX, logY_fit


def dependence(listx, listy, l, xlabel, ylabel, start=1, end=1000, savefile=None):
    plt.clf()
    plt.scatter(listx, listy, s=20, c='#fee8c8', marker='+', label='raw '+l)
    ax = plt.gca()
    xmeans, ymeans = mean_bin(listx, listy)
    ax.scatter(xmeans, ymeans, s=50, c='#fdbb84', marker='o', label='binned '+l)
    xfit, yfit = lr_ls(xmeans, ymeans, start, end)
    ax.plot(xfit, yfit, c='#e34a33', linewidth=2, linestyle='--', label='Fitted '+l)
    # ax.set_xscale("log")
    # ax.set_yscale("log")
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    # ax.set_xlim(xmin=1)
    # ax.set_ylim(ymin=1)
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
    # print xmax, xmin
    if linear_bins:
        # print xmin, xmax
        if (xmax-xmin) > 5000:
            bins = np.linspace(xmin, xmax, num=(xmax-xmin)/10)
        else:
            bins = range(int(xmin), int(xmax))
    else:
        log_min_size = np.log10(xmin)
        log_max_size = np.log10(xmax)
        number_of_bins = np.ceil((log_max_size-log_min_size)*10)
        # print log_min_size, log_max_size, number_of_bins
        bins = np.unique(
                np.floor(
                    np.logspace(
                        log_min_size, log_max_size, num=number_of_bins)))
    hist, edges = np.histogram(data, bins, density=True)
    bin_centers = (edges[1:]+edges[:-1])/2.0
    # hist[hist==0] = np.nan
    return bin_centers[hist!=0], hist[hist!=0]
    # new_x, new_y = [], []
    # # filter_limit = np.amax(hist) * 0.01
    # for index in xrange(len(hist)):
    #     if hist[index] != 0:
    #         new_x.append(bin_centers[index])
    #         new_y.append(hist[index])
    # return new_x, new_y


def pdf_fix_bin(data, xmin=None, xmax=None, linear_bins=False, **kwargs):
    if not xmax:
        xmax = max(data)
    if not xmin:
        xmin = min(data)
    if linear_bins:
        bins = np.linspace(xmin, xmax, num=35)
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
    # hist[hist==0] = np.nan
    return bin_centers[hist!=0], hist[hist!=0]


def pdf_plot_one_data(data, name, linear_bins=True, central=False, fit_start=1, fit_end=1, savefile=None, **kwargs):
    print 'Original length', len(data)
    data = drop_zeros(data)
    print 'Stripped length', len(data)
    # plt.gcf()
    # data = outstrength
    if central:
        xmin = np.percentile(data, 2.5)
        xmax = np.percentile(data, 97.5)
    else:
        xmin = min(data)
        xmax = max(data)
    ax = plt.gca()
    list_x, list_y = pdf_ada_bin(data, xmin=xmin, xmax=xmax, linear_bins=True)
    ax.plot(list_x, list_y, 'k^', label='Raw '+name)
    list_x, list_y = pdf_ada_bin(data, xmin=xmin, xmax=xmax, linear_bins=linear_bins)
    ax.plot(list_x, list_y, 'bo', label='Binned '+name)
    if fit_start != fit_end:
        list_fit_x, list_fit_y, coe = lr_ls(list_x, list_y, fit_start, fit_end)
        ax.plot(list_fit_x, list_fit_y, 'r--', label='Fitted '+name)
    if linear_bins == False:
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlim(xmin=1)
        ax.set_ylim(ymax=1)
    ax.set_xlabel('k')
    ax.set_ylabel('p(k)')
    handles, labels = ax.get_legend_handles_labels()
    leg = ax.legend(handles, labels, loc=0)
    leg.draw_frame(True)
    ax.grid(True)
    if savefile is None:
        plt.show()
    else:
        plt.savefig(savefile)
        plt.clf()


def plot_pdf_mul_data(lists, field, colors, marks, labels=None, linear_bins=True, central=False, fit=False, fitranges=None, savefile=None, **kwargs):
    # lists = [drop_zeros(a) for a in lists]
    if labels is None:
        labels = ['x'+str(i+1) for i in xrange(len(lists))]
    if central:
        max_x = np.max([np.percentile(listx, 97.5) for listx in lists])
        min_x = np.min([np.percentile(listx, 2.5) for listx in lists])
    else:
        max_x = np.max([np.max(listx) for listx in lists])
        min_x = np.min([np.min(listx) for listx in lists])
    plt.rcParams['axes.labelsize'] = 15
    plt.rcParams['xtick.labelsize'] = 15
    plt.rcParams['ytick.labelsize'] = 15
    plt.rcParams['legend.fontsize'] = 20
    plt.rcParams['lines.markersize'] = 10
    plt.rcParams['pdf.fonttype'] = 42
    plt.rcParams['ps.fonttype'] = 42
    # plt.rcParams['text.usetex'] = True

    # plot_config()
    ax = plt.gca()
    # print 'Max values in Lists', max_x, min_x
    list_x, list_y = pdf_fix_bin(lists[0], xmin=min_x, xmax=max_x, linear_bins=linear_bins)
    ax.plot(list_x, list_y, colors[0]+marks[0], label=labels[0])

    # '''Plot mean age'''
    # ax.axvline(np.mean(lists[0]), linestyle='dashdot', c='r', lw=6)
    # ax.annotate('Mean', xy=(np.mean(lists[0]), 0.25),  xycoords='data',
    #                  xytext=(-60, -50), textcoords='offset points', fontsize=30,
    #                  arrowprops=dict(arrowstyle="->"))

    '''add cut-offs for bmi'''
    bmilist = [(16.5, 'T'), (18.7, 'U'), (21.4, 'M'), (25.0, 'O')]
    for i in xrange(len(bmilist)):
        n, t = bmilist[i]
        c = np.random.rand(3)
        ax.axvline(n, linestyle='dashdot', c=c, lw=6)
        ax.annotate(t, xy=(n, 0.155),  xycoords='data',
                     xytext=(40*((4-i)+1), -30*((4-i)+1)), textcoords='offset points', fontsize=30,
                     arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=-.2"))

    if fit:
        if fitranges:
            fitmin, finmax = fitranges[0]
        else:
            fitmin, finmax = powerlaw_fit.fit_powerlaw(lists[0]), max(lists[0])
        list_fit_x, list_fit_y, cof = lr_ls(list_x, list_y, fitmin, finmax)
        ax.plot(list_fit_x, list_fit_y, colors[0]+'--', linewidth=2)
        ax.annotate(r'$p(k) \propto {k}^{'+str(round(cof, 2))+'}$',
                 xy=(list_fit_x[-6], list_fit_y[-6]),  xycoords='data',
                 xytext=(-100, -40), textcoords='offset points', fontsize=20,
                 arrowprops=dict(arrowstyle="->"))
    for i in xrange(len(lists[1:])):
        ax = plt.gca()
        list_x, list_y = pdf_fix_bin(lists[i+1], xmin=min_x, xmax=max_x, linear_bins=linear_bins)
        ax.plot(list_x, list_y, colors[i+1]+marks[i+1], label=labels[i+1])
        if fit:
            if fitranges:
                fitmin, finmax = fitranges[i+1]
            else:
                fitmin, finmax = powerlaw_fit.fit_powerlaw(lists[i+1]), max(lists[i+1])
            list_fit_x, list_fit_y, cof = lr_ls(list_x, list_y, fitmin, finmax)
            ax.plot(list_fit_x, list_fit_y, colors[i+1]+'--', linewidth=2)
            ax.annotate(r'$p(k) \propto {k}^{'+str(round(cof, 2))+'}$',
                 xy=(list_fit_x[-9], list_fit_y[-9]),  xycoords='data',
                 xytext=(-140-i*60, -30-i*35), textcoords='offset points', fontsize=20,
                 arrowprops=dict(arrowstyle="->"))
    if linear_bins == False:
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlim(xmin=1)
        ax.set_ylim(ymax=1)
    # ax.set_xlabel('k')
    # ax.set_ylabel('p(k)')
    handles, labels = ax.get_legend_handles_labels()
    leg = ax.legend(handles, labels, loc=0)
    leg.draw_frame(True)
    ax.set_autoscale_on(True)
    # plt.rcParams['xtick.labelsize'] = 20
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


def correlation(x, y, xlabel, ylabel, savefile):
    x = np.array(x)
    y = np.array(y)
    maxx, minx = np.percentile(x, 97.5), np.percentile(x, 2.5)
    # print maxx, minx
    xflags = (x>=minx)&(x<=maxx)
    # maxx, minx = max(x), min(x)
    maxy, miny = np.percentile(y, 97.5), np.percentile(y, 2.5)
    yflags = (y>=miny)&(y<=maxy)
    # maxy, miny = max(y), min(y)
    stat_func = stats.kendalltau
    # stat_func = stats.pearsonr
    print len(x[xflags&yflags])
    sns.jointplot(x[xflags&yflags], y[xflags&yflags], stat_func=stat_func, kind="reg", xlim=(minx, maxx), ylim=(miny, maxy)).set_axis_labels(xlabel, ylabel)
    plt.savefig(savefile)
    plt.clf()
    plt.close()


def plot_config():
    sns.set(style="whitegrid", palette="pastel", color_codes=True)
    plt.rcParams['axes.labelsize'] = 25
    plt.rcParams['xtick.labelsize'] = 18
    plt.rcParams['ytick.labelsize'] = 18
    plt.rcParams['legend.fontsize'] = 25
    plt.rcParams['font.family'] = 'sans-serif'
    # plt.rcParams['axes.formatter.useoffset'] = False
    # plt.rcParams['lines.markersize'] = 4
    # plt.rcParams['lines.linewidth'] = 2
    plt.rcParams['pdf.fonttype'] = 42
    plt.rcParams['ps.fonttype'] = 42


def test():
    sns.set(style="whitegrid")

    # Load the example Titanic dataset
    titanic = sns.load_dataset("titanic")
    print titanic

    # Set up a grid to plot survival probability against several variables
    g = sns.PairGrid(titanic, y_vars="survived",
                     x_vars=["class", "sex", "who", "alone"],
                     size=5, aspect=.5)

    # Draw a seaborn pointplot onto each Axes
    g.map(sns.pointplot, color=sns.xkcd_rgb["plum"])
    g.set(ylim=(0, 1))
    sns.despine(fig=g.fig, left=True)
    # a = [[1,1,1,1,1], [2,2,2], [3,4,2,4,3,12]]
    # g = sns.PairGrid(a)


def test2():
    import seaborn as sns
    sns.set(style="whitegrid", palette="pastel", color_codes=True)

    # Load the example tips dataset
    tips = sns.load_dataset("tips")
    print tips

    # Draw a nested violinplot and split the violins for easier comparison
    sns.violinplot(x="day", y="total_bill", hue="sex", data=tips, split=True,
                   inner="quart", palette={"Male": "b", "Female": "y"})
    sns.despine(left=True)


def power_law_fit(a):
    hist, bins = np.histogram(a, bins='doane', density=True)
    bin_centers = (bins[1:]+bins[:-1])/2.0

    list_fit_x, list_fit_y, cof = lr_ls(bin_centers, hist)
    plt.plot(bin_centers, hist, 'o', markersize=4, label='data')

    plt.plot(list_fit_x, list_fit_y, 'r--', label='Fitted')
    plt.annotate(r'$p(k) \propto {k}^{'+str(round(cof, 2))+'}$',
                 xy=(list_fit_x[-9], list_fit_y[-9]),  xycoords='data',
                 xytext=(-140-1*60, -30-1*35), textcoords='offset points', fontsize=20,
                 arrowprops=dict(arrowstyle="->"))
    plt.xlabel("K")
    plt.ylabel("PDF")
    plt.xscale('log')
    plt.yscale('log')
    plt.legend(loc='lower right')
    plt.show()


def binning(x, y):
    xmin = min(np.min(x), np.min(y))
    xmax = max(np.max(x), np.max(y))
    bins = [xmin]
    cur_value = bins[0]
    multiplier = 2.0
    while cur_value < xmax:
        cur_value = cur_value * multiplier
        bins.append(cur_value)
    bins = np.array(bins)
    return bins

def log_bin(x, bins):
    bin_widths = (bins[1:] + bins[0:-1])/2.0
    pdf, _ = np.histogram(x, bins=bins, normed=True)
    return bin_widths, pdf


if __name__ == '__main__':
    # sns.set(style="darkgrid", color_codes=True)
    # tips = sns.load_dataset("tips")
    # print tips
    # g = (sns.jointplot("total_bill", "tip", data=tips, stat_func=stats.kendalltau, kind="reg",
    #               xlim=(0, 60), ylim=(0, 12), color="b", size=7))
    # plt.show()
    # test2()
    # plt.show()
    rands = np.random.rand(10000)
    one_per_rands = 1./rands
    plot_log_bin(one_per_rands)
