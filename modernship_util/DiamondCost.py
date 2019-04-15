#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : __init__.py.py
# @Author: mjf
# @Date  : 2018/10/26
# @Desc  :
# #sqlstr
# select moneytype,mvip,count(distinct(a.uid)),count(a.uid),sum(cash),sum(totalcost) from
# (select uid,moneytype,sum(cash) as cash,sum(diamond) as diamond,sum(cash+diamond) as totalcost from diamond_detail where  date between "2018-10-22" and "2018-10-24" and keyword="CostDiamond" group by uid,moneytype) as a
# inner join
# (select uid,max(vip_level) as mvip from user_active where date between "2018-10-22" and "2018-10-24" group by uid) as b
# on a.uid=b.uid group by moneytype,mvip;
# | moneytype | mvip | count(distinct(a.uid)) | count(a.uid) | sum(cash) | sum(totalcost) |
# +-----------+------+------------------------+--------------+-----------+----------------+
# | 0 | 7 | 1 | 1 | 6500 | 13060 |
# | 1 | 0 | 8 | 8 | 0 | 4000 |



import util.EasyMysql as EasyMysql
from is_valid_data import is_legal_input

#initial argv



Costlist = ['UserCount',0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99]
Costtrans = ['人数','','改名字','改头像','使用道具','挑战副本','普通副本扫荡','副本重置','挑战精英副本','精英副本扫荡','精英副本重置','竞技场购买挑战次数','竞技场历史最高排名奖励','抽奖消耗','船建造','船升级','船升品','船升星','舰船模块升品','舰船技能升级','货币不足与购买','购买宝箱','商店购买','商店刷新','聊天扣费','科技升级','大洋任务','活动','科技抽奖消耗','竞技场挑战','旗舰大招升级','军团','舰船训练','vip礼包购买','热点抽奖','每日折扣','八日嘉年华','角色升级','冠军争夺刷新对手','世界BOSS','装备升级','领体力','军团BOSS','钻石成长','装备抽奖','传奇战舰18航母抽奖','购买金币','购买原油','买技能点','购买技能书','海军庆典','海上夺宝','多线补报名','升到7星后系统改造','强化改造','终极改造','海军节-每日折扣','海军节勋章回收','15船抽奖','军团GVE','军团GVG','跨服赛商店购买','导弹黑市刷新消耗','特权卡','招财猫消耗','精英本侦查','安装船员','卸下船员','批量解雇船员','船员升星','红包','船员还原','船员抽卡','指挥部角色等级重置','冠军争夺购买挑战次数','支援中心','远洋任务加速','创建军团','军团改名','军团改徽章','军团捐献','军团发红包','跨服聊天','任务中的兑换商店','RTGVG侦查','RTGVG集结','RTGVG轰炸','RTGVG鼓舞','RTGVG决战','装备还原','装备兑换','装备合成','装备替换','装备卸载','装备升星','装备拆解','军衔抽奖','购买晋升礼包','清空声望','礼包推送','支援中心激活','传奇战舰16航母抽奖','芯片兑换消耗','芯片抽奖消耗','芯片升级消耗技能书','芯片进化消耗固定物品']

# argv assignment

X_first = ['trans']
Y_list = Costlist
Y_listtrans = Costtrans
default_value = ''
Y_trans = dict(zip(Y_list, Y_listtrans))

##imput_dict={'date_list':[];'channel_list':[];zone_list:[];cursor:""}
def get_diamond_times(input_dict):
    global X_list
    global X_trans
    X_list = []
    data_dict = dict()
    for y in Y_list:
        data_dict[y] = dict()
    head_name = "钻石消耗次数"

    easy_mysql = EasyMysql.EasyMysql()
    is_legal_input(input_dict)
    date_list = input_dict['date_list']
    date_list = sorted(date_list)
    if len(date_list) == 0:
        msg = 'Not date selected, len(date_list)' + str(len(date_list))
        raise RuntimeError(msg)
    zoneid_list = input_dict['zone_list']
    channel_list = input_dict['channel_list']
    cursor = input_dict['cursor']
    sql_where = ' where date in (' + easy_mysql.sql_value_str(date_list) + ') '
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
            data_dict['UserCount'][vip]=user
            X_list.append(vip)
        X_list = sorted(list(set(X_list)))


    X_listtrans =['翻译'] + map(lambda x: 'VIP' + str(x), X_list)
    X_list = X_first + X_list
    X_trans = dict(zip(X_list, X_listtrans))

    sqlstr='select moneytype,mvip,count(distinct(a.uid)),count(a.uid),sum(cash),sum(totalcost) from (select uid,moneytype,sum(cash) as cash,sum(diamond) as diamond,sum(cash+diamond) as totalcost from diamond_detail'+sql_where+' and keyword="CostDiamond" group by uid,moneytype) as a inner join (select uid,max(vip_level) as mvip from user_active'+sql_where+' group by uid) as b on a.uid=b.uid group by moneytype,mvip; '
    cursor.execute(sqlstr)
    alldata = cursor.fetchall()
    if alldata:
        for rec in alldata:
            if int(rec[0]) not in data_dict.keys():
                data_dict[int(rec[0])] = dict()
            data_dict[int(rec[0])][rec[1]] = rec[3]
    for key in data_dict.keys():
        if X_first[0] not in data_dict.keys():
            data_dict[key]['trans'] = Y_trans.setdefault(key,key)
    res_dict={'data_dict':data_dict,'X_list':X_list,'Y_list':Y_list,'head_name':head_name,'X_trans':X_trans,'default_value':default_value}
    # print(res_dict)
    res_dict['note'] = "*起始日期-终止日期的各VIP段的钻石消耗次数*"
    return res_dict



