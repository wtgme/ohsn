# -*- coding: utf-8 -*-
"""
Created on 6:10 PM, 3/1/16

@author: tw
"""

import os

from skimage.io import imread
from sklearn.cluster import KMeans
from skimage.color import rgb2lab
import numpy as np
from sklearn.utils import shuffle
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000
from colormath.color_objects import LabColor, sRGBColor


def main_colors(filename):
    # return cluster centers, with LAB formats
    img = imread(filename)
    w, h, d = img.shape
    if d > 3:
        img = img[..., :3]
    imglab = rgb2lab(img)

    w, h, d = original_shape = tuple(imglab.shape)
    assert d == 3
    image_array = np.reshape(imglab, (w * h, d))

    image_array_sample = shuffle(image_array, random_state=0)[:1000]
    kmeans = KMeans(n_clusters=3, random_state=0).fit(image_array_sample)
    return kmeans.cluster_centers_


# colors = main_colors('data/black.png')
# colors = main_colors('https://pbs.twimg.com/profile_banners/3327720838/1437934435')
# print colors
# centers = np.reshape(colors, (1, 3, 3))
# print lab2rgb(centers)

def color_wheel():
    # read color wheel
    MYDIR = os.path.dirname(__file__)
    color_list = []
    with open(os.path.join(MYDIR, 'color-list'), 'r') as fo:
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


def cate_color(colors, standards, cformat='rgb'):
    # Map color to the most similar color in color wheel
    color_index = []
    for color in colors:
        minindex = color_map(color, cformat, standards)
        color_index.append(minindex)
    return color_index


def color_map(color, standards, cformat='rgb'):
    if cformat == 'rgb':
        rgb = srgbc(color)
        lab = convert_color(rgb, LabColor, target_illuminant='d50')
    elif cformat == 'lab':
        lab = labc(color)
    mindis, minindex = 10000000, 0
    for index in xrange(len(standards)):
        distance = delta_e_cie2000(lab, standards[index])
        if distance < mindis:
            mindis = distance
            minindex = index + 1
    return minindex


def rgbstandards(standards):
    # Plot color wheel: but first transform LAB formats of color wheel to sRGB formats
    rgblist = []
    for lab in standards:
        # print '--------------------'
        # print lab
        rgb = convert_color(lab, sRGBColor, target_illuminant='d50')
        # print rgb
        # print convert_color(rgb, LabColor, target_illuminant='d50')
        rgblist.append(rgb.get_rgb_hex())
    return rgblist


def color_standers():
    labstanders = color_wheel()
    rgbstan = rgbstandards(labstanders)
    rgbstan[-1] = '#FFFFFF'
    return (labstanders, rgbstan)

def get_color_sent():
    MYDIR = os.path.dirname(__file__)
    cmap = {}
    with open(os.path.join(MYDIR, 'color-cate'), 'r') as fo:
        lines = fo.readlines()
        for i in xrange(len(lines)):
            for index in lines[i].split(' '):
                cmap[int(index)] = i+1
    return cmap

# labstanders, rgbstan = color_standers()
# print labstanders
# print rgbstan
# plot.color_bars(rgbstan, [i+1 for i in range(38)])
# cs = get_color_sent()
# print len(cs)
# print cs
