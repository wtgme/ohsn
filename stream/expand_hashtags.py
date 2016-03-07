# -*- coding: utf-8 -*-
"""
Created on 10:45 PM, 3/7/16

@author: tw
Expanding the original hashtags
"""

import sys
sys.path.append('..')
import util.db_util as dbt
from collections import Counter
import re



db = dbt.db_connect_no_auth('depression')
stream = db['stream']
hgrex = re.compile(r'(?<=^|(?<=[^a-zA-Z0-9]))#([A-Za-z0-9_]+)')  # for hashtags
hashtags = list()
for tw in stream.find():
    text = tw['text'].lower()
    # print text
    for hashtag in re.findall(hgrex, text):
        hashtags.append(hashtag)
        # print hashtag
print Counter(hashtags).most_common()