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


stop = stopwords.words('english')

def tokenizer_stoprm(dscp):
    token_list = []
    dscp = dscp.strip().lower()
    # dscp = re.sub(r"(?:\@|https?\://)\S+", "", dscp) # replace @ and http://
    dscp = re.sub(r"(?:(rt\ ?@)|@|https?://)\S+", "", dscp) # replace RT @, @ and http://
    tokenizer = RegexpTokenizer(r'\w+')
    tokens = tokenizer.tokenize(dscp)
    for token in tokens:
        if token in stop:
            tokens.remove(token)
    return tokens




sentence = '''RT @sociopxthicmind: Lacey #thinspo #thinspiration #goals https://t.co/ZHnt3roe4r'''
print sentence
print tokenizer_stoprm(sentence)

sentence = '''... thinspo's are triggering too https://t.co/OWz8CH0IZ3'''
print sentence
print tokenizer_stoprm(sentence)

sentence = '''RT @deathbeana @jijio @fjaifjeioj: #thinspo Good morning, thins. Time to starve another day. Prepare yourself to be completely pure and skinny. Starve. https://dafds…'''
print sentence
print tokenizer_stoprm(sentence)
