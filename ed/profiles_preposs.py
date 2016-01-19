# -*- coding: utf-8 -*-
"""
Created on 17:18, 09/01/16

@author: wt

Analysis what terms are frequently used in EDs, their friends and followers
The user information in tweet may be not the state-of-the-art.

"""
import sys
sys.path.append('..')
import util.db_util as dbt
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
import re
from collections import Counter
from gensim import corpora, models, similarities

db = dbt.db_connect_no_auth('ed')
stream = db['stream']

bio_list = set(['bmi', 'cw', 'ugw', 'gw', 'lbs', 'hw', 'lw'])
dio_list = set(['eating disorder', 'anorexia', 'bulimia', 'anorexic',
                'ana', 'bulimic', 'anorexia nervosa', 'mia', 'thinspo',
                'bulemia', 'purge', 'bulimia nervosa', 'binge',  'ed',  'selfharm',
                'ednos', 'edprobs', 'edprob', 'proana', 'anamia', 'promia'
                'askanamia', 'bonespo', 'legspo'])

stop = stopwords.words('english')

def tokenizer_stoprm(dscp):
    dscp = dscp.strip().lower()
    # dscp = re.sub(r"(?:\@|https?\://)\S+", "", dscp) # replace @ and http://
    dscp = re.sub(r"(?:(rt\ ?@)|@|https?://)\S+", "", dscp) # replace RT @, @ and http://
    tokenizer = RegexpTokenizer(r'\w+')
    tokens = tokenizer.tokenize(dscp)
    for token in tokens:
        if token in stop:
            tokens.remove(token)
    return tokens


# documents = ["Human machine interface for lab abc computer applications",
#                  "A survey of user opinion of computer system response time",
#                  "The EPS user interface management system",
#                  "System and human system engineering testing of EPS",
#                  "Relation of user perceived response time to error measurement",
#                  "The generation of random binary unordered trees",
#                  "The intersection graph of paths in trees",
#                  "Graph minors IV Widths of trees and well quasi ordering",
#                  "Graph minors A survey"]
# stoplist = set('for a of the and to in'.split())
# texts = [[word for word in document.lower().split() if word not in stoplist]
#              for document in documents]
# from collections import defaultdict
# frequency = defaultdict(int)
# for text in texts:
#     for token in text:
#         frequency[token] += 1
#
# texts = [[token for token in text if frequency[token] > 1]
#          for text in texts]
#
# from pprint import pprint   # pretty-printer
# pprint(texts)

def check_ed(user):
    profile = user['description']
    if user['lang'] == 'en' and user['protected']==False and profile != None:
        profile = profile.strip().lower().replace("-", "").replace('_', '')
        tokens = tokenizer_stoprm(profile)
        bio_flag, dio_flag = False, False
        for token in tokens:
            if token in bio_list:
                bio_flag = True
            if token in dio_list: # for single words
                dio_flag = True
        for dio in dio_list:
            if ' ' in dio and dio in profile: # for phrases
                dio_flag = True

        if bio_flag and dio_flag:
            return True
        else:
            return False


def profile_pos(stream_db = stream):
    seed_user = set([])
    for tweet in stream_db.find():
        user = tweet['user']
        profile = user['description']
        if user['lang'] == 'en' and user['protected']==False and profile != None:
            profile = profile.strip().lower().replace("-", "").replace('_', '')
            tokens = tokenizer_stoprm(profile)
            bio_flag, dio_flag = False, False
            for token in tokens:
                if token in bio_list:
                    bio_flag = True
                if token in dio_list: # for single words
                    dio_flag = True
            for dio in dio_list:
                if ' ' in dio and dio in profile: # for phrases
                    dio_flag = True

            if bio_flag and dio_flag:
                seed_user.add(user['screen_name'])
    return [user for user in seed_user]


print 's' in 'sds'
print tokenizer_stoprm('''Bands•Blades•Suicidal•Depression•SelfHarm•EDNOS• Goal: 70/80 lbs''')

# print 'harm' in dio_list
# print profile_pos()
# sentence = '''RT @sociopxthicmind: Lacey #thinspo #thinspiration #goals https://t.co/ZHnt3roe4r'''
# print sentence
# print tokenizer_stoprm(sentence)
#
# sentence = '''new account SW:145 CW:126.2 GW:105 ... thinspo's are triggering3 too https://t.co/OWz8CH0IZ3'''
# print sentence
# print tokenizer_stoprm(sentence)
#
# sentence = '''RT @deathbeana @jijio @fjaifjeioj: #thinspo Good morn_ing, thins. Time to starve another day. Prepare yourself to be completely pure and skinny. Starve. https://dafds…'''
# print sentence
# print tokenizer_stoprm(sentence)
