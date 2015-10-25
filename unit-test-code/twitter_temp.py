# -*- coding: utf-8 -*-
"""
Created on Fri Mar 06 11:05:34 2015

@author: home
"""
#%%
from twython import Twython
twitter = Twython()
#%%
APP_KEY = 'YOUR_APP_KEY'
APP_SECRET = 'YOUR_APP_SECRET'

twitter = Twython(APP_KEY, APP_SECRET, oauth_version=2)
ACCESS_TOKEN = twitter.obtain_access_token()

APP_KEY = 'YOUR_APP_KEY'
ACCESS_TOKEN = 'YOUR_ACCESS_TOKEN'

twitter = Twython(APP_KEY, access_token=ACCESS_TOKEN)