# -*- coding: utf-8 -*-
"""
Created on 9:37 AM, 6/4/16

@author: tw
Uing klout API to evelaute users' influence
"""

from klout import *


def klout_score(k, screen_name):
    # Get kloutId of the user by inputting a twitter screenName
    kloutId = k.identity.klout(screenName=screen_name).get('id')

    # Get klout score of the user
    score = k.user.score(kloutId=kloutId).get('score')

    print "User's klout score is: %s" % (score)

    # By default all communication is not secure (HTTP). An optional secure parameter
    # can be sepcified for secure (HTTPS) communication
    # k = Klout('rvn6gu78y5kscj3cyrn57r6n', secure=True)

    # Optionally a timeout parameter (seconds) can also be sent with all calls
    # score = k.user.score(kloutId=kloutId, timeout=5).get('score')


if __name__ == '__main__':
    k = Klout('rvn6gu78y5kscj3cyrn57r6n')
    klout_score(k, 'bskinni87')
    klout_score(k, 'elizsabethmusic')
    klout_score(k, 'NotJustADiet')
