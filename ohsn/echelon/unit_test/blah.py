# -*- coding: utf-8 -*-
"""
Created on Tue Jun 23 19:25:38 2015

@author: brendan
"""
import re

e = "jhdsalkjf 404 ;sdj lkdsjf ksdl"
pattern = re.compile('\s+404\s+', re.IGNORECASE)
match = pattern.search(str(e))
if match:
    print "success"
else:
    print "no match"
         