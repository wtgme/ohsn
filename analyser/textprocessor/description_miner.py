# -*- coding: utf-8 -*-
"""
Created on 14:03, 18/11/15
Analysis user's description
Get CW, GW, H, LW, HW etc from description

@author: wt
"""


from os import path
import sys
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
import util.db_util as dbutil
# import time
# import urllib
import re
import datetime
from operator import itemgetter
from collections import Counter


MIN_RESOLUTION = datetime.timedelta(seconds=86400)

KEYWORDS = ['anorexic',
                    'anorexia',
                    'anorexia-purging',
                    'hypergymnasia',
                    'diagnosed',
                    'relapse',
                    'relapsing',
                    'recovery',
                    'recovering',
                    'inpatient',
                    'ed',
                    'eating',
                    'eating-disorder',
                    'ednos',
                    'ed-nos',
                    'bulimic',
                    'bulimia',
                    'depressed',
                    'depression',
                    'depressive',
                    'anxiety',
                    'anxieties',
                    'ocd',
                    'suicidal',
                    'skinny',
                    'thin',
                    'fat',
                    'thighs',
                    'collarbones',
                    'hips',
                    'harm',
                    'self-harm',
                    'selfharm',
                    'cutter',
                    'cutting',
                    'hate',
                    'ana',
                    'proana',
                    'mia',
                    'promia',
                    'starving',
                    'diet',
                    'fasting',
                    'purging',
                    'purge',
                    'clean',
                    'insomnia']


VERSION = 0.01


def getVersion():
    return VERSION


def identify_manual_retweet(text):
    #r'\b(?:#|@|)[0-9]*%s[0-9]*\b'
    pattern = re.compile('\s*(RT|retweet|MT|via)\s*@', re.IGNORECASE)
    match = pattern.search(text)
    if match is None:
        return False
    else:
        return True

def identify_retweet(tweet):
# if its an official retweet ignore the tweet itself
    try:
        orig = tweet['interaction']['twitter']['retweeted_status']
        return True
    except Exception:
        # remember it may still be a manual retweet so look out for that in mineTweetText!!
        return identify_manual_retweet(tweet['interaction']['twitter']['text'])


def get_age(text):
    # This assumes they are between the age of 10 and 89
    pattern = re.compile("(?P<age>[1-8][0-9])\syear", re.IGNORECASE)
    match = pattern.search(text)
    if match is not None:
        #print match.group('age') +"\t"+ text
        return match.group('age')

    pattern = re.compile("(?P<age>[1-8][0-9])year", re.IGNORECASE)
    match = pattern.search(text)
    if match is not None:
        #print match.group('age') +"\t"+ text
        return match.group('age')

    pattern = re.compile("(?P<age>[1-8][0-9])\sy/o", re.IGNORECASE)
    match = pattern.search(text)
    if match is not None:
        #print match.group('age') +"\t"+ text
        return match.group('age')

    pattern = re.compile("(?P<age>[1-8][0-9])y/o", re.IGNORECASE)
    match = pattern.search(text)
    if match is not None:
        #print match.group('age') +"\t"+ text
        return match.group('age')

    pattern = re.compile("^(?P<age>[1-8][0-9])\s*[,\./\\\:;\s-]", re.IGNORECASE)
    match = pattern.search(text)
    if match is not None:
        #print match.group('age') +"\t"+ text
        return match.group('age')

    pattern = re.compile("(?P<age>[1-8][0-9])\s*yrs", re.IGNORECASE)
    match = pattern.search(text)
    if match is not None:
        #print match.group('age') +"\t"+ text
        return match.group('age')

    pattern = re.compile("age[:;=\s-]+(?P<age>[1-8][0-9])", re.IGNORECASE)
    match = pattern.search(text)
    if match is not None:
        #print match.group('age') +"\t"+ text
        return match.group('age')


# def get_gender(text):
#     TODO


