# -*- coding: utf-8 -*-
"""
Created on 14:51, 20/05/16

@author: wt
"""
import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
from ohsn.util import db_util as dbt
from ohsn.util import io_util as io
import re


def data_4_opinionfinder(dbname, comname, timename, outpath, filter={}):
    db = dbt.db_connect_no_auth(dbname)
    time = db[timename]

    rtgrex = re.compile(r'RT (?<=^|(?<=[^a-zA-Z0-9-\.]))@([A-Za-z0-9_]+):')  # for Retweet
    mgrex = re.compile(r'(?<=^|(?<=[^a-zA-Z0-9-\.]))@([A-Za-z0-9_]+)')  # for mention
    hgrex = re.compile(r'(?<=^|(?<=[^a-zA-Z0-9]))#([A-Za-z0-9_]+)')  # for hashtags
    ugrex = re.compile(r'(https?://[^\s]+)')  # for url

    users = io.get_values_one_field(dbname, comname, 'id_str', filter)
    userlist = list()
    for user in users:
        documents = list()
        for tweet in time.find({'user.id': int(user)}):
            text = tweet['text'].encode('utf8')
            # replace RT, @, # and Http://
            text = rtgrex.sub('', text)
            text = mgrex.sub('', text)
            text = hgrex.sub('', text)
            text = ugrex.sub('', text)
            text = text.strip()
            if not(text.endswith('.') or text.endswith('?') or text.endswith('!')):
                text += '.'
            words = text.split()
            if len(words) > 5:
                documents.append(' '.join(words))
        if len(documents) > 0:
            with open(outpath+'/'+user+'.data', 'w') as fo:
                for document in documents:
                    fo.write(document+'\n')
            userlist.append(user)
    with open(outpath+'.doclist', 'w') as fo:
        for user in userlist:
            fo.write('database/'+outpath+'/'+ user+'.data\n')

if __name__ == '__main__':
    data_4_opinionfinder('random', 'scom', 'timeline', 'random')
    data_4_opinionfinder('fed', 'scom', 'timeline', 'ed')
    data_4_opinionfinder('young', 'scom', 'timeline', 'young')
