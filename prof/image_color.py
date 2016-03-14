# -*- coding: utf-8 -*-
"""
Created on 6:10 PM, 3/1/16

@author: tw
"""

from skimage.io import imread
from sklearn.cluster import KMeans
from skimage.color import rgb2lab
import numpy as np
from sklearn.utils import shuffle


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


# colors = main_colors('black.png')
# colors = main_colors('https://pbs.twimg.com/profile_banners/3327720838/1437934435')
# print colors
# centers = np.reshape(colors, (1, 3, 3))
# print lab2rgb(centers)

