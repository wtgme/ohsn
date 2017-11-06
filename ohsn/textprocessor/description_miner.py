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

from ohsn.util import db_util as dbutil
from ohsn.util import io_util as iot
import re
import datetime
from collections import Counter
from deepdiff import DeepDiff
import pymongo
import pickle
import numpy as np

MIN_RESOLUTION = datetime.timedelta(seconds=86400)
# KEYWORDS = set(['eating disorder', 'eatingdisorder', 'anorexia', 'bulimia', 'anorexic',
#                 'ana', 'bulimic', 'anorexia nervosa', 'mia', 'thinspo',
#                 'bulemia', 'purge', 'bulimia nervosa', 'binge',  'selfharm', 'ed-nos',
#                 'ednos', 'edprobs', 'edprob', 'proana', 'anamia', 'promia',
#                 'askanamia', 'bonespo', 'legspo'])

KEYWORDS = set(['anorexic',
            'anorexia',
            'anorexia-purging',
            # 'hypergymnasia',
            # 'diagnosed',
            # 'relapse',
            # 'relapsing',
            # 'recovery',
            # 'recovering',
            # 'inpatient',
            # 'ed',
            # 'eating',
            'eating-disorder',
            'ednos',
            'ed-nos',
            'bulimic',
            'bulimia',
            # 'depressed',
            # 'depression',
            # 'depressive',
            # 'anxiety',
            # 'anxieties',
            # 'ocd',
            # 'suicidal',
            # 'skinny',
            # 'thin',
            # 'fat',
            # 'thighs',
            # 'collarbones',
            # 'hips',
            # 'harm',
            # 'self-harm',
            # 'selfharm',
            # 'cutter',
            # 'cutting',
            # 'hate',
            'ana',
            'proana',
            'mia',
            'promia',
            # 'starving',
            # 'diet',
            # 'fasting',
            'purging',
            'purge',
            # 'clean',
            # 'insomnia',
            'eat', 'eating disorder', 'eatingdisorder', 'anorexia', 'bulimia', 'anorexic',
                'ana', 'bulimic', 'anorexia nervosa', 'mia', 'thinspo',
                'bulemia', 'purge', 'bulimia nervosa', 'binge',  'selfharm',
                'ednos', 'edprobs', 'edprob', 'proana', 'anamia', 'promia',
                'askanamia', 'bonespo', 'legspo'])

VERSION = 0.01



girl_names = iot.read_name(type='F')
boy_names = iot.read_name(type='M')

def getVersion():
    return VERSION


def identify_manual_retweet(text):
    # r'\b(?:#|@|)[0-9]*%s[0-9]*\b'
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
    # print text
    # This assumes they are between the age of 10 and 89
    pattern = re.compile("(?P<age>[1-8][0-9])\s*year", re.IGNORECASE)
    match = pattern.search(text)
    if match is not None:
        # print 'a'
        # print match.group('age') +"\t"+ text
        return match.group('age')

    pattern = re.compile("(?P<age>[1-8][0-9])\s*y/o", re.IGNORECASE)
    match = pattern.search(text)
    if match is not None:
        # print 'b'
        # print match.group('age') +"\t"+ text
        return match.group('age')

    pattern = re.compile("^(?P<age>[1-8][0-9])\s*([^\w'\"\.]|(\.\D)|(f|m))[^kdl]", re.IGNORECASE)
    match = pattern.search(text)
    if match is not None:
        # print 'c'
        # print match.group('age') +"\t"+ text
        return match.group('age')

    pattern = re.compile("(?P<age>[1-8][0-9])\s*yrs", re.IGNORECASE)
    match = pattern.search(text)
    if match is not None:
        # print 'd'
        # print match.group('age') +"\t"+ text
        return match.group('age')

    pattern = re.compile("(?P<age>[1-8][0-9])\s*yo?", re.IGNORECASE)
    match = pattern.search(text)
    if match is not None:
        # print 'e'
        # print match.group('age') +"\t"+ text
        return match.group('age')

    pattern = re.compile("age[:;=\s-]+(?P<age>[1-8][0-9])[^a-z]", re.IGNORECASE)
    match = pattern.search(text)
    if match is not None:
        # print 'f'
        # print match.group('age') +"\t"+ text
        return match.group('age')

    pattern = re.compile("\sa[:;=\s-]+(?P<age>[1-8][0-9])[^a-z]", re.IGNORECASE)
    match = pattern.search(text)
    if match is not None:
        # print 'h'
        # print match.group('age') +"\t"+ text
        return match.group('age')

    pattern = re.compile("[;|,•=-]\s*(?P<age>[1-8][0-9])\s*([;=|,•-])", re.IGNORECASE)
    match = pattern.search(text)
    if match is not None:
        # print 'i'
        # print match.group('age') +"\t"+ text
        return match.group('age')
    return None