def get_height(text):
    #Height Matching
    pattern = re.compile("(?P<feet>[4-6])\s*('|f(oo)?t)\s*(?P<inches>1[0-1]|[0-9])?\s*(\"|in(ches)?)?", re.IGNORECASE)
    #pattern = re.compile("(?P<feet>[4-6])'\s*(?P<inches>[1-9]|1[0-2])\"?", re.IGNORECASE)
    match = pattern.search(text)
    if match is not None:
        inches =  int(match.group('feet'))*12
        if match.group('inches') is not None:
             inches = inches + int(match.group('inches'))
        height = inches*2.54
        return height
       # print user_stats['username'].encode('utf-8') +":"+ user_stats['age'] +":"+ match.group('feet') +"'" + match.group('inches')+ "\"=" + str(user_stats['height']) #+'\n'
    else:
        pattern = re.compile("(?P<metres>[1-2])m\s*(?P<cmetres>[0-9][0-9]?)\s*(cm)?|(?P<ctmetres>[1-2][0-9][0-9])\s*(cm)", re.IGNORECASE)
        #pattern = re.compile("(?P<feet>[4-6])'\s*(?P<inches>1[01]|\d)\"?", re.IGNORECASE)
        match = pattern.search(text)
        if match is not None:
            if match.group('ctmetres') is not None:
                return float(match.group('ctmetres'))
            else:
                return float(int(match.group('metres'))*100 + int(match.group('cmetres')))
        else:
            pattern = re.compile("(?P<metres>\d\.\d*)\s*m[,\.:;=\s-]", re.IGNORECASE)
            match = pattern.search(text)
            if match is not None:
                return float(match.group('metres'))*100


def get_high_weightKG(text):
    pattern = re.compile("[(\[{]?(hw|high weight|high)[)\]}]?([.~:;=/|\s-]*|(\s(is|was)\s))(?P<mass>\d+\.?\d*)\s*(?P<units>kg|lb|pounds)*", re.IGNORECASE)
    match = pattern.search(text)
    if match is not None:
        mass = float(match.group('mass'))
        if match.group('units') is not None:
            #print match.group('mass') + match.group('units') #user_stats[
            if match.group('units') in ("lb","pounds"):
                weight_kg = mass * 0.453592
                unitsguessed = False
                        #bmi = weight_kg/(height_cm^2)
            else: # i.e. it matches kilos
                weight_kg = mass
                unitsguessed = False
        else:
            # search for units elsewhere in the description
            pattern = re.compile("(lb|lbs|kg|pounds)", re.IGNORECASE)
            match = pattern.search(text)
            if match is not None:
                 if match.group(0) in ("lb","lbs","pounds"):
                        weight_kg = mass * 0.453592
                        unitsguessed = True
                 else: # i.e. it matches kilos
                        weight_kg = mass
                        unitsguessed = True
                #print mass + match.group(0) + "(Unit Deduction)"
            #Lets assume that if the cw is greater than 70 then its in pounds.
            elif float(mass) < 70:
                weight_kg = mass
                unitsguessed = True
                # print mass + "kg" + "(Unit Probable)"
            else: # if in doubt guess lbs?
                weight_kg = mass * 0.453592
                unitsguessed = True
                #print mass + "lb" + "(Unit Guess)"
            # check location? i.e. USA = lbs, rest = kg

        return (weight_kg, unitsguessed)
    else:
        return (None, None)


def get_low_weight_KG(text):
    pattern = re.compile("[(\[{]?(lw|low weight|low)[)\]}]?([.~:;=/|\s-]*|(\s(is|was)\s))(?P<mass>\d+\.?\d*)\s*(?P<units>kg|lb|pounds)*", re.IGNORECASE)
    match = pattern.search(text)
    if match is not None:
        mass = float(match.group('mass'))
        if match.group('units') is not None:
            #print match.group('mass') + match.group('units') #user_stats[
            if match.group('units') in ("lb","pounds"):
                weight_kg = mass * 0.453592
                unitsguessed = False
                        #bmi = weight_kg/(height_cm^2)
            else: # i.e. it matches kilos
                weight_kg = mass
                unitsguessed = False
        else:
            # search for units elsewhere in the description
            pattern = re.compile("(lb|lbs|kg|pounds)", re.IGNORECASE)
            match = pattern.search(text)
            if match is not None:
                 if match.group(0) in ("lb","lbs","pounds"):
                        weight_kg = mass * 0.453592
                        unitsguessed = True
                 else: # i.e. it matches kilos
                        weight_kg = mass
                        unitsguessed = True
                #print mass + match.group(0) + "(Unit Deduction)"
            #Lets assume that if the cw is greater than 70 then its in pounds.
            elif float(mass) < 70:
                weight_kg = mass
                unitsguessed = True
                # print mass + "kg" + "(Unit Probable)"
            else: # if in doubt guess lbs?
                weight_kg = mass * 0.453592
                unitsguessed = True
                #print mass + "lb" + "(Unit Guess)"
            # check location? i.e. USA = lbs, rest = kg

        return (weight_kg, unitsguessed)
    else:
        return (None, None)