def get_diamond_cost(input_dict):
    data_dict = dict()
    for y in Y_list:
        data_dict[y] = dict()
    head_name = "消耗钻石数"

    easy_mysql = EasyMysql.EasyMysql()
    is_legal_input(input_dict)
    date_list = input_dict['date_list']
    date_list = sorted(date_list)
    if len(date_list) == 0:
        msg = 'Not date selected, len(date_list)' + str(len(date_list))
        raise RuntimeError(msg)
    zoneid_list = input_dict['zone_list']
    channel_list = input_dict['channel_list']
    cursor = input_dict['cursor']
    sql_where = ' where date in (' + easy_mysql.sql_value_str(date_list) + ') '
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
            data_dict['UserCount'][vip]=user

    sqlstr = 'select moneytype,mvip,count(distinct(a.uid)),count(a.uid),sum(cash),sum(totalcost) from (select uid,moneytype,sum(cash) as cash,sum(diamond) as diamond,sum(cash+diamond) as totalcost from diamond_detail' + sql_where + ' and keyword="CostDiamond" group by uid,moneytype) as a inner join (select uid,max(vip_level) as mvip from user_active' + sql_where + ' group by uid) as b on a.uid=b.uid group by moneytype,mvip; '
    cursor.execute(sqlstr)
    alldata = cursor.fetchall()
    if alldata:
        for rec in alldata:
            if int(rec[0]) not in data_dict.keys():
                data_dict[int(rec[0])] = dict()
            data_dict[int(rec[0])][rec[1]] = rec[5]
    for key in data_dict.keys():
        if X_first[0] not in data_dict.keys():
            data_dict[key]['trans'] = Y_trans.setdefault(key,key)

    res_dict={'data_dict':data_dict,'X_list':X_list,'Y_list':Y_list,'head_name':head_name,'X_trans':X_trans,'default_value':default_value}
    res_dict["note"] = "*起始日期-终止日期的各VIP段的钻石消耗数量*"
    # print(res_dict)
    return res_dict

def get_diamond_people(input_dict):
    data_dict = dict()
    for y in Y_list:
        data_dict[y] = dict()
    head_name = "消耗钻石人数"

    easy_mysql = EasyMysql.EasyMysql()
    is_legal_input(input_dict)
    date_list = input_dict['date_list']
    date_list = sorted(date_list)
    if len(date_list) == 0:
        msg = 'Not date selected, len(date_list)' + str(len(date_list))
        raise RuntimeError(msg)
    zoneid_list = input_dict['zone_list']
    channel_list = input_dict['channel_list']
    cursor = input_dict['cursor']
    sql_where = ' where date in (' + easy_mysql.sql_value_str(date_list) + ') '
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
            data_dict['UserCount'][vip]=user

    sqlstr = 'select moneytype,mvip,count(distinct(a.uid)),count(a.uid),sum(cash),sum(totalcost) from (select uid,moneytype,sum(cash) as cash,sum(diamond) as diamond,sum(cash+diamond) as totalcost from diamond_detail' + sql_where + ' and keyword="CostDiamond" group by uid,moneytype) as a inner join (select uid,max(vip_level) as mvip from user_active' + sql_where + ' group by uid) as b on a.uid=b.uid group by moneytype,mvip; '
    cursor.execute(sqlstr)
    alldata = cursor.fetchall()
    if alldata:
        for rec in alldata:
            if int(rec[0]) not in data_dict.keys():
                data_dict[int(rec[0])] = dict()
            data_dict[int(rec[0])][rec[1]] = rec[2]

    for key in data_dict.keys():
        if X_first[0] not in data_dict.keys():
            data_dict[key]['trans'] = Y_trans.setdefault(key,key)


    res_dict={'data_dict':data_dict,'X_list':X_list,'Y_list':Y_list,'head_name':head_name,'X_trans':X_trans,'default_value':default_value}
    res_dict["note"] = "*起始日期-终止日期的各VIP段的钻石消耗人数*"
    # print(res_dict)
    return res_dict