def get_gender(text, name=''):
    # from name
    name_pat = re.compile('^(?P<first>[A-Z][a-z]+) (?P<second>[A-Z][a-z]+)$')
    name_match = name_pat.search(name.strip())
        # age_match = age_pat.search(prof.strip())
    if name_match:
        if (name_match.group('first').lower() in girl_names):
            return 'F'
        elif (name_match.group('first').lower() in boy_names):
            return 'M'
    else:
        # from profile description
        pattern = re.compile("female|girl|woman|princess", re.IGNORECASE)
        match = pattern.search(text)
        if match is not None:
            # print 'a'
            # print match.group('age') +"\t"+ text
            return 'F'
        pattern = re.compile("male|boy|man|prince", re.IGNORECASE)
        match = pattern.search(text)
        if match is not None:
            # print 'b'
            # print match.group('age') +"\t"+ text
            return 'M'
        pattern = re.compile("(I(')?m|i( a)?m) (?P<name>[A-Z][a-z]+)", re.IGNORECASE)
        match = pattern.search(text)
        if match is not None:
            s = (match.group('name')).lower()
            if s in girl_names:
                return 'F'
            elif s in boy_names:
                return 'M'
        return None


def get_bmi(text):
    # print text
    # pattern = re.compile("BMI[:-]*\s*(?P<bmi>[0-9][0-9][.,]?[0-9]*)", re.IGNORECASE)
    pattern = re.compile("BMI\W*(?P<bmi>[0-9][0-9][.,]?[0-9]*)", re.IGNORECASE)
    match = pattern.search(text)
    if match is not None:
        s = (match.group('bmi'))
        s = s.replace(',', '.')
        return s


def get_height(text):
    # Height Matching
    pattern = re.compile("(?P<feet>[4-6])\s*(‘|'|f(oo)?t)\s*(?P<inches>1[0-1]|[0-9])?\s*(('')|“|\"|in(ches)?)?",
                         re.IGNORECASE)
    # pattern = re.compile("(?P<feet>[4-6])'\s*(?P<inches>[1-9]|1[0-2])\"?", re.IGNORECASE)
    match = pattern.search(text)
    if match is not None:
        inches = int(match.group('feet')) * 12
        if match.group('inches') is not None:
            inches = inches + int(match.group('inches'))
        height = inches * 2.54
        return height
        # print user_stats['username'].encode('utf-8') +":"+ user_stats['age'] +":"+ match.group('feet') +"'" + match.group('inches')+ "\"=" + str(user_stats['height']) #+'\n'
    else:
        pattern = re.compile(
            "(?P<metres>[1-2])(‘|'|m)\s*(?P<cmetres>[0-9][0-9]?)\s*(cm)?|(?P<ctmetres>[1-2][0-9][0-9])\s*(cm)",
            re.IGNORECASE)
        # pattern = re.compile("(?P<feet>[4-6])'\s*(?P<inches>1[01]|\d)\"?", re.IGNORECASE)
        match = pattern.search(text)
        if match is not None:
            if match.group('ctmetres') is not None:
                return float(match.group('ctmetres'))
            else:
                return float(int(match.group('metres')) * 100 + int(match.group('cmetres')))
        else:
            pattern = re.compile("(?P<metres>\d\.\d*)\s*m[,\.:;=\s-]", re.IGNORECASE)
            match = pattern.search(text)
            if match is not None:
                return float(match.group('metres')) * 100


