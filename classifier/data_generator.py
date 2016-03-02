# -*- coding: utf-8 -*-
"""
Created on 8:15 PM, 2/27/16

@author: tw
Export data from mongodb for classification and feature analysis
"""
import sys
sys.path.append('..')
import util.db_util as dbt
import util.io_util as io


def liwc_feature_output(fields, file_name, dbname, label):
    with open(file_name+'.data', 'a') as fw:
        db = dbt.db_connect_no_auth(dbname)
        poi = db['com']

        index = 0
        maxsize = 3300
        # exclude_set = set([4319191638L, 2627223434L, 2976822286L, 4788248335L, 3289264086L, 520847919, 439647015, 947539758, 617442479, 2481703728L, 2913311029L, 3760687289L, 2303011905L, 1712561862, 2882255303L, 261549132, 982895821, 2849269327L, 312684498, 160044558, 774072534, 330611545, 430569947, 1275228253, 3399616094L, 2924322143L, 457692129, 3006221026L, 2837359399L, 18942418, 2848241137L, 273768180, 235857269, 3315086840L])

        for x in poi.find({'liwc_anal.result.WC': {'$exists': True}},
                          ['id', 'liwc_anal.result']):
            if index < maxsize:
                values = io.get_fields_one_doc(x, fields)
                outstr = label + ' '
                for i in xrange(len(values)):
                    outstr += str(i+1)+':'+str(values[i])+' '
                index += 1
                fw.write(outstr+'\n')

LIWC = io.read_fields()

# common users in random and young = set([4319191638L, 2627223434L, 2976822286L, 4788248335L, 3289264086L, 520847919, 439647015, 947539758, 617442479, 2481703728L, 2913311029L, 3760687289L, 2303011905L, 1712561862, 2882255303L, 261549132, 982895821, 2849269327L, 312684498, 160044558, 774072534, 330611545, 430569947, 1275228253, 3399616094L, 2924322143L, 457692129, 3006221026L, 2837359399L, 18942418, 2848241137L, 273768180, 235857269, 3315086840L])
# fed, random, young
liwc_feature_output(LIWC, 'data/ed-all-liwc', 'yg', '-1')


