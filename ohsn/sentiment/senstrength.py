# -*- coding: utf-8 -*-
"""
Created on 15:25, 14/04/17

@author: wt
"""

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import os
import shlex, subprocess
import ohsn.util.db_util as dbt
import ohsn.util.io_util as iot
import re
import numpy as np
import datetime
import pickle
rtgrex = re.compile(r'RT (?<=^|(?<=[^a-zA-Z0-9-\.]))@([A-Za-z0-9_]+):')  # for Retweet
mgrex = re.compile(r'(?<=^|(?<=[^a-zA-Z0-9-\.]))@([A-Za-z0-9_]+)')  # for mention
hgrex = re.compile(r'(?<=^|(?<=[^a-zA-Z0-9]))#([A-Za-z0-9_]+)')  # for hashtags
# hgrex = re.compile(r'(?<=^|(?<=[^a-zA-Z0-9-\.]))#([A-Za-z0-9_]+)')  # for hashtags
ugrex = re.compile(r'(https?://[^\s]+)')  # for url

# java -jar SentiStrengthCom.jar sentidata SentiStrength_DataEnglishFeb2017/ input all-tweet.txt scale annotateCol 4 overwrite
# java -jar SentiStrengthCom.jar sentidata SentiStrength_DataEnglishFeb2017/ input retweet.txt scale annotateCol 4 overwrite
# java -jar SentiStrengthCom.jar sentidata SentiStrength_DataEnglishFeb2017/ input net-tweet.txt scale annotateCol 6 overwrite
def rate_sentiment(sentiString):
    # Return positive negative neutral tuple
    MYDIR = os.path.dirname(__file__)
    #open a subprocess using shlex to get the command line string into the correct args list format
    p = subprocess.Popen(shlex.split('java -jar '+os.path.join(MYDIR,'SentiStrengthCom.jar')+' stdin sentidata '
                                 + os.path.join(MYDIR, 'SentiStrength_DataEnglishFeb2017/ scale')),
                     stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    #communicate via stdin the string to be rated. Note that all spaces are replaced with +
    stdout_text, stderr_text = p.communicate(sentiString.replace(" ", "+"))
    #remove the tab spacing between the positive and negative ratings. e.g. 1    -5 -> 1-5
    # stdout_text = stdout_text.rstrip().replace("\t", "")
    return [int(v) for v in stdout_text.rstrip().split()]


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def process_chunks_db(dbname, timename, comname, n=100):
    ''' measure sentistrength for each user
    reduce IO
    '''
    time = dbt.db_connect_col(dbname, timename)
    com = dbt.db_connect_col(dbname, comname)
    MYDIR = os.path.dirname(__file__)

    ids = iot.get_values_one_field(dbname=dbname, colname=comname, fieldname='id', filt={'liwc_anal.result.WC': {'$exists': True},
                                                                                        'senti_100': {'$exists': False}})
    print 'Total users:', len(ids)
    for idlist in list(chunks(ids, n)):
    # for idlist in [[557442390, 2155187931, 2881928495]]: #test
        # read buntch of user tweets
        print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"),'users no:', len(idlist)
        f = open('tem.txt', 'w')
        id_count = []
        for uid in idlist:
            i = 0
            for tweet in time.find({'user.id': uid}).sort([("id", 1)]): # time from before to now
                if 'retweeted_status' in tweet:
                    continue
                elif 'quoted_status' in tweet:
                    continue
                else:
                    text = tweet['text'].encode('utf8')
                    # replace RT, @, # and Http://
                    text = rtgrex.sub('', text)
                    text = mgrex.sub('', text)
                    text = hgrex.sub('', text)
                    text = ugrex.sub('', text)
                    words = text.strip().split()
                    if len(words) > 0:
                        # print tweet['created_at']
                        print >> f, str(tweet['id']) + '\t'+ str(uid)+'\t' + ' '.join(words)
                        i += 1
            if i > 0:
                id_count.append((uid, i))
        f.close()

        '''Sentiment process'''
        # java -jar SentiStrengthCom.jar sentidata SentiStrength_DataEnglishFeb2017/ input tweets.txt scale annotateCol 3 overwrite
        #open a subprocess using shlex to get the command line string into the correct args list format
        p = subprocess.Popen(shlex.split('java -jar '+os.path.join(MYDIR,'SentiStrengthCom.jar') +' sentidata '
                                     + os.path.join(MYDIR, 'SentiStrength_DataEnglishFeb2017/')
                                         + ' input tem.txt annotateCol 3 overwrite'),
                 stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.communicate()

        '''processs results'''
        fr = open('tem.txt', 'r')
        lines = fr.readlines()
        index = 0
        for uid,i in id_count:
            half = i - 100
            if half < 100:
                half = i/2
            pos1, neg1, scale1, pos2, neg2, scale2 = [], [], [], [], [], []
            reslut = {'N': i}
            for j, line in enumerate(lines[index: index+i]):
                tokens = line.strip().split('\t')
                pos = int(tokens[-2])
                neg = int(tokens[-1])
                scale = pos + neg
                if j < half:
                    pos1.append(pos)
                    neg1.append(neg)
                    scale1.append(scale)
                else:
                    pos2.append(pos)
                    neg2.append(neg)
                    scale2.append(scale)
            if len(pos1) > 0:
                prior = {'N': len(pos1),
                         'posm': np.mean(pos1), 'posstd': np.std(pos1),
                         'negm': np.mean(neg1), 'negstd': np.std(neg1),
                         'scalem': np.mean(scale1), 'scalestd': np.std(scale1)}
                reslut['prior'] = prior
            if len(pos2) > 0:
                post = {'N': len(pos2),
                        'posm': np.mean(pos2), 'posstd': np.std(pos2),
                         'negm': np.mean(neg2), 'negstd': np.std(neg2),
                         'scalem': np.mean(scale2), 'scalestd': np.std(scale2)}
                reslut['post'] = post
            whole = {'N': len(pos1+pos2),
                     'posm': np.mean(pos1+pos2), 'posstd': np.std(pos1+pos2),
                     'negm': np.mean(neg1+neg2), 'negstd': np.std(neg1+neg2),
                     'scalem': np.mean(scale1+scale2), 'scalestd': np.std(scale1+scale2)}
            reslut['whole'] = whole
            # print uid,  reslut
            com.update_one({'id': uid}, {'$set': {'senti_100.mined': True, 'senti_100.result': reslut}}, upsert=False)
            index += i
        fr.close()


def process_chunks_db_multiperiod(dbname, timename, comname, n=100):
    ''' measure sentistrength for each user
    reduce IO
    '''
    time = dbt.db_connect_col(dbname, timename)
    com = dbt.db_connect_col(dbname, comname)
    MYDIR = os.path.dirname(__file__)

    ids = iot.get_values_one_field(dbname=dbname, colname=comname, fieldname='id', filt={'liwc_anal.result.WC': {'$exists': True},
                                                                               'level':1})
    user_series = {}
    print 'Total users:', len(ids)
    for idlist in list(chunks(ids, n)):
    # for idlist in [[557442390, 2155187931, 2881928495]]: #test
        # read buntch of user tweets
        print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"),'users no:', len(idlist)
        f = open('tem.txt', 'w')
        id_count = []
        for uid in idlist:
            i = 0
            for tweet in time.find({'user.id': uid}).sort([("id", 1)]): # time from before to now
                if 'retweeted_status' in tweet:
                    continue
                elif 'quoted_status' in tweet:
                    continue
                else:
                    text = tweet['text'].encode('utf8')
                    # replace RT, @, # and Http://
                    text = rtgrex.sub('', text)
                    text = mgrex.sub('', text)
                    text = hgrex.sub('', text)
                    text = ugrex.sub('', text)
                    words = text.strip().split()
                    if len(words) > 0:
                        # print tweet['created_at']
                        print >> f, str(tweet['id']) + '\t'+ str(uid)+'\t' + ' '.join(words)
                        i += 1
            if i > 0:
                id_count.append((uid, i))
        f.close()

        '''Sentiment process'''
        # java -jar SentiStrengthCom.jar sentidata SentiStrength_DataEnglishFeb2017/ input tweets.txt scale annotateCol 3 overwrite
        #open a subprocess using shlex to get the command line string into the correct args list format
        p = subprocess.Popen(shlex.split('java -jar '+os.path.join(MYDIR,'SentiStrengthCom.jar') +' sentidata '
                                     + os.path.join(MYDIR, 'SentiStrength_DataEnglishFeb2017/')
                                         + ' input tem.txt annotateCol 3 overwrite'),
                 stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.communicate()

        '''processs results'''
        fr = open('tem.txt', 'r')
        lines = fr.readlines()
        index = 0

        for uid, i in id_count:
            pos1, neg1, scale1, usentis = [], [], [], []
            uindex = 0
            for j, line in enumerate(lines[index: index+i]):
                tokens = line.strip().split('\t')
                pos = int(tokens[-2])
                neg = int(tokens[-1])
                scale = pos + neg
                if uindex < 50:
                    pos1.append(pos)
                    neg1.append(neg)
                    scale1.append(scale)
                    uindex += 1
                else:
                    usentis.append(np.mean(scale1))
                    uindex = 0
            user_series[uid] = usentis
            index += i
        fr.close()
    pickle.dump(user_series, open('data/core-ed-series-50.pick', 'w'))


def process_db(dbname, timename, comname):
    ''' measure sentistrength for each user
    too much IO
    '''
    time = dbt.db_connect_col(dbname, timename)
    com = dbt.db_connect_col(dbname, comname)
    MYDIR = os.path.dirname(__file__)

    ids = iot.get_values_one_field(dbname=dbname, colname=comname, fieldname='id', filt={"timeline_count": {'$gt': 0},
                                                                                         'senti': {'$exists': False}})

    # for user in com.find({"timeline_count": {'$gt': 0}}, ['id'], no_cursor_timeout=True):
    for uid in ids:
        f = open('tem.txt', 'w')
        i = 0
        # uid = user['id']
        for tweet in time.find({'user.id': uid}).sort([("id", 1)]): # time from before to now
            if 'retweeted_status' in tweet:
                continue
            elif 'quoted_status' in tweet:
                continue
            else:
                text = tweet['text'].encode('utf8')
                # replace RT, @, # and Http://
                text = rtgrex.sub('', text)
                text = mgrex.sub('', text)
                text = hgrex.sub('', text)
                text = ugrex.sub('', text)
                words = text.strip().split()
                if len(words) > 0:
                    # print tweet['created_at']
                    print >> f, str(tweet['id']) + '\t'+ str(uid)+'\t' + ' '.join(words)
                    i += 1
        f.close()

        if i > 0:
            '''Sentiment'''
            # java -jar SentiStrengthCom.jar sentidata SentiStrength_DataEnglishFeb2017/ input tweets.txt scale annotateCol 3 overwrite
            #open a subprocess using shlex to get the command line string into the correct args list format
            p = subprocess.Popen(shlex.split('java -jar '+os.path.join(MYDIR,'SentiStrengthCom.jar') +' sentidata '
                                         + os.path.join(MYDIR, 'SentiStrength_DataEnglishFeb2017/')
                                             + ' input tem.txt annotateCol 3 overwrite'),
                     stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            p.communicate()

            '''processs results'''
            reslut = {'N': i}
            half = i/2
            pos1, neg1, scale1, pos2, neg2, scale2 = [], [], [], [], [], []

            fr = open('tem.txt', 'r')
            for j, line in enumerate(fr.readlines()):
                tokens = line.strip().split('\t')
                # print tokens
                pos = int(tokens[-2])
                neg = int(tokens[-1])
                scale = pos + neg
                if j < half:
                    pos1.append(pos)
                    neg1.append(neg)
                    scale1.append(scale)
                else:
                    pos2.append(pos)
                    neg2.append(neg)
                    scale2.append(scale)
            if len(pos1) > 0:
                prior = {'N': len(pos1),
                         'posm': np.mean(pos1), 'posstd': np.std(pos1),
                         'negm': np.mean(neg1), 'negstd': np.std(neg1),
                         'scalem': np.mean(scale1), 'scalestd': np.std(scale1)}
                reslut['prior'] = prior
            if len(pos2) > 0:
                post = {'N': len(pos2),
                        'posm': np.mean(pos2), 'posstd': np.std(pos2),
                         'negm': np.mean(neg2), 'negstd': np.std(neg2),
                         'scalem': np.mean(scale2), 'scalestd': np.std(scale2)}
                reslut['post'] = post
            whole = {'N': len(pos1+pos2),
                     'posm': np.mean(pos1+pos2), 'posstd': np.std(pos1+pos2),
                     'negm': np.mean(neg1+neg2), 'negstd': np.std(neg1+neg2),
                     'scalem': np.mean(scale1+scale2), 'scalestd': np.std(scale1+scale2)}
            reslut['whole'] = whole
            com.update_one({'id': uid}, {'$set': {'senti.mined': True, 'senti.result': reslut}}, upsert=False)
            fr.close()


if __name__ == '__main__':
    # print rate_sentiment('Everynight I hope i wake up thinner, at my UGW. One day it will happen.')
    # print rate_sentiment('I talk to YOU')

    process_chunks_db_multiperiod(dbname='fed', timename='timeline', comname='scom')
    # process_chunks_db(dbname='fed', timename='timeline', comname='com')
    # process_chunks_db(dbname='younger', timename='timeline', comname='scom')
    # process_chunks_db(dbname='random', timename='timeline', comname='scom')