def get_current_weight_KG(text):
    pattern = re.compile("[(\[{]?(cw|current weight|current(ly)?)[)\]}]?([.~:;=/|\s-]*|(\s(is|was)\s))(?P<mass>\d+\.?\d*)\s*(?P<units>kg|lb|pounds)*", re.IGNORECASE)
    match = pattern.search(text)
    if match is not None:
        mass = float(match.group('mass'))
        if match.group('units') is not None:
            #print match.group('mass') + match.group('units') #user_stats[
            if match.group('units') in ("lb","pounds"):
                weight_kg = mass * 0.453592
                unitsguessed = False
                        #bmi = weight_kg/(height_cm^2)
            else: # i.e. it matches kilos
                weight_kg = mass
                unitsguessed = False
        else:
            # search for units elsewhere in the description
            pattern = re.compile("(lb|lbs|kg|pounds)", re.IGNORECASE)
            match = pattern.search(text)
            if match is not None:
                 if match.group(0) in ("lb","lbs","pounds"):
                     weight_kg = mass * 0.453592
                     unitsguessed = True
                 else: # i.e. it matches kilos
                     weight_kg = mass
                     unitsguessed = True
                #print mass + match.group(0) + "(Unit Deduction)"
            #Lets assume that if the cw is greater than 70 then its in pounds.
            elif float(mass) < 70:
                weight_kg = mass
                unitsguessed = True
                # print mass + "kg" + "(Unit Probable)"
            else: # if in doubt guess lbs?
                weight_kg = mass * 0.453592
                unitsguessed = True
                #print mass + "lb" + "(Unit Guess)"
            # check location? i.e. USA = lbs, rest = kg

        return (weight_kg, unitsguessed)
    else:
        return (None, None)



def get_goal_weight(text):
    pattern = re.compile("[(\[{]?(gw|goal weight|goal)\(?\w?\)?[)\]}]?([.~:;=/|\s-]*|(\s(is|was)\s))(?P<mass>\d+\.?\d*)\s*(?P<units>kg|lb|pounds)*", re.IGNORECASE)
    match = pattern.search(text)
    if match is not None:
        mass = float(match.group('mass'))
        if match.group('units') is not None:
            # print match.group('mass') + match.group('units') #user_stats[
            if match.group('units') in ("lb","pounds"):
                weight_kg = mass * 0.453592
                unitsguessed = False
                        #bmi = weight_kg/(height_cm^2)
            else: # i.e. it matches kilos
                weight_kg = mass
                unitsguessed = False
        else:
            # search for units elsewhere in the description
            pattern = re.compile("(lb|lbs|kg|pounds)", re.IGNORECASE)
            match = pattern.search(text)
            if match is not None:
                 if match.group(0) in ("lb","lbs","pounds"):
                     weight_kg = mass * 0.453592
                     unitsguessed = True
                 else: # i.e. it matches kilos
                     weight_kg = mass
                     unitsguessed = True
                #print mass + match.group(0) + "(Unit Deduction)"
            #Lets assume that if the cw is greater than 70 then its in pounds.
            elif float(mass) < 70:
                weight_kg = mass
                unitsguessed = True
                # print mass + "kg" + "(Unit Probable)"
            else: # if in doubt guess lbs?
                weight_kg = mass * 0.453592
                unitsguessed = True
                #print mass + "lb" + "(Unit Guess)"
            # check location? i.e. USA = lbs, rest = kg

        return (weight_kg, unitsguessed)
    else:
        return (None, None)


def get_ultimate_goal_weight(text):
    pattern = re.compile("ugw\w?[:;=\s-]+(?P<mass>\d+\.?\d*)\s*(?P<units>kg|lb|pounds)*", re.IGNORECASE)
    match = pattern.search(text)
    if match is not None:
        mass = float(match.group('mass'))
        if match.group('units') is not None:
            #print match.group('mass') + match.group('units') #user_stats[
            if match.group('units') in ("lb","pounds"):
                weight_kg = mass * 0.453592
                unitsguessed = False
                        #bmi = weight_kg/(height_cm^2)
            else: # i.e. it matches kilos
                weight_kg = mass
                unitsguessed = False
        else:
            # search for units elsewhere in the description
            pattern = re.compile("(lb|lbs|kg|pounds)", re.IGNORECASE)
            match = pattern.search(text)
            if match is not None:
                 if match.group(0) in ("lb","lbs","pounds"):
                     weight_kg = mass * 0.453592
                     unitsguessed = True
                 else: # i.e. it matches kilos
                     weight_kg = mass
                     unitsguessed = True
                #print mass + match.group(0) + "(Unit Deduction)"
            #Lets assume that if the cw is greater than 70 then its in pounds.
            elif float(mass) < 70:
                weight_kg = mass
                unitsguessed = True
                # print mass + "kg" + "(Unit Probable)"
            else: # if in doubt guess lbs?
                weight_kg = mass * 0.453592
                unitsguessed = True
                #print mass + "lb" + "(Unit Guess)"
            # check location? i.e. USA = lbs, rest = kg

        return (weight_kg, unitsguessed)
    else:
        return (None, None)


