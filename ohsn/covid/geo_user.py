import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import ohsn.util.db_util as dbt
from ohsn.api import tweet_lookup, following, lookup
import ohsn.util.io_util as iot
import pymongo
import pandas as pd
import json
import pandas as pd
from ohsn.api import timelines
import datetime
import math
# from __future__ import print_function


# Collect data
def collect_tweets():
    # College tweets based on tweet IDs.
    # df = pd.read_csv('/home/wt/Code/ohsn/ohsn/covid/us_geo.csv')
    df = pd.read_csv('/home/wt/Desktop/Antonella/geo-detail-2020.csv')
    tids = df['Tweet_ID'].tolist()
    tids = [str(int(i)) for i in tids]
    print(len(tids))
    print(tids[:2])


    dbname = 'covid'
    colname = 'geo_user_2020'
    db = dbt.db_connect_no_auth(dbname)
    com = db[colname]

    com.create_index([('user.id', pymongo.ASCENDING),
                        ('id', pymongo.DESCENDING)])
    com.create_index([('id', pymongo.ASCENDING)], unique=True)

    i = 0
    while 100 * i < len(tids):
        ids = tids[i*100: (i+1)*100]
        print(i*100, (i+1)*100)
        tweets = tweet_lookup.get_tweets_info(ids)
        for tweet in tweets:
            try:
                com.insert(tweet)
            except pymongo.errors.DuplicateKeyError:
                pass
        i += 1


def export_tweets():
    # Export tweets with selected fields
    dbname = 'covid'
    colname = 'geo_user_2020'
    db = dbt.db_connect_no_auth(dbname)
    com = db[colname]
    data = {}
    for doc in com.find({}, {'_id': 0}):
        data[doc['id']] = doc
        # tags = []
        # for tag in (doc['entities']['hashtags']):
        #     tags.append([doc['id'], tag['text'].encode('utf-8'), doc['created_at']])
    
    # df = pd.DataFrame(data, columns=['Tweet_ID', 'Hashtag', 'Date'])
    # df.to_csv('./covid/geo_user_tags_2020.csv', index=None) 


    json.dump(data, open('./covid/geo_user_2020.json', 'w'))


def user_set():
    # store user into db. Meaure users' regions via HPC code r_geo 
    dbname = 'covid'
    colname = 'geo_user_2020'
    db = dbt.db_connect_no_auth(dbname)
    com = db[colname]

    com.create_index([('id', pymongo.ASCENDING)], unique=True)
    df = pd.read_csv('./covid/geo_user_2020_remove_null_us_region.csv')
    user_regs = pd.Series(df.region.values,index=df.user).to_dict()

    stream = 'geo_user_2020_stream'
    st = db[stream]

    for doc in st.find({}, {'_id': 0}):
        user = doc['user']
        try:
            if user['id'] in user_regs:
                user['cregion'] = user_regs[user['id']]
                user['level'] = 0
                com.insert_one(doc['user'])
        except pymongo.errors.DuplicateKeyError:
            pass





def retrieve_timeline(dbname, comname, timename):
    print 'Job starts.......'
    '''Connecting db and user collection'''
    db = dbt.db_connect_no_auth(dbname)
    sample_user = db[comname]
    sample_time = db[timename]
    print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "\t" + 'Connecting db well'
    sample_user.create_index([('timeline_scraped_times', pymongo.ASCENDING),
                              ('level', pymongo.ASCENDING)])
    sample_time.create_index([('user.id', pymongo.ASCENDING),
                              ('id', pymongo.DESCENDING)])
    sample_time.create_index([('id', pymongo.ASCENDING)], unique=True)
    print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "\t" + 'Connect Twitter.com'
    # stream_timeline(sample_user, sample_time, 1, 2)
    timelines.stream_timeline(sample_user, sample_time, 1, 100)
    print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'finish timeline for sample users'




def retrieve_followings(dbname, comname):
    # The list of governors are on: https://twitter.com/i/lists/88692902/members 
    # 1. Follow them using personal account
    # 2. Find Twitter user ID based on screen name
    # 2. Collect following for the personal account
    db = dbt.db_connect_no_auth(dbname)
    poi_db = db[comname]
    poi_db.create_index([('timeline_scraped_times', pymongo.ASCENDING),
                              ('level', pymongo.ASCENDING)])
    # seed_list = ['4718137715']
    next_cursor = -1
    params = {'user_id': 4718137715, 'count': 5000, 'stringify_ids':True}
    while next_cursor != 0:
        params['cursor'] = next_cursor
        followees = following.get_followings(params)
        if followees:
            followee_ids = followees['ids']
            list_size = len(followee_ids)
            length = int(math.ceil(list_size/100.0))
            # print length
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'Process followings', list_size, 'for user'
            for index in xrange(length):
                index_begin = index*100
                index_end = min(list_size, index_begin+100)
                profiles = lookup.get_users_info(followee_ids[index_begin:index_end])
                if profiles:
                    print 'user prof:', index_begin, index_end, len(profiles)
                    for profile in profiles:
                        try:
                            profile['level'] = 1
                            poi_db.insert(profile)
                        except pymongo.errors.DuplicateKeyError:
                            pass
            # prepare for next iterator
            next_cursor = followees['next_cursor']
        else:
            break