def get_high_weightKG(text):
    pattern = re.compile(
        "[(\[{]?(hw|high weight| high|sw)(\s?[/|]\s?sw)?[)\]}]?([\.~×:;=/|\s-]*|(\s(is|was)\s))(?P<mass>\d+\.?\d*)\s*(?P<units>stone|kg|lb|pounds)*",
        re.IGNORECASE)
    match = pattern.search(text)
    if match is not None:
        mass = float(match.group('mass'))
        if match.group('units') is not None:
            # print match.group('mass') + match.group('units') #user_stats[
            if match.group('units') in ("lb", "pounds"):
                weight_kg = mass * 0.453592
                unitsguessed = False
                # bmi = weight_kg/(height_cm^2)
            elif match.group('units') in ('stone'):
                weight_kg = mass * 6.35029
                unitsguessed = False
            else:  # i.e. it matches kilos
                weight_kg = mass
                unitsguessed = False
        else:
            # search for units elsewhere in the description
            pattern = re.compile("(stone |lb|lbs|kg|pounds)", re.IGNORECASE)
            match = pattern.search(text)
            if match is not None:
                if match.group(0) in ("lb", "lbs", "pounds"):
                    weight_kg = mass * 0.453592
                    unitsguessed = True
                elif match.group(0) in ('stone '):
                    weight_kg = mass * 6.35029
                    unitsguessed = True
                else:  # i.e. it matches kilos
                    weight_kg = mass
                    unitsguessed = True
                    # print mass + match.group(0) + "(Unit Deduction)"
            # Lets assume that if the cw is greater than 70 then its in pounds.
            elif float(mass) < 70:
                weight_kg = mass
                unitsguessed = True
                # print mass + "kg" + "(Unit Probable)"
            elif float(mass) < 12:
                weight_kg = mass * 6.35029
                unitsguessed = True
            else:  # if in doubt guess lbs?
                weight_kg = mass * 0.453592
                unitsguessed = True
                # print mass + "lb" + "(Unit Guess)"
                # check location? i.e. USA = lbs, rest = kg

        return (weight_kg, unitsguessed)
    else:
        return (None, None)


def get_low_weight_KG(text):
    pattern = re.compile(
        "[(\[{]?(lw|low weight| low)[)\]}]?([\.~:×;=/|\s-]*|(\s(is|was)\s))(?P<mass>\d+\.?\d*)\s*(?P<units>stone|kg|lb|pounds)*",
        re.IGNORECASE)
    match = pattern.search(text)
    if match is not None:
        mass = float(match.group('mass'))
        if match.group('units') is not None:
            # print match.group('mass') + match.group('units') #user_stats[
            if match.group('units') in ("lb", "pounds"):
                weight_kg = mass * 0.453592
                unitsguessed = False
                # bmi = weight_kg/(height_cm^2)
            elif match.group('units') in ('stone'):
                weight_kg = mass * 6.35029
                unitsguessed = False
            else:  # i.e. it matches kilos
                weight_kg = mass
                unitsguessed = False
        else:
            # search for units elsewhere in the description
            pattern = re.compile("(stone |lb|lbs|kg|pounds)", re.IGNORECASE)
            match = pattern.search(text)
            if match is not None:
                if match.group(0) in ("lb", "lbs", "pounds"):
                    weight_kg = mass * 0.453592
                    unitsguessed = True
                elif match.group(0) in ('stone '):
                    weight_kg = mass * 6.35029
                    unitsguessed = True
                else:  # i.e. it matches kilos
                    weight_kg = mass
                    unitsguessed = True
                    # print mass + match.group(0) + "(Unit Deduction)"
            # Lets assume that if the cw is greater than 70 then its in pounds.
            elif float(mass) < 70:
                weight_kg = mass
                unitsguessed = True
                # print mass + "kg" + "(Unit Probable)"
            elif float(mass) < 12:
                weight_kg = mass * 6.35029
                unitsguessed = True
            else:  # if in doubt guess lbs?
                weight_kg = mass * 0.453592
                unitsguessed = True
                # print mass + "lb" + "(Unit Guess)"
                # check location? i.e. USA = lbs, rest = kg

        return (weight_kg, unitsguessed)
    else:
        return (None, None)


