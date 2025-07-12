# -*- coding: utf-8 -*-
"""
Created on 12:55 PM, 3/1/16

@author: tw


Background color ----> "profile_background_color": "EBEBEB"
Theme color ----> "profile_link_color": "990000"
Profile image small block ----> profile_image_url
Profile image top ----> "profile_banner_url". if profile_banner_url is not none, user has modified the banner
If prof image small block is modefied, default egg avatar -----> default_profile_image": false 头像
default Theme color: 0084B4 Background color: C0DEED
Theme color and background colors are default ------> default_profile": true

"""

import ohsn.util.io_util as io
import datetime
import pickle
import urllib2
from image_color import *
from ohsn import util as plot


def rmdefault(clist):
    # Remove the default color on Twitter.
    # default Theme color: 0084B4 Background color: C0DEED
    return [co for co in clist if co!='0084B4']


def get_image_color(urllist):
    print len(urllist)
    colorlist = []
    i = 0
    for url in urllist:
        i += 1
        try:
            main_colors = main_colors(url)
        except urllib2.HTTPError:
            continue
        # print main_colors
        colorlist.extend(main_colors)
        if i%100 == 0:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'finish users', i
    return colorlist


def image_color_compare():
    ed_urls = io.get_values_one_field('fed', 'com', 'profile_banner_url', {'level': 1, 'profile_banner_url': {'$exists': True}})
    rd_urls = io.get_values_one_field('random', 'com', 'profile_banner_url', {'level': 1, 'profile_banner_url': {'$exists': True}})
    yg_urls = io.get_values_one_field('young', 'com', 'profile_banner_url', {'level': 1, 'profile_banner_url': {'$exists': True}})

    pickle.dump(ed_urls, open("data/edimage.pick", "wb"))
    pickle.dump(rd_urls, open("data/rdimage.pick", "wb"))
    pickle.dump(yg_urls, open("data/ygimage.pick", "wb"))
    standers, rgbstan = color_standers()

    # ed_urls = pickle.load(open("data/edimage.pick", "rb"))
    # rd_urls = pickle.load(open("data/rdimage.pick", "rb"))
    # yg_urls = pickle.load(open("data/ygimage.pick", "rb"))

    ed_cs = get_image_color(ed_urls)
    pickle.dump(ed_cs, open("data/edics.pick", "wb"))
    ed_cs = pickle.load(open("data/edics.pick", "rb"))
    edi = cate_color(ed_cs, standers, 'lab')
    plot.color_bars(rgbstan, edi)

    rd_cs = get_image_color(rd_urls)
    pickle.dump(rd_cs, open("data/rdics.pick", "wb"))
    rd_cs = pickle.load(open("data/rdics.pick", "rb"))
    rdi = cate_color(rd_cs, standers, 'lab')
    plot.color_bars(rgbstan, rdi)

    yg_cs = get_image_color(yg_urls)
    pickle.dump(yg_cs, open("data/ygics.pick", "wb"))
    ygi = cate_color(yg_cs, standers, 'lab')
    plot.color_bars(rgbstan, ygi)

image_color_compare()


def color_compare():
    standers = color_wheel()
    # print cate_color(['C0DEED'], standers)
    rgbstan = rgbstandards(standers)
    rgbstan[-1] = '#FFFFFF'

    # randomc = get_field_values('random', 'profile_link_color')
    # youngc = get_field_values('young', 'profile_link_color')
    # fedc = get_field_values('fed', 'profile_link_color')
    # pickle.dump(randomc, open("data/randomc.pick", "wb"))
    # pickle.dump(youngc, open("data/youngc.pick", "wb"))
    # pickle.dump(fedc, open("data/fedc.pick", "wb"))

    randomc = pickle.load(open("data/randomc.pick", "rb"))
    youngc = pickle.load(open("data/youngc.pick", "rb"))
    fedc = pickle.load(open("data/fedc.pick", "rb"))

    randomc = rmdefault(randomc)
    youngc = rmdefault(youngc)
    fedc = rmdefault(fedc)

    randomci = cate_color(randomc, standers)
    youngci = cate_color(youngc, standers)
    fedci = cate_color(fedc, standers)

    plot.color_bars(rgbstan, fedci)

    # plot.plot_pdf_two_data(randomc, fedc)

    # plot.plot_pdf_mul_data([randomc, youngc, fedc], ['--bo', '--r*', '--k+'], ['random', 'younger', 'ed'])

    # http://stackoverflow.com/questions/14095849/calculating-the-analogous-color-with-python
