# -*- coding: utf-8 -*-
"""
Created on 2:30 PM, 10/26/16

@author: tw

This script split ED users' timeline in every 500 tweets.
For each bunch, perform LIWC analysis to see the changes of LIWC feature over time
"""

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))


from ohsn.util import db_util as dbt
import ohsn.lexiconsmaster.liwc_timeline_processor as liwcp
from datetime import datetime
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from ohsn.util import plot_util as pltt


def bunch_user_tweets_panel(dbname, comname, timename, n=100):
    '''
    :param dbname: db name
    :param comname: user collection name
    :param timename: timeline collection name
    :param n: split tweets every n
    :return: pandas panel
    '''
    db = dbt.db_connect_no_auth(dbname)
    com = db[comname]
    times = db[timename]

    data = {}

    for user in com.find({'timeline_count': {'$gt': 500}}, ['id', 'id_str', 'created_at']):
        uid = user['id']

        liwc_results = []
        indices = []
        user_create_time = []
        first_tweet_time = []
        last_tweet_time = []
        fields = []

        count = 0
        index = 0
        tweets = []

        for tweet in times.find({'user.id': uid}).sort([("id", 1)]):
            if count < n:
                tweets.append(tweet)
                count += 1
            else:
                result = liwcp.process_tweet(tweets, Trim_rt=False)
                if result:
                    liwc_results.append([result[k] for k in result.keys()])
                    if len(fields) == 0:
                        fields = [k for k in result.keys()]
                    indices.append(index)
                    user_create_time.append(datetime.strptime(user['created_at'], '%a %b %d %H:%M:%S +0000 %Y'))
                    first_tweet_time.append(datetime.strptime(tweets[0]['created_at'], '%a %b %d %H:%M:%S +0000 %Y'))
                    last_tweet_time.append(datetime.strptime(tweets[-1]['created_at'], '%a %b %d %H:%M:%S +0000 %Y'))
                    # print index, count
                index += 1
                count = 0
                tweets = []
        liwc_results = np.array(liwc_results)
        size = len(user_create_time)
        user_create_time = np.reshape(user_create_time, (size, 1))
        first_tweet_time = np.reshape(first_tweet_time, (size, 1))
        last_tweet_time = np.reshape(last_tweet_time, (size, 1))
        liwc_results = np.append(liwc_results, user_create_time, axis=1)
        liwc_results = np.append(liwc_results, first_tweet_time, axis=1)
        liwc_results = np.append(liwc_results, last_tweet_time, axis=1)
        print liwc_results.shape


        df = pd.DataFrame(data=liwc_results,
                          columns=fields + ['user_created_time', 'first_tweet_time', 'last_tweet_time'],
                          index=indices)
        data[user['id_str']] = df
    pn = pd.Panel(data)
    pn.to_pickle('ed-liwc.panel')


def bunch_user_tweets_dataframe(dbname, comname, timename, filename, num_batch=2, n=-1):
    '''
    :param dbname: db name
    :param comname: user collection name
    :param timename: timeline collection name
    :param n: split tweets every n
    :return: pandas dataframe
    '''
    db = dbt.db_connect_no_auth(dbname)
    com = db[comname]
    times = db[timename]

    liwc_results = []
    indices = []
    user_dis = []
    user_create_time = []
    first_tweet_time = []
    last_tweet_time = []
    counts = []
    fields = []
    split_k = False
    if n == -1:
        split_k = True

    for user in com.find({'timeline_count': {'$gt': 0}}, ['id', 'id_str', 'created_at', 'timeline_count'], no_cursor_timeout=True):
        uid = user['id']
        tweet_count = user['timeline_count']
        if split_k == True:
            n = (tweet_count-1)/num_batch
            print '---------------------------------------------'
            print '%d tweets batched in every %d' %(tweet_count, n)

        count = 0
        index = 0
        tweets = []

        for tweet in times.find({'user.id': uid}).sort([("id", 1)]):
            if count < n:
                tweets.append(tweet)
                count += 1
            else:
                result = liwcp.process_tweet(tweets, Trim_rt=True)
                if result:
                    liwc_results.append([result[k] for k in result.keys()])
                    if len(fields) == 0:
                        fields = [k for k in result.keys()]
                    user_dis.append(user['id_str'])
                    indices.append(index)
                    counts.append(n)
                    user_create_time.append(datetime.strptime(user['created_at'], '%a %b %d %H:%M:%S +0000 %Y'))
                    first_tweet_time.append(datetime.strptime(tweets[0]['created_at'], '%a %b %d %H:%M:%S +0000 %Y'))
                    last_tweet_time.append(datetime.strptime(tweets[-1]['created_at'], '%a %b %d %H:%M:%S +0000 %Y'))
                    print 'User %s, in time %d with %d tweets ---- verify %d tweets' %(user['id_str'], index, count, len(tweets))
                index += 1
                tweets = [tweet]
                count = 1

    liwc_results = np.array(liwc_results)
    size = len(user_create_time)
    counts = np.reshape(counts, (size, 1))
    user_create_time = np.reshape(user_create_time, (size, 1))
    first_tweet_time = np.reshape(first_tweet_time, (size, 1))
    last_tweet_time = np.reshape(last_tweet_time, (size, 1))

    user_dis = np.reshape(user_dis, (size, 1))
    indices = np.reshape(indices, (size, 1))

    user_dis = np.append(user_dis, indices, axis=1)
    user_dis = np.append(user_dis, user_create_time, axis=1)
    user_dis = np.append(user_dis, first_tweet_time, axis=1)
    user_dis = np.append(user_dis, last_tweet_time, axis=1)
    user_dis = np.append(user_dis, counts, axis=1)
    liwc_results = np.append(user_dis, liwc_results, axis=1)
    print 'user matrix', liwc_results.shape


    df = pd.DataFrame(data=liwc_results,
                      columns=['user_id', 'time_index', 'user_created_time', 'first_tweet_time', 'last_tweet_time', 'count'] + fields)
    df.to_csv(filename)
    df.to_pickle(filename+'.pick')


