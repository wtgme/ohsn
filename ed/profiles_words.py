# -*- coding: utf-8 -*-
"""
Created on 17:18, 09/01/16

@author: wt

Analysis what terms are frequently used in EDs, their friends and followers

"""
import sys
sys.path.append('..')
import util.db_util as dbt
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
import re
from collections import Counter


db = dbt.db_connect_no_auth('ed')
ed_poi = db['poi_ed']

dic = {}
stop = stopwords.words('english')

for user in ed_poi.find():
    dscp = user['description']
    decp = decp.strip().lower()
    dscp = re.sub(r"(?:\@|https?\://)\S+", "", dscp)
    tokenizer = RegexpTokenizer(r'\w+')
    tokens = tokenizer.tokenize(dscp)
    if tokens:
        for token in tokens:
            if token not in stop:
                count = dic.get(token, 0)
                count += 1
                dic[token] = count
cnt = Counter(dic)
for k,v in cnt.most_common(30):
    print '%s: %i' % (k, v)

