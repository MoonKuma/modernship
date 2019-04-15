#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : __init__.py.py
# @Author: mjf
# @Date  : 
# @Desc  :
# | techid | mvip | mtech | count(uid) | sum(mtech)/count(uid) |
# +--------+------+-------+------------+-----------------------+
# |   1010 |    0 |     1 |       2872 |                1.0000 |

# | techid | mvip | count(uid) | sum(mtech)/count(uid) |
# +--------+------+------------+-----------------------+
# |   1010 |    0 |       3121 |                1.0804 |

import util.EasyMysql as EasyMysql
from is_valid_data import is_legal_input

# argv assignment
vip_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
vip_trans = map(lambda x:'VIP'+str(x),vip_list)
# tech_list = []
times_list=[]
# times_list = ['UserCount']+[1010,1020,1030,1040,1050,1060,1070,1080,1090,1100,2011,2012,2013,2021,2022,2023,2031,2032,2033,2041,2042,2043,2051,2052,2053,2061,2062,2063,2064,2071,2072,2073,2074,2081,2082,2083,2084,2091,2092,2093,2094,2095,2101,2102,2103,2104,2105]
for i in range(47):
    times_list.append(i)
times_list = ['UserCount']+times_list
times_trans = ['人数',1010,1020,1030,1040,1050,1060,1070,1080,1090,1100]+['高速突防技术','隐身突防技术','低空突防技术','超高频雷达技术','双波段雷达技术','合成孔径雷达技术','一体化核动力技术','电力推进技术','燃料电池技术','智能数据链技术','综合通信桅杆技术','蓝绿激光通信技术','超高速跳频技术','全频谱对抗技术','有源主动对消技术','超地平线防空技术','舰队指挥中枢技术','激光防御系统技术','战区空天防御技术','复合声纳系统技术','复合制导鱼雷技术','低频降噪技术','泵喷推进技术','舰队中枢技术','隐形舰载机技术','先进起降技术','综合电力技术','联合指挥中心技术','极高频通讯卫星技术','全球卫星定位技术','海洋监视卫星技术','海底声纳阵列技术','预警飞艇技术','空天飞机技术','亚轨道飞行器技术','超长时无人机技术','天基飞船技术']





X_first_trans = ['翻译']
X_first = ['trans']
Y_list = times_list
Y_listtrans = times_trans
default_value = ''
Y_trans = dict(zip(Y_list, Y_listtrans))


def tech_people(input_dict):
    global X_list
    global X_trans
    X_list = []
    data_dict = dict()
    for y in Y_list:
        data_dict[y] = dict()
    head_name = "科技人数"

    easy_mysql = EasyMysql.EasyMysql()
    is_legal_input(input_dict)
    date_list = [max(input_dict['date_list'])]
    date_list = sorted(date_list)
    if len(date_list) == 0:
        msg = 'Not date selected, len(date_list)' + str(len(date_list))
        raise RuntimeError(msg)
    zoneid_list = input_dict['zone_list']
    channel_list = input_dict['channel_list']
    cursor = input_dict['cursor']
    sql_where = ' where date =' + easy_mysql.sql_value_str(date_list)
    if len(zoneid_list) > 0:
        sql_where = sql_where + ' and zoneid in (' + easy_mysql.sql_value_str(zoneid_list) + ') '
    if len(channel_list) > 0:
        sql_where = sql_where + ' and channel in (' + easy_mysql.sql_value_str(channel_list) + ') '
    sql_str = 'select mvip,count(uid) from(select uid,max(level) as mlevel,max(vip_level) as mvip from user_active '+sql_where+'  group by uid) as a group by mvip;'
    cursor.execute(sql_str)
    all_data = cursor.fetchall()
    if all_data:
        for rec in all_data:
            vip = int(rec[0])
            user = int(rec[1])
            data_dict['UserCount'][vip] = user

            X_list.append(vip)
        X_list = sorted(list(set(X_list)))

        X_listtrans = ['翻译'] + map(lambda x: 'VIP' + str(x), X_list)
        X_list = X_first + X_list
        X_trans = dict(zip(X_list, X_listtrans))

    # sql_str = 'select techid,mvip,mtech,count(uid),sum(mtech)/count(uid) from (select uid,techid,max(viplevel) as mvip,max(techlevel) as mtech from TechInfo'+sql_where+' group by uid,techid) as a group by techid,mvip,mtech;'
    # sql_str = 'select techid,mvip,count(uid),sum(mtech)/count(uid) from (select uid,techid,max(viplevel) as mvip,max(techlevel) as mtech from TechInfo '+sql_where+' group by uid,techid) as a group by techid,mvip;'
    sql_str = 'select techid,viplevel,sum(peoplenum),sum(techlevel*peoplenum)/sum(peoplenum) from TechInfoNew '+sql_where+'  and techlevel>0 group by techid,viplevel;'

    cursor.execute(sql_str)
    all_data = cursor.fetchall()
    if all_data:
        for rec in all_data:
            data_dict[int(rec[0])][rec[1]] = rec[2]
    for key in data_dict.keys():
        if X_first[0] not in data_dict.keys():
            data_dict[key]['trans'] = Y_trans[key]
    res_dict={'data_dict':data_dict,'X_list':X_list,'Y_list':Y_list,'head_name':head_name,'X_trans':X_trans,'default_value':default_value}
    # print(res_dict)
    res_dict["note"] = "统计最后日的各VIP段的激活科技的人数*"
    return res_dict

