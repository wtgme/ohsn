# -*- coding: utf-8 -*-
"""
Created on Sat Jun 20 10:07:27 2015

@author: brendan
"""
from collections import Counter
import re

keywords = ['anorexic', 
                    'anorexia',
                    'anorexia-purging',
                    'diagnosed',
                    'relapse',
                    'recovery',
                    'inpatient',
                    'ed',
                    'eating',
                    'eating-disorder',
                    'ednos',
                    'ed-nos',
                    'bulimic',
                    'bulimia',
                    'depressed',
                    'depression',
                    'anxiety',
                    'ocd',
                    'suicidal',
                    'skinny',
                    'fat',
                    'harm',
                    'self-harm',
                    'selfharm',
                    'cutter',
                    'ana',
                    'mia',
                    'starving',
                    'diet',
                    'insomnia']

# description = "16 y/o Girl | Eating Disorder | And many other diagnoses | Stuck between relapse and recovery |"                    
# description = "secret account. sixteen years old. want to be skinny and pretty. CW:106 GW1:100 GW2:93 UGW:87"                   
description = " EDNOS / anxiety / OCD / 5'5 / sw: 135 cw: 123 gw: 105"

cnt = Counter()
words = re.findall('\w+', description.lower())
for word in words:
    if word in keywords:
        cnt[word] += 1
        
print cnt
print sum(cnt.values())