def get_current_weight_KG(text):
    pattern = re.compile(
        "[(\[{]?(cw|current weight|current(ly)?)\(?\w?\)?[)\]}]?([\.~×:;=/|\s-]*|(\s(is|was)\s))(?P<mass>\d+\.?\d*)\s*(?P<units>stone|kg|lb|pounds)*",
        re.IGNORECASE)
    match = pattern.search(text)
    if match is not None:
        mass = float(match.group('mass'))
        if match.group('units') is not None:
            # print match.group('mass') + match.group('units') #user_stats[
            if match.group('units') in ("lb", "pounds"):
                weight_kg = mass * 0.453592
                unitsguessed = False
                # bmi = weight_kg/(height_cm^2)
            elif match.group('units') in ('stone'):
                weight_kg = mass * 6.35029
                unitsguessed = False
            else:  # i.e. it matches kilos
                weight_kg = mass
                unitsguessed = False
        else:
            # search for units elsewhere in the description
            pattern = re.compile("(stone |lb|lbs|kg|pounds)", re.IGNORECASE)
            match = pattern.search(text)
            if match is not None:
                if match.group(0) in ("lb", "lbs", "pounds"):
                    weight_kg = mass * 0.453592
                    unitsguessed = True
                elif match.group(0) in ('stone '):
                    weight_kg = mass * 6.35029
                    unitsguessed = True
                else:  # i.e. it matches kilos
                    weight_kg = mass
                    unitsguessed = True
                    # print mass + match.group(0) + "(Unit Deduction)"
            # Lets assume that if the cw is greater than 70 then its in pounds.
            elif float(mass) < 70:
                weight_kg = mass
                unitsguessed = True
                # print mass + "kg" + "(Unit Probable)"
            elif float(mass) < 12:
                weight_kg = mass * 6.35029
                unitsguessed = True
            else:  # if in doubt guess lbs?
                weight_kg = mass * 0.453592
                unitsguessed = True
                # print mass + "lb" + "(Unit Guess)"
                # check location? i.e. USA = lbs, rest = kg

        return (weight_kg, unitsguessed)
    else:
        return (None, None)


def get_goal_weight(text):
    pattern = re.compile(
        "[(\[{]?(gw|goal weight|goal)\(?\w?\)?[)\]}]?([\.~:×;=/|\s-]*|(\s(is|was)\s))(?P<mass>\d+\.?\d*)\s*(?P<units>kg|lb|pounds)*",
        re.IGNORECASE)
    match = pattern.search(text)
    if match is not None:
        mass = float(match.group('mass'))
        if match.group('units') is not None:
            # print match.group('mass') + match.group('units') #user_stats[
            if match.group('units') in ("lb", "pounds"):
                weight_kg = mass * 0.453592
                unitsguessed = False
                # bmi = weight_kg/(height_cm^2)
            elif match.group('units') in ('stone'):
                weight_kg = mass * 6.35029
                unitsguessed = False
            else:  # i.e. it matches kilos
                weight_kg = mass
                unitsguessed = False
        else:
            # search for units elsewhere in the description
            pattern = re.compile("(stone |lb|lbs|kg|pounds)", re.IGNORECASE)
            match = pattern.search(text)
            if match is not None:
                if match.group(0) in ("lb", "lbs", "pounds"):
                    weight_kg = mass * 0.453592
                    unitsguessed = True
                elif match.group(0) in ('stone '):
                    weight_kg = mass * 6.35029
                    unitsguessed = True
                else:  # i.e. it matches kilos
                    weight_kg = mass
                    unitsguessed = True
                    # print mass + match.group(0) + "(Unit Deduction)"
            # Lets assume that if the cw is greater than 70 then its in pounds.
            elif float(mass) < 70:
                weight_kg = mass
                unitsguessed = True
                # print mass + "kg" + "(Unit Probable)"
            elif float(mass) < 12:
                weight_kg = mass * 6.35029
                unitsguessed = True
            else:  # if in doubt guess lbs?
                weight_kg = mass * 0.453592
                unitsguessed = True
                # print mass + "lb" + "(Unit Guess)"
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
            # print match.group('mass') + match.group('units') #user_stats[
            if match.group('units') in ("lb", "pounds"):
                weight_kg = mass * 0.453592
                unitsguessed = False
                # bmi = weight_kg/(height_cm^2)
            else:  # i.e. it matches kilos
                weight_kg = mass
                unitsguessed = False
        else:
            # search for units elsewhere in the description
            pattern = re.compile("(lb|lbs|kg|pounds)", re.IGNORECASE)
            match = pattern.search(text)
            if match is not None:
                if match.group(0) in ("lb", "lbs", "pounds"):
                    weight_kg = mass * 0.453592
                    unitsguessed = True
                else:  # i.e. it matches kilos
                    weight_kg = mass
                    unitsguessed = True
                    # print mass + match.group(0) + "(Unit Deduction)"
            # Lets assume that if the cw is greater than 70 then its in pounds.
            elif float(mass) < 70:
                weight_kg = mass
                unitsguessed = True
                # print mass + "kg" + "(Unit Probable)"
            else:  # if in doubt guess lbs?
                weight_kg = mass * 0.453592
                unitsguessed = True
                # print mass + "lb" + "(Unit Guess)"
                # check location? i.e. USA = lbs, rest = kg

        return (weight_kg, unitsguessed)
    else:
        return (None, None)


