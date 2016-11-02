# -*- coding: utf-8 -*-
"""
Created on 17:18, 09/01/16

@author: wt

Analysis what terms are frequently used in EDs, their friends and followers
The user information in tweet may be not the state-of-the-art.
girl name: https://www.ssa.gov/oact/babynames/decades/names2000s.html
"""

from ohsn.util import db_util as dbt
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from collections import Counter
import re
import os
import random, time


def read_name():
    names = set()
    with open(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)), 'conf', 'name.txt')) as fo:
        for line in fo.readlines():
            tokens = line.split('\t')
            names.add(tokens[3].strip())
    return names


ed_bio_list = set(['bmi', 'cw', 'ugw', 'gw', 'lbs', 'hw', 'lw', 'kg'])
ed_keywords_list = set(['eating disorder', 'eatingdisorder', 'anorexia', 'bulimia', 'anorexic',
                'ana', 'bulimic', 'anorexia nervosa', 'mia', 'thinspo',
                'bulemia', 'purge', 'bulimia nervosa', 'binge',  'selfharm',
                'ednos', 'edprobs', 'edprob', 'proana', 'anamia', 'promia',
                'askanamia', 'bonespo', 'legspo'])

depression_list = set(['depression', 'depressed', 'depressing', 'suicide',
                       'sadness', 'suicidal', 'anxiety', 'death', 'angry',
                       'anxious', 'paranoia', 'nervousness', 'ocd', 'nervous'])

name_pat = re.compile('^(?P<first>[A-Z][a-z]+) (?P<second>[A-Z][a-z]+)$')
age_pat = re.compile('(([1-2][0-9]\s*(year|y/o|yrs|yo))|(^[1-2][0-9]\D)|([;|,•=-]+\s*[1-2][0-9]\s*[;|,•=-]+))', re.IGNORECASE)
#(?P<age>[1-2][0-9])\s*(year|y/o|yrs|yo)  "[;|,•=-]?\s*(?P<age>[1-2][0-9])\s*([;=|,•-]?)"  '(\D|^)(?P<age>[1-2][0-9])\D'

stop = stopwords.words('english')
random.seed(time.time())

girl_names = read_name()


def tokenizer_stoprm(dscp):
    dscp = dscp.strip().lower()
    # dscp = re.sub(r"(?:\@|https?\://)\S+", "", dscp) # replace @ and http://
    dscp = re.sub(r"(?:(rt\ ?@)|@|https?://)\S+", "", dscp) # replace RT @, @ and http://
    tokenizer = RegexpTokenizer(r'\w+')
    tokens = tokenizer.tokenize(dscp)
    new_tokens = []
    for token in tokens:
        token = re.sub(r'[\.0-9]', '', token) #remove all numbers
        if token not in stop and token!='':
            new_tokens.append(token)
    return new_tokens


def check_ed_profile(profile):
    profile = profile.strip().lower().replace("-", "").replace('_', '')
    tokens = tokenizer_stoprm(profile)
    bio_flag, dio_flag = False, False
    for token in tokens:
        if token in ed_bio_list:
            bio_flag = True
        if token in ed_keywords_list: # for single words
            dio_flag = True
    for dio in ed_keywords_list:
        if ' ' in dio and dio in profile: # for phrases
            dio_flag = True

    if bio_flag and dio_flag:
        return True
    else:
        return False


def check_ed_related_profile(profile):
    profile = profile.strip().lower().replace("-", "").replace('_', '')
    tokens = tokenizer_stoprm(profile)
    dio_flag = False
    for token in tokens:
        if token in ed_keywords_list or token in ed_bio_list: # for single words
            dio_flag = True
    for dio in ed_keywords_list:
        if ' ' in dio and dio in profile: # for phrases
            dio_flag = True

    return dio_flag



def check_depression_profile(profile):
    profile = profile.strip().lower().replace("-", "").replace('_', '')
    tokens = tokenizer_stoprm(profile)
    dio_flag = False
    for token in tokens:
        if token in depression_list: # for single words
            dio_flag = True
    for dio in depression_list:
        if ' ' in dio and dio in profile: # for phrases
            dio_flag = True
    return dio_flag


def check_en(user):
    if user['lang'] == 'en' and user['protected']==False:
        return True
    else:
        return False


def check_ed(user):
    profile = user['description']
    if user['lang'] == 'en' and user['protected']==False and profile != None:
        # print check_ed_profile(prof)
        return check_ed_profile(profile)
    else:
        return False


