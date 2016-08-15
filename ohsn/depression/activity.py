# -*- coding: utf-8 -*-
"""
Created on 18:12, 14/08/16

@author: wt
"""
import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

from ohsn.util import db_util as dbt
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import calendar, pickle
import pandas as pd


def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = int(sourcedate.year + month / 12 )
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    return datetime(year, month, day)

def add_day(sourcedate, days):
    month = sourcedate.month - 1
    year = int(sourcedate.year + month / 12)
    month = month % 12 + 1
    day = min(sourcedate.day + days, calendar.monthrange(year, month)[1])
    return datetime(year, month, day)

def month_bins(datemin, datemax, length=1):
    dates = [datemin]
    datec = datemin
    next_date = add_months(datec, length)
    while next_date < datemax:
        dates.append(next_date)
        datec = next_date
        next_date = add_months(datec, length)
    dates.append(datemax)
    return dates


def day_bin(datemin, datemax, length=1):
    dates = [datemin]
    next_date = datetime(datemin.year, datemin.month, datemin.day+length)
    while next_date <= datemax:
        dates.append(next_date)
        next_date = datetime(next_date.year, next_date.month, next_date.day+length)
    return dates


def plot_time(data, length=1, title=None):
    '''date(2012, 10, 6).toordinal() - date(2012, 9, 25).toordinal()'''
    mpl_data = mdates.date2num(data)
    '''Bin by Month'''
    # datemin = datetime(min(data).year, min(data).month, 1)
    # datemax = datetime(max(data).year, max(data).month+1, 1) - timedelta(days=1)
    # print min(data), max(data), len(data)
    # print datemin, datemax
    # bins = month_bins(datemin, datemax, length)

    '''Bin by Day'''
    datemin = min(data)
    datemax = max(data)
    bins = day_bin(datemin, datemax, 1)

    years = mdates.YearLocator()   # every year
    months = mdates.MonthLocator()  # every month
    yearsFmt = mdates.DateFormatter('%Y')
    fig, ax = plt.subplots()
    # print bins
    # print mdates.date2num(bins)
    ax.hist(mpl_data, bins=mdates.date2num(bins), color='lightblue')
    # ax.plot(binss, hists, 'r--')
    ax.xaxis.set_major_locator(years)
    ax.xaxis.set_major_formatter(yearsFmt)
    ax.xaxis.set_minor_locator(months)
    ax.set_xlim(datemin, datemax)
    ax.set_ylabel('Counts')
    if title:
        ax.set_title(title)
    ax.grid(True)
    plt.show()


def timeline(dbname, timename):
    db = dbt.db_connect_no_auth(dbname)
    timeline = db[timename]
    dates = []
    for status in timeline.find(no_cursor_timeout=True):
        dates.append(status['created_at'])
    return dates

if __name__ == '__main__':
    # dates = timeline('depression', 'search')
    # pickle.dump(dates, open('data/date.pick', 'w'))
    dates = pickle.load(open('data/date.pick', 'r'))
    # plot_time(dates, length=1, title='Depression')

    ts = pd.Series(dates)
    ts.groupby(ts.dt.date).count().plot(kind="bar")