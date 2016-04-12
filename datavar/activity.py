# -*- coding: utf-8 -*-
"""
Created on 3:35 PM, 4/11/16

@author: tw
Plot the distribution of timeline, i.e., how many tweets are there in each period
"""

import sys
sys.path.append('..')
import util.db_util as dbt
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import calendar


def create_time():
    db = dbt.db_connect_no_auth('fed')
    com = db['com']
    created_time = {}
    for user in com.find({'level':1}):
        ts = datetime.strptime(user['created_at'],'%a %b %d %H:%M:%S +0000 %Y')
        # print type(ts)
        created_time[user['id']] = ts
        # print ts
        # print user['created_at']
        # print '-----------------------'
    return created_time


def monthdelta(d1, d2):
    delta = 0
    while True:
        mdays = calendar.monthrange(d1.year, d1.month)[1]
        d1 += timedelta(days=mdays)
        if d1 <= d2:
            delta += 1
        else:
            break
    return delta


def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = int(sourcedate.year + month / 12 )
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year, month)[1])
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


def plot_time(data, length=1, title=None):
    '''date(2012, 10, 6).toordinal() - date(2012, 9, 25).toordinal()'''
    mpl_data = mdates.date2num(data)
    datemin = datetime(min(data).year, min(data).month, 1)
    datemax = datetime(max(data).year, max(data).month+1, 1)
    print datemin, datemax
    bins = month_bins(datemin, datemax, length)

    years = mdates.YearLocator()   # every year
    months = mdates.MonthLocator()  # every month
    yearsFmt = mdates.DateFormatter('%Y')
    fig, ax = plt.subplots()
    print bins
    print mdates.date2num(bins)
    ax.hist(mpl_data, bins=mdates.date2num(bins), color='lightblue')
    ax.xaxis.set_major_locator(years)
    ax.xaxis.set_major_formatter(yearsFmt)
    ax.xaxis.set_minor_locator(months)
    ax.set_xlim(datemin, datemax)
    ax.set_ylabel('Counts')
    if title:
        ax.set_title(title)
    plt.show()


print
dates = create_time().values()
print len(dates), min(dates), max(dates)
print mdates.date2num(min(dates)), mdates.date2num(max(dates))
plot_time(dates, 1, 'Created time of ED accounts')
