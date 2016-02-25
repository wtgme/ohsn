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
import random, time


ed_bio_list = set(['bmi', 'cw', 'ugw', 'gw', 'lbs', 'hw', 'lw', 'kg'])
ed_keywords_list = set(['eating disorder', 'eatingdisorder', 'anorexia', 'bulimia', 'anorexic',
                'ana', 'bulimic', 'anorexia nervosa', 'mia', 'thinspo',
                'bulemia', 'purge', 'bulimia nervosa', 'binge',  'selfharm',
                'ednos', 'edprobs', 'edprob', 'proana', 'anamia', 'promia',
                'askanamia', 'bonespo', 'legspo'])

young_bio_list = set(['year', 'yrs', 'years'])
young_list = set(['girl', 'girls'])

depression_list = set(['depression', 'depressed', 'depressing', 'suicide',
                       'sadness', 'suicidal', 'anxiety', 'death', 'angry',
                       'anxious', 'paranoia', 'nervousness', 'ocd', 'nervous'])


stop = stopwords.words('english')
random.seed(time.time())

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


def check_young_profile(profile):
    profile = profile.strip().lower().replace("-", "").replace('_', '')
    tokens = tokenizer_stoprm(profile)
    bio_flag, dio_flag = False, False
    for token in tokens:
        if token in young_bio_list:
            bio_flag = True
        if token in young_list: # for single words
            dio_flag = True
    bio_flag = True
    for dio in young_list:
        if ' ' in dio and dio in profile: # for phrases
            dio_flag = True

    if bio_flag and dio_flag:
        return True
    else:
        return False


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
        # print check_ed_profile(profile)
        return check_ed_profile(profile)
    else:
        return False


def check_girl(user):
    profile = user['description']
    if user['lang'] == 'en' and user['protected']==False and profile != None:
        # print check_ed_profile(profile)
        return check_young_profile(profile)
    else:
        return False


def check_random(user):
    if user['lang'] == 'en' and user['protected']==False:
    # probability of level 1 to level 2 is 0.0162914951388, see data_refine.py in ed
        if random.random() <= 0.02:
            return True
        else:
            return False
    else:
        return False


def check_depression(user):
    profile = user['description']
    if user['lang'] == 'en' and user['protected']==False and profile != None:
        # print check_ed_profile(profile)
        return check_depression_profile(profile)
    else:
        return False


def profile_pos():
    db = dbt.db_connect_no_auth('ed')
    stream_db = db['stream']
    stream_db.create_index("id", unique=True)

    seed_user = set([])
    for tweet in stream_db.find({'checked':{'$exists': False}}).limit(1000):
        user = tweet['user']
        if check_en(user):
            seed_user.add(user['screen_name'])
        stream_db.update({'id': int(tweet['id_str'])},
                         {'$set':{"checked": True}}, upsert=False)
    return [user for user in seed_user]


def seed_all_profile(stream_db):
    # db = dbt.db_connect_no_auth('ed')
    # stream_db = db['stream_users']
    seed_user = []
    for user in stream_db.find({'seeded':{'$exists': False}}).limit(100):
        seed_user.append(user['screen_name'])
        stream_db.update({'id': int(user['id_str'])},
                         {'$set':{"seeded": True}}, upsert=False)
    return seed_user


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