# -*- coding: utf-8 -*-
"""
Created on 15:51, 19/11/15
CSV cannot recognize dic{{}}, this module is discarded, using mongochef to export
@author: wt
"""

import db_util as dbutil
import csv
import io_util as iot


def csv_output(data, fields, file_name):
    with open(file_name+'.csv', 'wb') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(fields)
        for x in data:
            # print x
            values = []
            for field in fields:
                # print field
                if '.' in field:
                    levels = field.split('.')
                    t = x.get(levels[0], {})
                    for level in levels[1:]:
                        # print t
                        t = t.get(level)
                        if t is None:
                            break
                    values.append(t)
                else:
                    values.append(x.get(field))
            proce_values = []
            for s in values:
                s = unicode(s).encode("utf-8").replace('\t', ' ').replace(';', ' ').replace(',', ' ').replace('\n', ' ').replace('\r', ' ').replace('\r\n', ' ').replace('\n\r', ' ')
                if s == 'None':
                    s = ''
                proce_values.append(s)
            writer.writerow(proce_values)


def export_poi(dbname, colname, index=0):
    db = dbutil.db_connect_no_auth(dbname)
    poidb = db[colname]
    data = []
    for x in poidb.find({'timeline_count': {'$gt': 0}}):
        if index != 0:
            x['time_index'] = index
        data.append(x)
    return data


def export_net_agg(dbname, colname, file_name):
    db = dbutil.db_connect_no_auth(dbname)
    net = db[colname]
    fields = ['id0', 'id1', 'type', 'count']
    ttypes = {1: 'retweet', 2: 'reply', 3: 'mention'}

    '''Only include poi users'''
    data = []
    tems = {}
    for re in net.find({"type": {'$in': [1, 2, 3]}}):
        id0 = re['id0']
        id1 = re['id1']
        typeid = re['type']
        if id0 != id1:
            count = tems.get((id0, id1, typeid), 0)
            tems[(id0, id1, typeid)] = count+1

    for id0, id1, typeid in tems.keys():
        data.append({'id0': id0, 'id1': id1, 'type': ttypes[typeid], 'count': tems[(id0, id1, typeid)]})
    csv_output(fields, file_name, data)


if __name__ == '__main__':
    fields = iot.read_fields()
    d = export_poi('fed', 'scom')
    csv_output(d, fields, 'poi')
    d1 = export_poi('fed', 'com_t1', 1)
    d2 = export_poi('fed', 'com_t2', 2)
    d3 = export_poi('fed', 'com_t3', 3)
    d4 = export_poi('fed', 'com_t4', 4)
    d5 = export_poi('fed', 'com_t5', 5)
    d = d1 + d2 + d3 + d4 + d5
    csv_output(d, fields, 'poi_ts')

    # export_net_agg('fed', 'com_t1', 'sbnet_t1', 'bnet_t1')
    # export_net_agg('fed', 'com_t2', 'sbnet_t2', 'bnet_t2')
    # export_net_agg('fed', 'com_t3', 'sbnet_t3', 'bnet_t3')
    # export_net_agg('fed', 'com_t4', 'sbnet_t4', 'bnet_t4')
    # export_net_agg('fed', 'com_t5', 'sbnet_t5', 'bnet_t5')
