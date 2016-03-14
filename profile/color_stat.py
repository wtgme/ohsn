# -*- coding: utf-8 -*-
"""
Created on 12:55 PM, 3/1/16

@author: tw


Background color ----> "profile_background_color": "EBEBEB"
Theme color ----> "profile_link_color": "990000"
Profile image small block ----> profile_image_url
Profile image top ----> "profile_banner_url". if profile_banner_url is not none, user has modified the banner
If profile image small block is modefied, default egg avatar -----> default_profile_image": false 头像
default Theme color: 0084B4 Background color: C0DEED
Theme color and background colors are default ------> default_profile": true

"""

import datetime
import pickle
import urllib2

from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000
from colormath.color_objects import LabColor, sRGBColor

import image_color
import util.plot_util as plot


def color_wheel():
    # read color wheel
    color_list = []
    with open('color.list') as fo:
        lines = fo.readlines()
        for i in xrange(len(lines)/3):
            color_list.append(labc([float(line.strip()) for line in lines[3*i:3*i+3]]))
    return color_list


def labc(clist):
    # New Color object with LAB format
    return LabColor(clist[0], clist[1], clist[2], illuminant='d50')


def srgbc(rgbv):
    # New Color object with Standard RGB format
    rgbv = rgbv.replace('#', '')
    return sRGBColor(float(int(rgbv[0:2], 16)), float(int(rgbv[2:4], 16)), float(int(rgbv[4:6], 16)), is_upscaled=True)


def cate_color(colors, standards, format='rgb'):
    # Map color to the most similar color in color wheel
    color_index = []
    for color in colors:
        if format is 'rgb':
            rgb = srgbc(color)
            lab = convert_color(rgb, LabColor, target_illuminant='d50')
        elif format is 'lab':
            lab = labc(color)
        mindis, minindex = 10000, 0
        for index in xrange(len(standards)):
            distance = delta_e_cie2000(lab, standards[index])
            if distance < mindis:
                mindis = distance
                minindex = index + 1
        # print mindis, minindex
        color_index.append(minindex)
    return color_index


def rgbstandards(standards):
    # Plot color wheel: but first transform LAB formats of color wheel to sRGB formats
    rgblist = []
    for lab in standards:
        rgb = convert_color(lab, sRGBColor, target_illuminant='d50')
        rgblist.append(rgb.get_rgb_hex())
    return rgblist


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
            main_colors = image_color.main_colors(url)
        except urllib2.HTTPError:
            continue
        # print main_colors
        colorlist.extend(main_colors)
        if i%100 == 0:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'finish users', i
    return colorlist


def image_color_compare():
    # ed_urls = io.get_values_one_field('fed', 'com', 'profile_banner_url', {'level': 1, 'profile_banner_url': {'$exists': True}})
    # rd_urls = io.get_values_one_field('random', 'com', 'profile_banner_url', {'level': 1, 'profile_banner_url': {'$exists': True}})
    # yg_urls = io.get_values_one_field('young', 'com', 'profile_banner_url', {'level': 1, 'profile_banner_url': {'$exists': True}})
    #
    # pickle.dump(ed_urls, open("data/edimage.pick", "wb"))
    # pickle.dump(rd_urls, open("data/rdimage.pick", "wb"))
    # pickle.dump(yg_urls, open("data/ygimage.pick", "wb"))
    standers = color_wheel()
    rgbstan = rgbstandards(standers)
    rgbstan[-1] = '#FFFFFF'

    ed_urls = pickle.load(open("data/edimage.pick", "rb"))
    rd_urls = pickle.load(open("data/rdimage.pick", "rb"))
    yg_urls = pickle.load(open("data/ygimage.pick", "rb"))

    # ed_cs = get_image_color(ed_urls)
    # pickle.dump(ed_cs, open("data/edics.pick", "wb"))
    ed_cs = pickle.load(open("data/edics.pick", "rb"))
    edi = cate_color(ed_cs, standers, 'lab')
    plot.color_bars(rgbstan, edi)

    # rd_cs = get_image_color(rd_urls)
    # pickle.dump(rd_cs, open("data/rdics.pick", "wb"))
    # rd_cs = pickle.load(open("data/rdics.pick", "rb"))
    # rdi = cate_color(rd_cs, standers, 'lab')
    # plot.color_bars(rgbstan, rdi)

    # yg_cs = get_image_color(yg_urls)
    # pickle.dump(yg_cs, open("data/ygics.pick", "wb"))
    # ygi = cate_color(yg_cs, standers, 'lab')
    # plot.color_bars(rgbstan, ygi)

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