def check_yg(user):
    # prof = user['description']
    if user['lang'] == 'en' and user['protected'] == False and user['verified'] == False:
        name_match = name_pat.search(user['name'].strip())
        # age_match = age_pat.search(prof.strip())
        if name_match and (name_match.group('first') in girl_names):
            return True
    else:
        return False


def check_rd(user):
    if user['lang'] == 'en' and user['protected']==False:
    # probability of level 1 to level 2 is 0.0162914951388, see data_refine.py in ed
        if random.random() <= 0.0163:
            return True
    else:
        return False


def check_depression(user):
    profile = user['description']
    if user['lang'] == 'en' and user['protected']==False and profile != None:
        # print check_ed_profile(prof)
        return check_depression_profile(profile)
    else:
        return False


def check_user(profile, check='N'):
    if check is 'ED':
        return check_ed(profile)
    elif check is 'YG':
        return check_yg(profile)
    elif check is 'DP':
        return check_depression(profile)
    elif check is 'RD':
        return check_rd(profile)
    else:
        return check_en(profile)

def profile_pos():
    db = dbt.db_connect_no_auth('ed')
    stream_db = db['stream']
    stream_db.create_index("id", unique=True)

    seed_user = set([])
    for tweet in stream_db.find({'checked':{'$exists': False}}).limit(1000):
        user = tweet['user']
        if check_en(user):
            seed_user.add(user['screen_name'])
        stream_db.update_one({'id': int(tweet['id_str'])},
                         {'$set':{"checked": True}}, upsert=False)
    return [user for user in seed_user]


def seed_all_profile(stream_db, limit=100):
    # db = dbt.db_connect_no_auth('ed')
    # stream_db = db['stream_users']
    seed_user = []
    for user in stream_db.find({'seeded':{'$exists': False}}).limit(limit):
        seed_user.append(user['id'])
        stream_db.update_one({'id': int(user['id_str'])},
                         {'$set':{"seeded": True}}, upsert=False)
    return seed_user


def common_word(dbname, colname):
    db = dbt.db_connect_no_auth(dbname)
    col = db[colname]
    t_dic = {}
    p_dic = {}
    p_pmi = {}
    a_count = 0
    for user in col.find({}):
        a_count += 1
        profile = user['description']
        tokens = tokenizer_stoprm(profile)
        token_count = Counter(tokens)
        key_list = list(token_count.keys())
        for i in range(len(key_list)):
            token1 = key_list[i]
            t_count = t_dic.get(token1, 0)
            t_dic[token1] = t_count+1
            for j in range(i+1, len(key_list)):
                token2 = key_list[j]
                if token1 > token2:
                    p_key = (token2, token1)
                elif token1 < token2:
                    p_key = (token1, token2)
                else:
                    print 'Error'
                p_count = p_dic.get(p_key, 0)
                p_dic[p_key] = p_count+1

    for t1, t2 in p_dic.keys():
        pmi = float(p_dic[(t1, t2)] * a_count)/(t_dic[t1] * t_dic[t2])
        p_pmi[(t1, t2)] = pmi

    pp_list = {}
    for (t1, t2) in p_pmi.keys():
        if (t_dic[t1] > 5) and (t_dic[t2] > 5):
            if ((t1 in ed_keywords_list) and (t2 not in ed_keywords_list)) or ((t1 not in ed_keywords_list) and (t2 in ed_keywords_list)):
                pp_list[(t1, t2)] = p_pmi[(t1, t2)]
    print len(p_pmi), len(pp_list)
    p_list = sorted(pp_list, key=pp_list.get)
    for i in p_list[-100:]:
        print i, pp_list[i], t_dic[i[0]], t_dic[i[1]]


if __name__ == '__main__':

    db = dbt.db_connect_no_auth('young')
    com = db['stream']
    count = 0
    for user in com.find():
        if check_user(user['user'], 'YG'):
            count += 1
            print user['user']['screen_name']
    print count
    # common_word('fed', 'scom')

    # print girl_names, len(girl_names)

    # print 's' in 'sds'
    # print stop
    # print tokenizer_stoprm('''RT @sociopxthicmind: Lacey #thinspo #thinspiration #goals I am https://t.co/ZHnt3roe4r''')

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

    # print check_random_profile('''anorexic//borderline//fairytales//disney lover//current weight: 54.1kg//height: 163cm//diet coke and cigarettes''')
    # print tokenizer_stoprm('''16, ana, mia, self harm, OCD. CW 100 GW 100 UGW 95. LW 94 HW 110 height 5'3. I will help you reach your goal. DM me to chat about EDs or self harm''')