def identify_governor(dbname, comname):
    states = {'AL': 'Alabama',
                'NY': 'New York',
                'CA': 'California',
                'PR': 'Puerto Rico',
                'SC': 'South Carolina',
                'LA': 'Louisiana',
                'KS': 'Kansas',
                'NJ': 'New Jersey',
                'IA': 'Iowa',
                'IN': 'Indiana',
                'AK': 'Alaska',
                'ID': 'Idaho',
                'WA': 'Washington',
                'GA': 'Georgia',
                'CT': 'Connecticut',
                'FL': 'Florida',
                'TX': 'Texas',
                'NC': 'North Carolina',
                'AZ': 'Arizona',
                'TN': 'Tennessee',
                'PA': 'Pennsylvania',
                'NE': 'Nebraska',
                'HI': 'Hawaii',
                'IL': 'Illinois',
                'KY': 'Kentucky',
                'MS': 'Mississippi',
                'MO': 'Missouri',
                'NV': 'Nevada',
                'WI': 'Wisconsin',
                'DE': 'Delaware',
                'MA': 'Massachusetts',
                'OR': 'Oregon',
                'VA': 'Virginia',
                'NH': 'New Hampshire',
                'ME': 'Maine',
                'CO': 'Colorado',
                'UT': 'Utah',
                'OH': 'Ohio',
                'NM': 'New Mexico',
                'MI': 'Michigan',
                'AR': 'Arkansas',
                'MT': 'Montana',
                'DC': 'District of Columbia',
                'OK': 'Oklahoma',
                'ND': 'North Dakota',
                'WV': 'West Virginia',
                'MD': 'Maryland',
                'RI': 'Rhode Island',
                'GU': 'Guam',
                'MN': 'Minnesota',
                'VT': 'Vermont',
                'SD': 'South Dakota',
                'VI': 'U.S. Virgin Islands',
                'WY': 'Wyoming',
                'MP': 'Northern Mariana Islands',
                'MH': 'Marshall Islands'}

    db = dbt.db_connect_no_auth(dbname)

    sample_user = db[comname]
    states_names = sorted(states.values(), key=len)
    print(states_names)
    data = []
    for user in sample_user.find({}):
        des = user['description'].encode('utf-8')
        if 'governor' in des.lower():
            for state in states_names:
                if state in des:
                    data.append([user['screen_name'], des, state])
                    
    df = pd.DataFrame(data, columns=['screen_name', 'description', 'state'])        
    df.to_csv('governor.csv')


def extract_timeline(dbname, comname, timename, govers, filename):
    db = dbt.db_connect_no_auth(dbname)
    com = db[comname]
    time = db[timename]
    data = []

    for state in govers.keys():
        screen_names = govers[state]
        for screen_name in screen_names:
            gov = com.find_one({'screen_name': screen_name})
            user_id = gov['id']
            for tweet in time.find({'user.id': user_id}):
                retweet = ('retweeted_status' in tweet)
                quote = ('quoted_status' in tweet)
                text = tweet['text'].encode('utf-8')
                data.append([state, user_id, screen_name, tweet['id'], tweet['created_at'], tweet['favorite_count'], tweet['retweet_count'], text, retweet, quote])

    df = pd.DataFrame(data, columns=['state', 'user_id', 'screen_name', 'tid', 'created_at', 'favorite_count', 'retweet_count', 'text', 'retweet', 'quote'])
    df.to_csv(filename, index=None)

# export_tweets()

# user_set()    

# retrieve_timeline('covid', 'geo_user_2020', 'geo_user_2020_timeline')
# retrieve_followings('covid',  'governor')

# retrieve_timeline('covid',  'governor', 'governor_timeline')
# identify_governor('covid',  'governor')



govers = {'NY': ['andrewcuomo', 'NYGovCuomo'],
'CA': ['CAgovernor', 'GavinNewsom'],
'TX': ['GregAbbott_TX', 'GovAbbott'],
'FL': ['RonDeSantisFL', 'GovRonDeSantis']
}


extract_timeline('covid',  'governor', 'governor_timeline', govers, filename='governor_timeline_pop.csv')
