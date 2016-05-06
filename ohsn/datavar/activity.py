# -*- coding: utf-8 -*-
"""
Created on 3:35 PM, 4/11/16

@author: tw
Plot the distribution of timeline, i.e., how many tweets are there in each period
"""


from ohsn.util import db_util as dbt
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import calendar
import pickle


def create_time(dbname, colname):
    db = dbt.db_connect_no_auth(dbname)
    com = db[colname]
    created_time = {}
    # biolist =    ['text_anal.gw.value',
    #               'text_anal.cw.value',
    #               # 'text_anal.edword_count.value',
    #               'text_anal.h.value',
    #               'text_anal.a.value',
    #               'text_anal.lw.value',
    #               'text_anal.hw.value']
    # for user in com.find({"$and":[
    #                      # {biolist[0]:{'$exists': True}},
    #                      {biolist[1]:{'$exists': True}},
    #                      {biolist[2]:{'$exists': True}},
    #                      # {biolist[3]:{'$exists': True}},
    #                      # {biolist[4]:{'$exists': True}},
    #                      # {biolist[5]:{'$exists': True}}
    #     {'status':{'$exists': True}}
    #                     ]}):
    for user in com.find({}):
        ts = datetime.strptime(user['created_at'],'%a %b %d %H:%M:%S +0000 %Y')
        # print type(ts)
        created_time[user['id']] = ts
        # print ts
        # print user['created_at']
        # print '-----------------------'
    # print max(created_time.values()), min(created_time.values())
    return created_time


def timeline_split(dbname, colname):
    db = dbt.db_connect_no_auth(dbname)
    timeline = db[colname]
    yeartw = {}
    for status in timeline.find():
        ts = datetime.strptime(status['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
        tid = status['id']
        tlist = yeartw.get(ts.year, [])
        tlist.append(tid)
        yeartw[ts.year] = tlist
    return yeartw


def timeline_time(dbname, colname, timename):
    db = dbt.db_connect_no_auth(dbname)
    com = db[colname]
    timeline = db[timename]
    posts = {}
    dates = {}
    biolist =    ['text_anal.gw.value',
                  'text_anal.cw.value',
                  # 'text_anal.edword_count.value',
                  'text_anal.h.value',
                  'text_anal.a.value',
                  'text_anal.lw.value',
                  'text_anal.hw.value']
    for user in com.find({"$and":[
                         # {biolist[0]:{'$exists': True}},
                         {biolist[1]:{'$exists': True}},
                         {biolist[2]:{'$exists': True}},
                         # {biolist[3]:{'$exists': True}},
                         # {biolist[4]:{'$exists': True}},
                         # {biolist[5]:{'$exists': True}}
                        ]}):
        uid, timeline_count = user['id'], user['timeline_count']
        posts[uid] = timeline_count
        for tw in timeline.find({'user.id': uid}):
            ts = datetime.strptime(tw['created_at'],'%a %b %d %H:%M:%S +0000 %Y')
            datelist = dates.get(uid, [])
            datelist.append(ts)
            dates[uid] = datelist
    return posts, dates


def relative_time(creat_time, post_time):
    dates = []
    oldest, oldcre, oldpost = 0, datetime.now(), datetime.now()
    for key in post_time.keys():
        ctime = creat_time[key]
        posts = post_time[key]
        for post in posts:
            delta = post.date() - ctime.date()
            dates.append(delta.days+1)
            if delta.days > oldest:
                oldest, oldcre, oldpost = delta.days, ctime, post
    print 'Oldest', oldest, oldcre, oldpost
    return dates


def avg_per_day(post_count, post_time):
    dates = []
    oldest, oldcre, oldpost, count, uid = 0.0, datetime.now(), datetime.now(), 0, 0
    for key in post_time.keys():
        posts = post_time[key]
        first, last = min(posts), max(posts)
        delta = last.date() - first.date()
        dates.append(post_count[key]/float(delta.days+1))
        if post_count[key]/float(delta.days+1) > oldest:
            oldest, oldcre, oldpost, count, uid = post_count[key]/float(delta.days+1), first, last, post_count[key], key
    print 'Oldest', oldest, oldcre, oldpost, count, uid
    return dates


def first_last_time(post_time):
    dates = []
    oldest, oldcre, oldpost = 0, datetime.now(), datetime.now()
    for key in post_time.keys():
        posts = post_time[key]
        first, last = min(posts), max(posts)
        delta = last.date() - first.date()
        dates.append(delta.days+1)
        if delta.days > oldest:
            oldest, oldcre, oldpost = delta.days, first, last
    print 'Oldest', oldest, oldcre, oldpost
    return dates


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
    datemax = datetime(max(data).year, max(data).month+1, 1) - timedelta(days=1)
    print min(data), max(data), len(data)
    print datemin, datemax
    bins = month_bins(datemin, datemax, length)

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

if __name__ == '__main__':

    # create_dates = create_time('sed', 'com')
    # pickle.dump(create_dates, open('data/user-create-time.pick', 'w'))
    # create_dates = pickle.load(open('data/user-create-time.pick', 'r'))
    # cdates = create_dates.values()
    # print len(cdates), min(cdates), max(cdates)
    # print mdates.date2num(min(cdates)), mdates.date2num(max(cdates))
    # plot_time(cdates, 1, 'Created time of ED accounts')
    #
    #
    # posts, timelines = timeline_time('sed', 'com', 'timeline')
    # pickle.dump(posts, open('data/user-post-count.pick', 'w'))
    # pickle.dump(timelines, open('data/user-post-time.pick', 'w'))
    # posts = pickle.load(open('data/user-post-count.pick', 'r'))
    # timelines = pickle.load(open('data/user-post-time.pick', 'r'))
    #
    # plot.pdf_plot_one_data(posts.values(), 'counts', 'Timeline counts of ED')
    # timelist = []
    # for v in timelines.values():
    #     timelist += v
    # plot_time(timelist, 1, 'Created time of ED posts')
    #
    #
    # days = relative_time(create_dates, timelines)
    # plot.pdf_plot_one_data(days, 'counts', 'Timeline ages of ED')
    #
    # durings = first_last_time(timelines)
    # plot.pdf_plot_one_data(durings, 'counts', 'Spans of first post and last post')
    #
    #
    # avgs = avg_per_day(posts, timelines)
    # plot.pdf_plot_one_data(avgs, 'counts', 'Average posts per day')

    # for key in posts.keys():
    #     if (posts[key]==0 and key not in timelines) or (posts[key] == len(timelines[key])):
    #         pass
    #     else:
    #         print key

    '''Count the published years of tweets '''
    yearsplit = timeline_split('fed', 'timeline')
    pickle.dump(yearsplit, open('data/fedtyear.pick', 'w'))
    # yearsplit = pickle.load(open('data/fedtyear.pick', 'r'))
    print yearsplit.keys()