def tech_avglevel(input_dict):
    data_dict = dict()
    for y in Y_list:
        data_dict[y] = dict()
    head_name = "科技人均等级"

    easy_mysql = EasyMysql.EasyMysql()
    is_legal_input(input_dict)
    date_list = [max(input_dict['date_list'])]
    date_list = sorted(date_list)
    if len(date_list) == 0:
        msg = 'Not date selected, len(date_list)' + str(len(date_list))
        raise RuntimeError(msg)
    zoneid_list = input_dict['zone_list']
    channel_list = input_dict['channel_list']
    cursor = input_dict['cursor']
    sql_where = ' where date =' + easy_mysql.sql_value_str(date_list)
    if len(zoneid_list) > 0:
        sql_where = sql_where + ' and zoneid in (' + easy_mysql.sql_value_str(zoneid_list) + ') '
    if len(channel_list) > 0:
        sql_where = sql_where + ' and channel in (' + easy_mysql.sql_value_str(channel_list) + ') '
    sql_str = 'select mvip,count(uid) from(select uid,max(level) as mlevel,max(vip_level) as mvip from user_active '+sql_where+'  group by uid) as a group by mvip;'
    cursor.execute(sql_str)
    all_data = cursor.fetchall()
    if all_data:
        for rec in all_data:
            vip = int(rec[0])
            user = int(rec[1])
            data_dict['UserCount'][vip] = user

    # sql_str = 'select techid,mvip,mtech,count(uid),sum(mtech)/count(uid) from (select uid,techid,max(viplevel) as mvip,max(techlevel) as mtech from TechInfo'+sql_where+' group by uid,techid) as a group by techid,mvip,mtech;'
    # sql_str = 'select techid,mvip,count(uid),sum(mtech)/count(uid) from (select uid,techid,max(viplevel) as mvip,max(techlevel) as mtech from TechInfo '+sql_where+' group by uid,techid) as a group by techid,mvip;'
    sql_str = 'select techid,viplevel,sum(peoplenum),sum(techlevel*peoplenum)/sum(peoplenum) from TechInfoNew '+sql_where+'  and techlevel>0 group by techid,viplevel;'

    cursor.execute(sql_str)
    all_data = cursor.fetchall()
    if all_data:
        for rec in all_data:
            data_dict[rec[0]][rec[1]] = rec[3]
    for key in data_dict.keys():
        if X_first[0] not in data_dict.keys():
            data_dict[key]['trans'] = Y_trans[key]
    res_dict={'data_dict':data_dict,'X_list':X_list,'Y_list':Y_list,'head_name':head_name,'X_trans':X_trans,'default_value':default_value}
    # print(res_dict)
    res_dict["note"] = "统计最后日的各VIP段的激活科技的人的平均等级*"
    return res_dict