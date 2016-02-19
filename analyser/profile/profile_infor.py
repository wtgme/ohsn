# -*- coding: utf-8 -*-
"""
Created on 13:56, 18/02/16

@author: wt

Compare the difference from their profile information
"""

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
import util.db_util as dbt
import pymongo
import networkx as nx
import util.plot_util as plot
import math
from colormath.color_objects import LabColor, sRGBColor
from colormath.color_diff import delta_e_cie2000
from colormath.color_conversions import convert_color


def get_field_values(db_name, field):
    db = dbt.db_connect_no_auth(db_name)
    poi = db['com']
    counts = []
    for user in poi.find({'level': 1}, [field]):
        counts.append(user[field])
    return counts


def color_wheel():
    color_list = []
    with open('color.list') as fo:
        lines = fo.readlines()
        for i in xrange(len(lines)/3):
            color_list.append(labc([float(line.strip()) for line in lines[3*i:3*i+3]]))
    return color_list


def labc(clist):
    return LabColor(clist[0], clist[1], clist[2], illuminant='d50')


def srgbc(rgbv):
    return sRGBColor(float(int(rgbv[0:2], 16)), float(int(rgbv[2:4], 16)), float(int(rgbv[4:6], 16)), is_upscaled=True)


def cate_color(colors, standards):
    color_index = []
    for color in colors:
        rgb = srgbc(color)
        lab = convert_color(rgb, LabColor, target_illuminant='d50')
        mindis, minindex = 10000, 0
        for index in xrange(len(standards)):
            distance = delta_e_cie2000(lab, standards[index])
            if distance < mindis:
                mindis = distance
                minindex = index + 1
        # print mindis, minindex
        color_index.append(minindex)
    return color_index


def color_dis(dbname, colorname):
    background = get_field_values(dbname, colorname)
    standers = color_wheel()
    return cate_color(background, standers)


randomc = color_dis('random', 'profile_background_color')
youngc = color_dis('young', 'profile_background_color')
fedc = color_dis('fed', 'profile_background_color')
plot.plot_pdf_two_data(randomc, fedc)

# plot.plot_pdf_mul_data([randomc, youngc, fedc], ['--bo', '--r*', '--k+'], ['random', 'younger', 'ed'])

http://stackoverflow.com/questions/14095849/calculating-the-analogous-color-with-python
    
# get_field_values('fed', 'followers_count')
# get_field_values('fed', 'friends_count')
# get_field_values('fed', 'favourites_count')
# get_field_values('fed', 'statuses_count')


# color_list = read_colors('color.list')
# print color_list
# print len(color_list)
# print delta_e_cie2000(labc(color_list[0]), labc(color_list[1]))
# print delta_e_cie2000(labc(color_list[0]), labc(color_list[37]))
# print delta_e_cie2000(labc(color_list[0]), labc(color_list[36]))
# print delta_e_cie2000(labc(color_list[3]), labc(color_list[4]))