def edword(text):
    cnt = Counter()
    words = re.findall('\w+', text)
    for word in words:
        if word in KEYWORDS:
            cnt[word] += 1
    return int(sum(cnt.values()))


def process_text(text, name=''):
    # extract demongraphic features from user profile and user name
    results = {}
    text = text.encode('utf-8').replace('\n', ' ')
    text = text.lower()

    edword_count = edword(text)
    if edword_count is not 0:
        results['edword_count'] = {'value': edword_count}

    gw, gw_ug = get_goal_weight(text)
    if gw is not None:
        results['gw'] = {'ug': gw_ug, 'value': float(gw)}

    cw, cw_ug = get_current_weight_KG(text)
    if cw is not None:
        results['cw'] = {'ug': cw_ug, 'value': float(cw)}

    hw, hw_ug = get_high_weightKG(text)
    if hw is not None:
        results['hw'] = {'ug': hw_ug, 'value': float(hw)}

    bmi = get_bmi(text)
    if bmi is not None:
        results['bmi'] = {'value': float(bmi)}

    lw, lw_ug = get_low_weight_KG(text)
    if lw is not None:
        results['lw'] = {'ug': lw_ug, 'value': float(lw)}

    h = get_height(text)
    if h is not None:
        results['h'] = {'value': float(h)}
        h = h/100
        if 'gw' in results:
            gw = results['gw']['value']
            results['gbmi'] = {'value': gw / (h * h)}
            # print results['gw']['value'], results['h']['value'], results['gbmi']['value']
        if 'cw' in results:
            cw = results['cw']['value']
            results['cbmi'] = {'value': cw / (h * h)}

    a = get_age(text)
    if a is not None:
        results['a'] = {'value': float(a)}

    gender = get_gender(text, name)
    if gender is not None:
        results['gender'] = {'value': gender}

    return results


def process_timelines(user_id, timeline, bio):
    while True:
        count = timeline.count({'user.id': user_id, 'bio_mined': {'$exists': False}})
        if count == 0:
            break
        else:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "\t" + str(count) + " remaining"

        last_bio_rec = {}
        try:
            last_bio = bio.find({'uid': user_id}).sort([('tid', -1)]).limit(1)[
                0]  # sort: 1 = ascending, -1 = descending
            if last_bio:
                last_bio_rec = last_bio['results']
        except IndexError as detail:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "\t" + \
                  'Get latest stored bio ERROR, a new user ' + str(detail)
            pass
        flag = False
        for tweet in timeline.find({'user.id': user_id, 'bio_mined': {'$exists': False}},
                                   {'id': 1, 'user': 1, 'created_at': 1}).sort([('id', 1)]):
            user = tweet['user']
            text = user['description']
            if text is None:
                results = {}
            else:
                results = process_text(text)
            if results and DeepDiff(results, last_bio_rec):
                flag = True
                last_bio_rec = results
                bio.insert({"uid": user_id, 'tid': tweet['id'], 'screen_name': user['screen_name'],
                            'created_at': tweet['created_at'], 'results': results})
            timeline.update({"id": tweet['id']}, {'$set': {'bio_mined': True}}, upsert=False)
        print str(user_id) + ' has bio information ' + str(flag)


def process_description(poi):
    # poi.update({}, {'$set': {"text_anal.mined": False}}, multi=True)
    while True:
        count = poi.count({"text_anal.mined": {'$exists': False}})
        # count({'$or':[{'protected': False, 'text_anal.mined': {'$exists': False}, 'level': {'$lte': level}},
        #                                      {'protected': False, 'text_anal.mined': {'$lt': scrapt_times}, 'level': {'$lte': level}}]})
        if count == 0:
            break
        else:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "\t" + str(count) + " remaining"
        for user in poi.find({"text_anal.mined": {'$exists': False}}).limit(500):
            text = user['description']
            if text is None:
                results = {}
            else:
                results = process_text(text, user['name'])
            results['mined'] = True
            poi.update({"id": user['id']}, {'$set': {'text_anal': results}}, upsert=False)


