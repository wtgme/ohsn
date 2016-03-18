# -*- coding: utf-8 -*-
"""
Created on 09:40, 11/02/16

@author: wt

verify all users in ED have been added in com db
"""

import sys
sys.path.append('..')
import util.db_util as dbt
import pymongo

import sys
import datetime

import numpy
from matplotlib import pyplot
from matplotlib.dates import YearLocator, MonthLocator, DateFormatter
from matplotlib.dates import date2num


def num_now():
    """
    Return the current date in matplotlib representation
    """
    return date2num(datetime.datetime.now())


def get_limit(past):
    """
    Get the date `past` time ago as the matplotlib representation
    """
    return num_now() - float(past) * 365


def read_dates():
    """
    Read newline-separated unix time from stream
    """
    dates = []
    db = dbt.db_connect_no_auth('fed')
    poi = db['com']
    for user in poi.find({'level': 1, 'status.created_at': {'$exists': True}}):
        last_time = user['status']['created_at']
        # print last_time
        date_object = datetime.datetime.strptime(last_time,
                                       "%a %b %d %H:%M:%S +0000 %Y")
        # print date_object.strftime("%a %b %d %H:%M:%S +0000 %Y")
        num = date2num(date_object)
        dates.append(num)
    return dates


def plot_datehist(dates, bins, title=None):
    (hist, bin_edges) = numpy.histogram(dates, bins, density=True)
    print bin_edges
    print hist, sum(hist)
    # sum = sum(hist)
    # hist = hist/sum(hist)
    # print hist
    width = bin_edges[1] - bin_edges[0]

    fig = pyplot.figure()
    ax = fig.add_subplot(111)
    ax.bar(bin_edges[:-1], hist, width=0.8*width)
    ax.set_xlim(bin_edges[0], bin_edges[-1])
    ax.set_ylabel('Count')
    if title:
        ax.set_title(title)

    # set x-ticks in date
    # see: http://matplotlib.sourceforge.net/examples/api/date_demo.html
    ax.xaxis.set_major_locator(YearLocator())
    ax.xaxis.set_major_formatter(DateFormatter('%Y'))
    ax.xaxis.set_minor_locator(MonthLocator())
    # format the coords message box
    ax.format_xdata = DateFormatter('%Y-%m-%d')
    # ax.grid(True)
    ax.yaxis.grid()
    fig.autofmt_xdate()
    return fig


def main():
    dates = read_dates()
    # print dates
    fig = plot_datehist(dates, 30, title='Datetime of last posts')

    # if opts.out:
    #     fig.savefig(opts.out)
    # else:
    pyplot.show()


if __name__ == '__main__':
    main()