def compare_periods(filename, prefix):
    # parser = lambda date: pd.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    # df = pd.read_csv(filename, parse_dates=['user_created_time', 'first_tweet_time', 'last_tweet_time'], date_parser=parser, index_col=[0])
    df = pd.read_pickle(filename+'.pick')
    # print df.describe()
    users = set(df['user_id'])
    print 'number of users: %d' %len(users)
    print 'All features:'
    names = list(df.columns.values)
    print names
    noi = ['posemo', 'negemo', 'health', 'body', 'ingest', 'death']
    # recover = set([u'946529629', u'1682256595', u'1209898242', u'1250864694', u'2600203795', u'1849655365', u'2956069936', u'880912610', u'1590161850', u'2484784148', u'2525172540', u'521655711', u'2252626398', u'741449148', u'2627692395', u'1458224383', u'1054225837', u'2365997659', u'2327948041', u'2747144492', u'867352153', u'536752131', u'2269511532', u'894435654', u'1167549211', u'846477558', u'870618870', u'1078223436', u'1551911419', u'2824684680', u'4818062473', u'899052614', u'623101932', u'2358940014', u'2357260466', u'891608479', u'622140829', u'1268301654', u'178030167', u'1055888702', u'939440118', u'1220107045', u'3082368646', u'1539188581', u'568455627', u'2746904423', u'3396249681', u'1419350881', u'1705683883', u'2844615608', u'1596203167', u'1319345712', u'780824682', u'734717672', u'1284716263', u'799412802', u'1353540547', u'1876143192', u'3173952120', u'925391660', u'3311796872', u'3260610991', u'3073404545', u'1567191541', u'2223419558', u'910747506', u'1273328341', u'286722806', u'1317062646', u'792872552', u'1489055828', u'2258210623', u'816538232', u'1482675907', u'1229839622', u'1443048278', u'1240523563', u'1674059323', u'2255985468', u'1463477515', u'1300098991', u'360698200', u'932996862', u'1367465329', u'2240053074', u'982964593', u'1619392266', u'2800734048', u'2306743449', u'1626162828', u'1407697442', u'1904180432', u'719277854', u'1614628700', u'2221590855', u'2506154331', u'2151402855', u'2225893177', u'436420640', u'1918910587', u'2747064597', u'1666187750', u'538509802', u'1109557784', u'2713821854', u'777200318', u'1284851154', u'273203971', u'1675281260', u'258440340', u'377619516', u'701678826', u'990053641', u'621888786', u'904365414', u'1058088361', u'635889252', u'164480604', u'487728741', u'1872463484', u'3137701603', u'1494402829', u'781608757', u'220130271', u'725002621', u'599620600', u'1265412168', u'783742651', u'605038884', u'2543905130', u'1049258474', u'1347840504', u'2223704572', u'1134725642', u'869214949', u'304458528', u'908823343', u'899386196', u'527952865', u'888376346', u'1581591648', u'2567802096', u'1463659819', u'614174044', u'1252412918', u'215174706', u'1076293386', u'1442393875', u'2288553834', u'1167069050', u'745468003', u'717697231', u'45273301', u'2419593438', u'996552967', u'602433517', u'413364530', u'1230090788', u'569266852', u'809956010', u'2204726011', u'413561706', u'320967613', u'1005786006', u'1047844286', u'503503094', u'1257657252', u'609171099', u'1483847354', u'1216984920', u'1153308649', u'621484126', u'162011268', u'1088021534', u'1276255952', u'1539094772', u'381794593', u'1420982640', u'1423333874', u'543750643', u'618338817', u'292256172', u'1316502037', u'199752409', u'457136874', u'1186389506', u'1549237184', u'1120647768', u'411794527', u'1418985170', u'1262967985', u'2886089921', u'1525816806', u'852164156', u'1720942249', u'1187274426', u'1635081919', u'2844303053', u'1693966087', u'739655448', u'3379953496', u'833937307', u'2840611944', u'967248524', u'1921762350', u'2534293513', u'2492219417', u'565223880', u'928154102', u'1093878319', u'519692975', u'2657362720', u'630629210', u'2276475811', u'557442390', u'390350321', u'1445144167', u'2572789899', u'1350874850', u'2852489594', u'492964360', u'2891295326', u'1126132572', u'722173116', u'385141868', u'3093482777', u'1283108131', u'482340295', u'2244652602', u'1429540550', u'847529941', u'1107595075', u'1242788161', u'1668723068', u'559067952', u'1242026917', u'1729131446', u'593237064', u'1029313632', u'846211285', u'707163436', u'2451953051', u'928462478', u'3340269245', u'1030833176', u'1656199405', u'530839880', u'2323126634', u'1068718476', u'854652230', u'3165477317', u'1023204037', u'358928191', u'886193125', u'1115264185', u'1411792002', u'4614995115', u'764541175', u'4767809181', u'540401600', u'457519100', u'332770861', u'2273960540', u'548884928', u'817254450', u'1496790434', u'2362224704', u'737889739', u'1220844366', u'2806743010', u'1120611552', u'2647563619', u'1285514569', u'1914026989', u'2375449677', u'1416609986', u'1424235312', u'713504342', u'2172964410', u'1722276122', u'809827358', u'1049261317', u'1470817399', u'579373511', u'593688348', u'2878516074', u'1700498090', u'1463030096', u'1276019382', u'750382572', u'579278907', u'2758869202', u'350604277', u'598829382', u'469090885', u'2808908655', u'3020433891', u'2850499568', u'2234796254', u'1586534125', u'261996598', u'791079109', u'1388295048', u'1385256074', u'1236433207', u'1198185026', u'898649935', u'1945261902'])
    # recovery_users = (set(users).intersection(recover))
    for name in noi[:2]:
        changes = []
        # recovery_changes = []
        # non_recovery_changes = []
        negatives = []
        positives = []
        active_time = []
        for user in users:
            uvs = df[(df.user_id == user)].loc[:, ['time_index', name,
                                                   'user_created_time',
                                                   'last_tweet_time',
                                                   'first_tweet_time',
                                                   'count']]
            # print uvs
            if len(uvs) == 2:
                # print user
                old = uvs.iloc[0][name]
                new = uvs.iloc[1][name]
                # print period
                if old != 0:
                    change = (new - old)
                    period0 = (uvs.iloc[0]['last_tweet_time'] - uvs.iloc[0]['first_tweet_time']).days+1
                    period1 = (uvs.iloc[1]['last_tweet_time'] - uvs.iloc[1]['first_tweet_time']).days+1
                    activity0 = float(uvs.iloc[0]['count'])/(period0)
                    activity1 = float(uvs.iloc[1]['count'])/(period1)
                    # print change
                    if change > 0:
                        positives.append(user)
                    elif change < 0:
                        negatives.append(user)
                    changes.append(change)
                    # if user in recover:
                    #     recovery_changes.append(change)
                    # else:
                    #     non_recovery_changes.append(change)
                    active_time.append(activity1-activity0)
        print '----------------------'+name+'---------------'
        print 'All users changes: ', len(changes)
        print 'Mean of changes: %.3f' %np.mean(changes)
        # print 'Recovery users changes: ', len(recovery_changes)
        # print 'Non-Recovery users changes: ',len(non_recovery_changes)

        # print 'Value-Increased Recovery users:'
        # print len(set(positives).intersection(recover))
        # # print positives[:10]
        # print 'Value-Decreased Recovery susers:'
        # print len(set(negatives).intersection(recover))
        # # print negatives[:10]

        # sns.distplot(changes, label='All user '+str(len(changes)), hist=False)
        # sns.distplot(recovery_changes, label='Recovery user '+str(len(recovery_changes)), hist=False)
        # sns.distplot(non_recovery_changes, label='Non-Recovery user '+str(len(non_recovery_changes)), hist=False)
        # plt.xlabel(r'$\Delta$('+name+')')
        # plt.ylabel(r'p($\Delta$)')
        # plt.legend()
        # plt.savefig(name+'change-recovery.pdf')
        # plt.clf()

        pltt.correlation(changes, active_time, r'$\Delta$('+name+')', r'$\Delta$(Activity)', prefix+name+'activity-change.pdf')




if __name__ == '__main__':
    filename = 'rd-liwc2stage.csv'
    bunch_user_tweets_dataframe('random', 'scom', 'timeline', filename)
    filename = 'yg-liwc2stage.csv'
    bunch_user_tweets_dataframe('younger', 'scom', 'timeline', filename)

    # compare_periods('ed-liwc2stage.csv', 'ed')