def inference_stat(dbname, colname):
    db = dbutil.db_connect_no_auth(dbname)
    com = db[colname]
    for user in com.find({'text_anal.h': {'$exists': True}}, ['id', 'text_anal']):
        values = user['text_anal']
        h = values['h']['value'] / 100
        if 'gw' in values:
            gw = values['gw']['value']
            values['gbmi'] = {'value': gw / (h * h)}
        if 'cw' in values:
            cw = values['cw']['value']
            values['cbmi'] = {'value': cw / (h * h)}
        com.update({"id": user['id']}, {'$set': {'text_anal': values}}, upsert=False)


def process_poi(dbname, colname):
    print 'Processing', dbname, colname
    db = dbutil.db_connect_no_auth(dbname)
    sample_poi = db[colname]
    process_description(sample_poi)
    # inference_stat(dbname, colname)


def process_test_results():
    db = dbutil.db_connect_no_auth('fed')
    # poi = db['com']
    timeline = db['timeline']
    bio = db['bio']
    bio.create_index([('uid', pymongo.ASCENDING),
                      ('tid', pymongo.ASCENDING)],
                     unique=True)
    test_ids = np.array(pickle.load(open('test_ids.data', 'r')))
    test_class = pickle.load(open('test_class.pick', 'r'))
    test_class[test_class < 0] = 0
    test_class = test_class.astype(bool)
    targest_ids = test_ids[test_class]
    # print targest_ids.shape
    for user_id in targest_ids:
        process_timelines(int(user_id), timeline, bio)
        # user = poi.find_one({'id': user_id}, ['id', 'screen_name'])
        # print user['screen_name']


if __name__ == '__main__':
    process_poi('fed3', 'com')
    # inference_stat('fed', 'com')
    # process_poi('sed', 'com')
    # process_poi('srd', 'com')
    # process_poi('syg', 'com')
    # inference_stat('fed', 'com_t1')
    # inference_stat('fed', 'com_t2')
    # inference_stat('fed', 'com_t3')
    # inference_stat('fed', 'com_t4')
    # inference_stat('fed', 'com_t5')




   #  text = '''hi, i'm Katie. i'm here if you wanna talk♥ Self Harmer,. 18.132lbs. 5ft3.  Bisexual. Anorexic. Alone. Self harm. Depressed. A big F*CK you to everyone who made me like this'''

   # # Leeshly. 15. Ana with Mia tendencies. Bipolar. Self- harmer. CW: 88 HW:13O LW: 88 GW: 85 UGW: 7O (then lower)'''.lower()
   # #  print get_high_weightKG(text)

   #  # 17. uk. 5'4. 114lbs. (bmi: 18.9) bulimic. anorexic. anxiety. paranoia. anemic.  Hands Like Houses
   #  # 15, anorexia, CW:106lbs UGW: 90lbs
   #  # 17. Anorexic. Bulimic. Bipolar. Insomniac.
   #  # 23, 5'4 EDNOS. starve, purge, dying. don't care.
   #  # Mi lucha hasta llegar a cincuenta. He bajado de 75kg a 60 actualmente. No soy pro ana o pro mía. Soy pro-dieta estricta
   #  # hi, i'm Katie. i'm here if you wanna talk♥ Self Harmer, Depressed, Anorexia. SW:10 stone CW:8stone GW:7 and a half stone.
   #  # LW: 40.6 GW: because of my age 45kg Ana/mia for 10 wonderfully turmultuous years. Ana never let's go!!!!
   #  # female. 18.132lbs. 5ft3.  Bisexual. Anorexic. Alone. Self harm. Depressed. A big F*CK you to everyone who made me like this
   #  # I am a vegan relapser with a bmi of 20.I need to loose 12lbs to be 18.4 -My goal for may I'm not pro ana but my posts are triggering. Anon

   #  # Anon / Self harmer / Depressed / EDNOS / Anxiety / Suicidal / Music / here to talk / cw: 102/46 / gw: 100/45 / ugw: 90/40.5
   #  # Esclava de una mente trastornada, morí hacia ya varios aÑos atrás..meta: 40- 37kg bulimia/ anorexia alterna de @princesskatsura estudiante de medicina
   #  print get_gender(text)