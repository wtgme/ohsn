# -*- coding: utf-8 -*-
"""
Created on Sun Jun 21 17:23:54 2015

@author: brendan
"""

list = [('abc', 121),('abc', 231),('abc', 148), ('abc',221)]

list = sorted(list, key=lambda x: x[1], reverse=True)

print list