def process_description(poi):
    # poi.update({}, {'$set': {"text_anal.mined": False}}, multi=True)
    while True:
        count = poi.count({"text_anal.mined": {'$exists': False}})
        # count({'$or':[{'protected': False, 'text_anal.mined': {'$exists': False}, 'level': {'$lte': level}},
        #                                      {'protected': False, 'text_anal.mined': {'$lt': scrapt_times}, 'level': {'$lte': level}}]})

        if count == 0:
            break
        else:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") +"\t"+ str(count) + " remaining"
        for user in poi.find({"text_anal.mined": {'$exists': False}}).limit(500):
            try:
                text = user['description']
                text = text.encode('utf-8').replace('\n', '')
                text = text.lower()
                source = 'description'

                cnt = Counter()
                words = re.findall('\w+', text.lower())
                for word in words:
                    if word in KEYWORDS:
                        cnt[word] += 1
                edword_count = sum(cnt.values())
                poi.update({"id": user['id']}, {'$set':{'text_anal.edword_count.datetime':datetime.datetime.now() ,'text_anal.edword_count.source':source, 'text_anal.edword_count.value':int(edword_count)}})

                # ugw, ugw_ug = get_ultimate_goal_weight(text)
                # if ugw is not None:
                #     poi.update({"id": user['id']}, {'$set':{'text_anal.ugw.datetime':datetime.datetime.now(),'text_anal.ugw.source':source, 'text_anal.ugw.ug':gw_ug, 'text_anal.ugw.value':gw}})

                gw, gw_ug = get_goal_weight(text)
                if gw is not None:
                    poi.update({"id": user['id']}, {'$set':{'text_anal.gw.datetime':datetime.datetime.now(),'text_anal.gw.source':source, 'text_anal.gw.ug':gw_ug, 'text_anal.gw.value':float(gw)}})

                cw, cw_ug = get_current_weight_KG(text)
                if cw is not None:
                    poi.update({"id": user['id']}, {'$set':{'text_anal.cw.datetime':datetime.datetime.now(),'text_anal.cw.source':source, 'text_anal.cw.ug':cw_ug, 'text_anal.cw.value':float(cw)}})

                hw, hw_ug = get_high_weightKG(text)
                if hw is not None:
                    poi.update({ "id": user['id']}, {'$set':{'text_anal.hw.datetime':datetime.datetime.now(),'text_anal.hw.source':source, 'text_anal.hw.ug':hw_ug, 'text_anal.hw.value':float(hw)}})

                lw, lw_ug = get_low_weight_KG(text)
                if lw is not None:
                    poi.update({ "id": user['id']}, {'$set':{'text_anal.lw.datetime':datetime.datetime.now(),'text_anal.lw.source':source, 'text_anal.lw.ug':lw_ug, 'text_anal.lw.value':float(lw)}})

                h = get_height(text)
                if h is not None:
                    poi.update({ "id": user['id']}, {'$set':{'text_anal.h.datetime':datetime.datetime.now(),'text_anal.h.source':source, 'text_anal.h.value':float(h)}})

                a = get_age(text)
                if a is not None:
                    poi.update({ "id": user['id']}, {'$set':{'text_anal.a.datetime':datetime.datetime.now(),'text_anal.a.source':source, 'text_anal.a.value':int(a)}})
            except Exception as detail:
                print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), str(detail), 'miss user description'

            poi.update({ "id": user['id']}, {'$set':{'text_anal.mined':True}})

db = dbutil.db_connect_no_auth('fed')
sample_poi = db['poi']
process_description(sample_poi)

# text =  '''I was diagnosed anorexic when I was 14 and I.am now 20. my hw was 195 lw was 105 and my cw is 140. my gw is 93 and my goal is to be that by christmas!
# '''.lower()
# print get_low_weight_KG(text)

# ,