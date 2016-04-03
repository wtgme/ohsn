# -*- coding: utf-8 -*-
"""
Created on 11:39 AM, 3/1/16

@author: tw
Identify the main colors of an image
See: http://charlesleifer.com/blog/using-python-and-k-means-to-find-the-dominant-colors-in-images/

#######################discarded......###############
"""

from collections import namedtuple
import urllib, cStringIO
import random
try:
    import Image
except ImportError:
    from PIL import Image

Point = namedtuple('Point', ('coords', 'n', 'ct'))
Cluster = namedtuple('Cluster', ('points', 'center', 'n'))


def get_points(img):
    points = []
    w, h = img.size
    for count, color in img.getcolors(w * h):
        points.append(Point(color, 3, count))
    return points

rtoh = lambda rgb: '#%s' % ''.join(('%02x' % p for p in rgb))


def colorz(filename, n=3):
    try:
        img = Image.open(filename)
    except IOError:
        im_file = cStringIO.StringIO(urllib.urlopen(filename).read())
        try:
            img = Image.open(im_file)
        except IOError:
            return []
    img.thumbnail((200, 200))

    points = get_points(img)
    clusters = kmeans(points, n, 1)
    rgbs = [map(int, c.center.coords) for c in clusters]
    return map(rtoh, rgbs)


def euclidean(p1, p2):
    return (sum([
        (p1.coords[i] - p2.coords[i]) ** 2 for i in range(p1.n)
    ]))


def calculate_center(points, n):
    vals = [0.0 for i in range(n)]
    plen = 0
    for p in points:
        plen += p.ct
        for i in range(n):
            vals[i] += (p.coords[i] * p.ct)
    return Point([(v / plen) for v in vals], n, 1)


def kmeans(points, k, min_diff):
    try:
        clusters = [Cluster([p], p, p.n) for p in random.sample(points, k)]
    except ValueError:
        return [Cluster([points[0]], points[0], points[0].n)]*3

    while True:
        plists = [[] for i in range(k)]

        for p in points:
            smallest_distance = float('Inf')
            for i in range(k):
                distance = euclidean(p, clusters[i].center)
                if distance < smallest_distance:
                    smallest_distance = distance
                    idx = i
            plists[idx].append(p)

        diff = 0
        for i in range(k):
            old = clusters[i]
            center = calculate_center(plists[i], old.n)
            new = Cluster(plists[i], center, old.n)
            clusters[i] = new
            diff = max(diff, euclidean(old.center, new.center))

        if diff < min_diff:
            break

    return clusters

# print colorz('https://pbs.twimg.com/profile_banners/3214409921/1451516411')
# print colorz('http://www.nancybw.com/images/0006.jpg')
# print colorz('test.jpg')
# print colorz('test.jpg')
# print colorz('test.jpg')