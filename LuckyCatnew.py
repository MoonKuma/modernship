#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : __init__.py.py
# @Author: mjf
# @Date  : 
# @Desc  :

import util.ReadTable as ReadTable
import util.EasyXls as EasyXls
import util.EasyMysql as EasyMysql
import util.DateList as DateList
from util.WriteStandardForm import write_standard_form
import conf.ConfParameters as ConfParameters
import MySQLdb
import xlwt
import collections
import os
from util.LogQuery import LogQuery
import datetime

class LuckyCat():
    def __init__(self):
        #bigdata
        mysqlStatInfo = {'host': '10.66.127.43', 'port': 3306, 'user': 'root', 'passwd': 'r00tr00t'}
        self.db = MySQLdb.connect(host=mysqlStatInfo['host'], port=mysqlStatInfo['port'], user=mysqlStatInfo['user'],
                                  passwd=mysqlStatInfo['passwd'], db='modernship_gf_stat_base', charset='utf8')
        self.cursor = self.db.cursor()
        self.easy_mysql = EasyMysql.EasyMysql()
        # # xls
        self.wbk = xlwt.Workbook()
        self.xls_writer = EasyXls.EasyXls()
        self.style = xlwt.XFStyle()
        self.style.borders = self.xls_writer.borders
    #老玩家
    def re_resultold(self,date_list,item_list,item_trans,headname):

        X_list = ["trans",0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,21,22,23,24,25]
        X_listtrans=['翻译']
        for i in X_list[1:]:
            X_listtrans.append('VIP'+ str(i))
        Y_list = ['activepeople','money','cash']+item_list
        Y_listtrans = ['活跃人数','金额','消耗rmb钻石']+item_trans
        X_trans = dict(zip(X_list, X_listtrans))
        Y_trans = dict(zip(Y_list, Y_listtrans))

        head_name = headname
        default_value = ''

        data_dict_oldvipgiftbuy = dict()
        data_dict_oldvipgiftbuyratio = dict()
        for i in Y_list:
            data_dict_oldvipgiftbuy[i] = dict()
            data_dict_oldvipgiftbuyratio[i] = dict()
        sql_where = ' where date in (' + self.easy_mysql.sql_value_str(date_list) + ') '
        #老用户活跃人数
        sql_str = 'select mvip,count(uid) from(select uid,max(vip_level) as mvip from user_active_extend '+sql_where+'and regdate<\"'+min(date_list)+'\" and uid not in (select uid from modernship_stat_busi.uid_block_list) group by uid)as a group by mvip;'
        print(sql_str)
        self.cursor.execute(sql_str)
        all_data = self.cursor.fetchall()
        if all_data:
            for rec in all_data:
                data_dict_oldvipgiftbuy['activepeople'][int(rec[0])] = rec[1]
                data_dict_oldvipgiftbuyratio['activepeople'][int(rec[0])] = rec[1]
        #老用户付费
        sql_str = 'select mvip,count(a.uid),sum(money) from (select uid,sum(money/100) as money from pay_syn_day '+sql_where+'  group by uid) as a inner join (select uid,max(vip_level) as mvip from user_active_extend '+sql_where+'and regdate<\"'+min(date_list)+'\" group by uid) as b on a.uid=b.uid group by mvip;'
        print(sql_str)
        self.cursor.execute(sql_str)
        all_data = self.cursor.fetchall()
        # | mvip | count(a.uid) | sum(money) |
        # +------+--------------+------------+
        # | 0 | 28 | 29.0000 |
        if all_data:
            for rec in all_data:
                data_dict_oldvipgiftbuy['money'][int(rec[0])] = rec[2]
                data_dict_oldvipgiftbuyratio['money'][int(rec[0])] = rec[2]
        #vipgift buy 老用户
        # sql_where_item = sql_where + 'and itemid in (' + self.easy_mysql.sql_value_str(item_list) + ') '
        sql_str = 'select mlevel,mvip,count(uid) from (select uid,max(vip_level) as mvip,max(cash+diamond) as mlevel from modernship_stat_busi.diamond_detail_needs '+sql_where+' and uid not in (select uid from modernship_stat_busi.uid_block_list) and uid in (select uid from user_active_extend where regdate<\"'+min(date_list)+'\") group by uid) as a group by mlevel,mvip;'
        print(sql_str)
        self.cursor.execute(sql_str)
        all_data = self.cursor.fetchall()
        if all_data:
            for rec in all_data:
                if(data_dict_oldvipgiftbuy.has_key(int(rec[0]))):
                    data_dict_oldvipgiftbuy[int(rec[0])][int(rec[1])] = float(rec[2])
                    data_dict_oldvipgiftbuyratio[int(rec[0])][int(rec[1])] = float(rec[2])/float(data_dict_oldvipgiftbuy['activepeople'][int(rec[1])])

        sql_str = 'select mvip,sum(cash) from (select uid,max(vip_level) as mvip,sum(cash) as cash from modernship_stat_busi.diamond_detail_needs '+sql_where+' and uid not in (select uid from modernship_stat_busi.uid_block_list) and uid in (select uid from user_active_extend where regdate<\"'+min(date_list)+'\") group by uid) as a group by mvip;'
        self.cursor.execute(sql_str)
        all_data = self.cursor.fetchall()
        if all_data:
            for rec in all_data:
                data_dict_oldvipgiftbuy['cash'][int(rec[0])] = float(rec[1])
                data_dict_oldvipgiftbuyratio['cash'][int(rec[0])] = float(rec[1])


        #加入翻译
        for k in data_dict_oldvipgiftbuy.keys():
            data_dict_oldvipgiftbuy[k]['trans']=Y_trans[k]
            data_dict_oldvipgiftbuyratio[k]['trans']=Y_trans[k]

        res_dict_oldpeople = {'data_dict': data_dict_oldvipgiftbuy, 'X_list': X_list, 'Y_list': Y_list, 'head_name': head_name+'人数', 'X_trans': X_trans, 'default_value': default_value}
        res_dict_oldpeople["note"] = "每期各VIP段招财最高档位的人数*"
        res_dict_oldpeopleratio= {'data_dict': data_dict_oldvipgiftbuyratio, 'X_list': X_list, 'Y_list': Y_list, 'head_name': head_name+'占比', 'X_trans': X_trans, 'default_value': default_value}
        res_dict_oldpeopleratio["note"] = "每期各VIP段招财最高档位的人数占比*"

        return [res_dict_oldpeople,res_dict_oldpeopleratio]

    #充值人次
    def re_resultoldrecharge(self,date_list,item_list,item_trans,headname):
        #viplist
        X_list = ["trans",0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,21,22,23,24,25]
        X_listtrans=['翻译']
        for i in X_list[1:]:
            X_listtrans.append('VIP'+ str(i))
        Y_list = ['activepeople','money']+item_list
        Y_listtrans = ['活跃人数','金额']+item_trans
        X_trans = dict(zip(X_list, X_listtrans))
        Y_trans = dict(zip(Y_list, Y_listtrans))

        head_name = headname
        default_value = ''

        data_dict_oldviprecharge = dict()
        data_dict_oldviprechargeratio = dict()
        data_dict_oldviprechargetimes = dict()
        dict_oldcoupon = dict()
        for i in Y_list:
            data_dict_oldviprecharge[i] = dict()
            data_dict_oldviprechargetimes[i] = dict()
            data_dict_oldviprechargeratio[i] = dict()
            dict_oldcoupon[i]=dict()

        sql_where = ' where date in (' + self.easy_mysql.sql_value_str(date_list) + ') '
        #老用户活跃人数
        sql_str = 'select mvip,count(uid) from(select uid,max(vip_level) as mvip from user_active_extend '+sql_where+'and regdate<\"'+min(date_list)+'\" and uid not in (select uid from modernship_stat_busi.uid_block_list) group by uid)as a group by mvip;'
        self.cursor.execute(sql_str)
        all_data = self.cursor.fetchall()
        if all_data:
            for rec in all_data:
                data_dict_oldviprecharge['activepeople'][int(rec[0])] = rec[1]
                data_dict_oldviprechargetimes['activepeople'][int(rec[0])] = rec[1]
                data_dict_oldviprechargeratio['activepeople'][int(rec[0])] = rec[1]
        #老用户付费
        sql_str = 'select mvip,count(a.uid),sum(money) from (select uid,sum(money/100) as money from pay_syn_day '+sql_where+'  group by uid) as a inner join (select uid,max(vip_level) as mvip from user_active_extend '+sql_where+'and regdate<\"'+min(date_list)+'\" group by uid) as b on a.uid=b.uid group by mvip;'
        self.cursor.execute(sql_str)
        all_data = self.cursor.fetchall()
        # | mvip | count(a.uid) | sum(money) |
        # +------+--------------+------------+
        # | 0 | 28 | 29.0000 |
        if all_data:
            for rec in all_data:
                data_dict_oldviprecharge['money'][int(rec[0])] = rec[2]
                data_dict_oldviprechargetimes['money'][int(rec[0])] = rec[2]
                data_dict_oldviprechargeratio['money'][int(rec[0])] = rec[2]

        # 老用户充值各档位人次占比
        sql_where_item = sql_where + 'and itemid in (' + self.easy_mysql.sql_value_str(item_list) + ') '
        sql_str = 'select itemid,mvip,count(a.uid),sum(times),sum(money) from (select uid,itemid,count(uid) as times,sum(money/100) as money from pay_syn_day_extend' + sql_where_item + '  group by uid,itemid) as a inner join (select uid,max(vip_level) as mvip from user_active_extend ' + sql_where + 'and regdate<\"'+min(date_list)+'\" group by uid) as b on a.uid=b.uid group by itemid,mvip;'
        print(sql_str)
        self.cursor.execute(sql_str)
        all_data = self.cursor.fetchall()
        if all_data:
            for rec in all_data:
                data_dict_oldviprecharge[int(rec[0])][int(rec[1])] = float(rec[2])
                data_dict_oldviprechargeratio[int(rec[0])][int(rec[1])] = float(rec[2])/float(data_dict_oldviprecharge['activepeople'][int(rec[1])])
                data_dict_oldviprechargetimes[int(rec[0])][int(rec[1])] = float(rec[3])

        #老用户购买各档位初始vip
        dateminus30 = (datetime.datetime.strptime(min(date_list),"%Y-%m-%d")-datetime.timedelta(days=30)).strftime("%Y-%m-%d")
        sql_wherevip = 'where date>=\"' + dateminus30 + '\" '
        dateminus1 = (datetime.datetime.strptime(min(date_list),"%Y-%m-%d") - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        sql_wherevip += 'and date<=\"' + dateminus1 + '\" '

        # 老用户7日前活跃人数
        dateminus7 = (datetime.datetime.strptime(min(date_list), "%Y-%m-%d") - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
        sql_where7 = 'where date>=\"' + dateminus7 + '\" '
        sql_where7 += 'and date<=\"' + dateminus1 + '\"'
        sql_str = 'select mvip,count(uid) from (select uid,max(vip_level) as mvip from user_active_extend '+ sql_where7 +' and uid not in (select uid from modernship_stat_busi.uid_block_list) group by uid) as a group by mvip;'
        print(sql_str)
        self.cursor.execute(sql_str)
        all_data = self.cursor.fetchall()
        for rec in all_data:
            if (dict_oldcoupon.has_key('activepeople')):
                dict_oldcoupon['activepeople'][rec[0]] = int(rec[1])


        sql_str = 'select mvip,itemid,count(distinct(a.uid)) from (select uid,max(vip_level) as mvip from user_active_extend '+ sql_wherevip +' and uid not in (select uid from modernship_stat_busi.uid_block_list) group by uid) as a inner join (select uid,itemid from  pay_syn_day_extend '+sql_where_item+') as b on a.uid=b.uid group by mvip,itemid;'
        print(sql_str)
        self.cursor.execute(sql_str)
        all_data = self.cursor.fetchall()
        if all_data:
            for rec in all_data:
                if(dict_oldcoupon.has_key(int(rec[1]))):
                    dict_oldcoupon[int(rec[1])][int(rec[0])] = float(rec[2])

        #加入翻译
        for k in data_dict_oldviprecharge.keys():
            data_dict_oldviprecharge[k]['trans']=Y_trans[k]
            data_dict_oldviprechargetimes[k]['trans']=Y_trans[k]
            data_dict_oldviprechargeratio[k]['trans']=Y_trans[k]

        for k in dict_oldcoupon.keys():
            dict_oldcoupon[k]['trans']=Y_trans[k]

        res_dict_oldpeople = {'data_dict': data_dict_oldviprecharge, 'X_list': X_list, 'Y_list': Y_list, 'head_name': head_name+'人数', 'X_trans': X_trans, 'default_value': default_value}
        res_dict_oldpeople["note"] = "*老用户每期各VIP段的各充值档位人数*"
        res_dict_oldpeopleratio = {'data_dict': data_dict_oldviprechargeratio, 'X_list': X_list, 'Y_list': Y_list,
                              'head_name': head_name + '占比', 'X_trans': X_trans, 'default_value': default_value}
        res_dict_oldpeopleratio["note"] = "*老用户每期各VIP段的各充值档位人数占比*"
        res_dict_oldpeople2 = {'data_dict': data_dict_oldviprechargetimes, 'X_list': X_list, 'Y_list': Y_list, 'head_name': head_name+'次数', 'X_trans': X_trans, 'default_value': default_value}
        res_dict_oldpeople["note"] = "*老用户每期各VIP段的各充值档位次数*"

        res_dict_oldcoupon = {'data_dict': dict_oldcoupon, 'X_list': X_list, 'Y_list': Y_list, 'head_name': '充值前VIP人数', 'X_trans': X_trans, 'default_value': default_value}
        res_dict_oldcoupon["note"] = "*老用户每期各fisrtVIP段的各充值档位人数*"

        return [res_dict_oldpeople,res_dict_oldpeopleratio,res_dict_oldpeople2,res_dict_oldcoupon]
    #老玩家首次充值
    def re_resultoldfirst(self,date_list,item_list,item_trans,headname):
        #viplist
        X_list = ["trans",0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,21,22,23,24,25]
        X_listtrans=['翻译']
        for i in X_list[1:]:
            X_listtrans.append('VIP'+ str(i))
        Y_list = ['activepeople','money']+item_list
        Y_listtrans = ['活跃人数','金额']+item_trans
        X_trans = dict(zip(X_list, X_listtrans))
        Y_trans = dict(zip(Y_list, Y_listtrans))

        head_name = headname
        default_value = ''

        data_dict_oldvipfirst = dict()
        data_dict_oldvipfirstratio = dict()
        for i in Y_list:
            data_dict_oldvipfirst[i] = dict()
            data_dict_oldvipfirstratio[i] = dict()
        sql_where = ' where date in (' + self.easy_mysql.sql_value_str(date_list) + ') '
        #老用户活跃人数
        sql_str = 'select mvip,count(uid) from(select uid,max(vip_level) as mvip from user_active_extend '+sql_where+'and regdate<\"'+min(date_list)+'\" and uid not in (select uid from modernship_stat_busi.uid_block_list) group by uid)as a group by mvip;'
        self.cursor.execute(sql_str)
        all_data = self.cursor.fetchall()
        if all_data:
            for rec in all_data:
                data_dict_oldvipfirst['activepeople'][int(rec[0])] = rec[1]
                data_dict_oldvipfirstratio['activepeople'][int(rec[0])] = rec[1]
        #老用户付费
        sql_str = 'select mvip,count(a.uid),sum(money) from (select uid,sum(money/100) as money from pay_syn_day '+sql_where+'  group by uid) as a inner join (select uid,max(vip_level) as mvip from user_active_extend '+sql_where+'and regdate<\"'+min(date_list)+'\" group by uid) as b on a.uid=b.uid group by mvip;'
        self.cursor.execute(sql_str)
        all_data = self.cursor.fetchall()
        # | mvip | count(a.uid) | sum(money) |
        # +------+--------------+------------+
        # | 0 | 28 | 29.0000 |
        if all_data:
            for rec in all_data:
                data_dict_oldvipfirst['money'][int(rec[0])] = rec[2]
                data_dict_oldvipfirstratio['money'][int(rec[0])] = rec[2]
        #recharge 老用户
        sql_where_item = sql_where + 'and itemid in (' + self.easy_mysql.sql_value_str(item_list) + ') '
        sql_str = 'select itemid,mvip,count(a.uid),sum(money) from (select uid,itemid,sum(money/100) as money from pay_syn_day_extend' + sql_where_item + 'and uid not in (select uid from pay_syn_day_extend where date<\"'+min(date_list)+'\")  group by uid,itemid) as a inner join (select uid,max(vip_level) as mvip from user_active_extend ' + sql_where + 'and regdate<\"'+min(date_list)+'\" group by uid) as b on a.uid=b.uid group by itemid,mvip;'
        print(sql_str)
        self.cursor.execute(sql_str)
        all_data = self.cursor.fetchall()
        if all_data:
            for rec in all_data:
                data_dict_oldvipfirst[int(rec[0])][int(rec[1])] = float(rec[2])
                data_dict_oldvipfirstratio[int(rec[0])][int(rec[1])] = float(rec[2])/float(data_dict_oldvipfirst['activepeople'][int(rec[1])])
        #加入翻译
        for k in data_dict_oldvipfirst.keys():
            data_dict_oldvipfirst[k]['trans']=Y_trans[k]
            data_dict_oldvipfirstratio[k]['trans']=Y_trans[k]
        res_dict_oldpeople = {'data_dict': data_dict_oldvipfirst, 'X_list': X_list, 'Y_list': Y_list, 'head_name': head_name+'人数', 'X_trans': X_trans, 'default_value': default_value}
        res_dict_oldpeople["note"] = "*老用户每期各VIP段的首次充值档位人数*"
        res_dict_oldpeopleratio = {'data_dict': data_dict_oldvipfirstratio, 'X_list': X_list, 'Y_list': Y_list, 'head_name': head_name+'占比', 'X_trans': X_trans, 'default_value': default_value}
        res_dict_oldpeopleratio["note"] = "*老用户每期各VIP段的首次充值档位人数占比*"
        return [res_dict_oldpeople,res_dict_oldpeopleratio]

    #老玩家用券
    def use_couponold(self,date_list,item_list,item_trans,headname):
        X_list = ["trans",0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,21,22,23,24,25]
        X_listtrans=['翻译']
        for i in X_list[1:]:
            X_listtrans.append('VIP'+ str(i))
        Y_list = ['activepeople','money']+item_list
        Y_listtrans = ['活跃人数','金额']+item_trans
        X_trans = dict(zip(X_list, X_listtrans))
        Y_trans = dict(zip(Y_list, Y_listtrans))

        head_name = headname
        default_value = ''

        dict_oldcoupon = dict()
        dict_oldcouponratio = dict()
        for i in Y_list:
            dict_oldcoupon[i] = dict()
            dict_oldcouponratio[i] = dict()
        sql_where = ' where date in (' + self.easy_mysql.sql_value_str(date_list) + ') '

        dateminus30 = (datetime.datetime.strptime(min(date_list),"%Y-%m-%d")-datetime.timedelta(days=30)).strftime("%Y-%m-%d")
        sql_wherevip = 'where date>=\"' + dateminus30 + '\" '
        dateminus1 = (datetime.datetime.strptime(min(date_list),"%Y-%m-%d") - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        sql_wherevip += 'and date<=\"' + dateminus1 + '\" '

        # 老用户7日前活跃人数
        dateminus7 = (datetime.datetime.strptime(min(date_list), "%Y-%m-%d") - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
        sql_where7 = 'where date>=\"' + dateminus7 + '\" '
        sql_where7 += 'and date<=\"' + dateminus1 + '\"'
        sql_str = 'select mvip,count(uid) from (select uid,max(vip_level) as mvip from user_active_extend '+ sql_where7 +' and uid not in (select uid from modernship_stat_busi.uid_block_list) group by uid) as a group by mvip;'
        print(sql_str)
        self.cursor.execute(sql_str)
        all_data = self.cursor.fetchall()
        for rec in all_data:
            if (dict_oldcoupon.has_key('activepeople')):
                dict_oldcoupon['activepeople'][rec[0]] = int(rec[1])


        #2 购买的vip
        # select mvip,itemid,count(distinct(a.uid)) from (select uid,max(vip_level) as mvip from modernship_gf_stat_base.user_active_extend where date<="2018-12-21" and uid not in (select uid from modernship_stat_busi.uid_block_list) group by uid) as a inner join (select uid,itemid from  modernship_stat_busi.diamond_coupon_needs where date>="2018-12-22") as b on a.uid=b.uid group by mvip,itemid;
        sql_str = 'select mvip,itemid,count(distinct(a.uid)) from (select uid,max(vip_level) as mvip from user_active_extend '+ sql_wherevip +' and uid not in (select uid from modernship_stat_busi.uid_block_list) group by uid) as a inner join (select uid,itemid from  modernship_stat_busi.diamond_coupon_needs '+sql_where+') as b on a.uid=b.uid group by mvip,itemid;'
        print(sql_str)
        self.cursor.execute(sql_str)
        all_data = self.cursor.fetchall()
        if all_data:
            for rec in all_data:
                if(dict_oldcoupon.has_key(int(rec[1]))):
                    dict_oldcoupon[int(rec[1])][int(rec[0])] = float(rec[2])
                    # dict_oldcouponratio[int(rec[1])][int(rec[0])] = float(rec[2])/float(data_dict_oldvipgiftbuy['activepeople'][int(rec[1])])

        #加入翻译
        for k in dict_oldcoupon.keys():
            dict_oldcoupon[k]['trans']=Y_trans[k]

        res_dict_oldpeople = {'data_dict': dict_oldcoupon, 'X_list': X_list, 'Y_list': Y_list,
                              'head_name': head_name, 'X_trans': X_trans, 'default_value': default_value}
        res_dict_oldpeople["note"] = "充值人数*"
        return [res_dict_oldpeople]

    ###新用户
    def re_resultnew(self, date_list, item_list, item_trans, headname):
        # viplist
        X_list = ["trans", 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]
        X_listtrans = ['翻译']
        for i in X_list[1:]:
            X_listtrans.append('VIP' + str(i))
        Y_list = ['activepeople', 'money','cash'] + item_list
        Y_listtrans = ['活跃人数', '金额','rmb钻石'] + item_trans
        X_trans = dict(zip(X_list, X_listtrans))
        Y_trans = dict(zip(Y_list, Y_listtrans))

        head_name = headname
        default_value = ''

        data_dict_oldvipgiftbuy = dict()
        data_dict_oldvipgiftbuyratio = dict()
        for i in Y_list:
            data_dict_oldvipgiftbuy[i] = dict()
            data_dict_oldvipgiftbuyratio[i] = dict()
        sql_where = ' where date in (' + self.easy_mysql.sql_value_str(date_list) + ') '
        # 新用户活跃人数
        sql_str = 'select mvip,count(uid) from(select uid,max(vip_level) as mvip from user_active_extend ' + sql_where + 'and regdate>=\"' + min(date_list) + '\" and uid not in (select uid from modernship_stat_busi.uid_block_list) group by uid)as a group by mvip;'
        print(sql_str)
        self.cursor.execute(sql_str)
        all_data = self.cursor.fetchall()
        if all_data:
            for rec in all_data:
                data_dict_oldvipgiftbuy['activepeople'][int(rec[0])] = rec[1]
                data_dict_oldvipgiftbuyratio['activepeople'][int(rec[0])] = rec[1]

        # 新用户付费
        sql_str = 'select mvip,count(a.uid),sum(money) from (select uid,sum(money/100) as money from pay_syn_day ' + sql_where + '  group by uid) as a inner join (select uid,max(vip_level) as mvip from user_active_extend ' + sql_where + 'and regdate>=\"' + min(date_list) + '\" group by uid) as b on a.uid=b.uid group by mvip;'
        print(sql_str)
        self.cursor.execute(sql_str)
        all_data = self.cursor.fetchall()
        # | mvip | count(a.uid) | sum(money) |
        # +------+--------------+------------+
        # | 0 | 28 | 29.0000 |
        if all_data:
            for rec in all_data:
                data_dict_oldvipgiftbuy['money'][int(rec[0])] = rec[2]
                data_dict_oldvipgiftbuyratio['money'][int(rec[0])] = rec[2]

        # 新用户
        # sql_where_item = sql_where + 'and itemid in (' + self.easy_mysql.sql_value_str(item_list) + ') '
        sql_str = 'select mlevel,mvip,count(uid) from (select uid,max(vip_level) as mvip,max(cash+diamond) as mlevel from modernship_stat_busi.diamond_detail_needs ' + sql_where + ' and uid not in (select uid from modernship_stat_busi.uid_block_list) and uid in (select uid from user_active_extend where regdate>=\"' + min(date_list) + '\") group by uid) as a group by mlevel,mvip;'
        print(sql_str)
        self.cursor.execute(sql_str)
        all_data = self.cursor.fetchall()
        if all_data:
            for rec in all_data:
                if(data_dict_oldvipgiftbuy.has_key(int(rec[0]))):
                    data_dict_oldvipgiftbuy[int(rec[0])][int(rec[1])] = float(rec[2])
                    data_dict_oldvipgiftbuyratio[int(rec[0])][int(rec[1])] = float(rec[2]) / float(data_dict_oldvipgiftbuy['activepeople'][int(rec[1])])
                    # data_dict_oldvipgiftbuy[int(rec[0])][int(rec[1])] = float(rec[2]) / float(data_dict_oldvipgiftbuy['activepeople'][int(rec[1])])

        sql_str = 'select mvip,sum(cash) from (select uid,max(vip_level) as mvip,sum(cash) as cash from modernship_stat_busi.diamond_detail_needs '+sql_where+' and uid not in (select uid from modernship_stat_busi.uid_block_list) and uid in (select uid from user_active_extend where regdate>=\"'+min(date_list)+'\") group by uid) as a group by mvip;'
        self.cursor.execute(sql_str)
        all_data = self.cursor.fetchall()
        if all_data:
            for rec in all_data:
                data_dict_oldvipgiftbuy['cash'][int(rec[0])] = float(rec[1])
                data_dict_oldvipgiftbuyratio['cash'][int(rec[0])] = float(rec[1])

        # 加入翻译
        for k in data_dict_oldvipgiftbuy.keys():
            data_dict_oldvipgiftbuy[k]['trans'] = Y_trans[k]
            data_dict_oldvipgiftbuyratio[k]['trans'] = Y_trans[k]
        res_dict_oldpeople = {'data_dict': data_dict_oldvipgiftbuy, 'X_list': X_list, 'Y_list': Y_list, 'head_name': head_name+'人数', 'X_trans': X_trans, 'default_value': default_value}
        res_dict_oldpeople["note"] = "每期各VIP段招财最高档位的人数*"
        res_dict_oldpeopleratio= {'data_dict': data_dict_oldvipgiftbuyratio, 'X_list': X_list, 'Y_list': Y_list, 'head_name': head_name+'占比', 'X_trans': X_trans, 'default_value': default_value}
        res_dict_oldpeopleratio["note"] = "每期各VIP段招财最高档位的人数占比*"

        return [res_dict_oldpeople,res_dict_oldpeopleratio]

        # 充值人次

    def re_resultnewrecharge(self, date_list, item_list, item_trans, headname):
        # viplist
        X_list = ["trans", 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]
        X_listtrans = ['翻译']
        for i in X_list[1:]:
            X_listtrans.append('VIP' + str(i))
        Y_list = ['activepeople', 'money'] + item_list
        Y_listtrans = ['活跃人数', '金额'] + item_trans
        X_trans = dict(zip(X_list, X_listtrans))
        Y_trans = dict(zip(Y_list, Y_listtrans))

        head_name = headname
        default_value = ''

        data_dict_oldviprecharge = dict()
        data_dict_oldviprechargeratio = dict()
        data_dict_oldviprechargetimes = dict()
        dict_oldcoupon = dict()
        for i in Y_list:
            data_dict_oldviprecharge[i] = dict()
            data_dict_oldviprechargetimes[i] = dict()
            data_dict_oldviprechargeratio[i] = dict()
            dict_oldcoupon[i] = dict()

        sql_where = ' where date in (' + self.easy_mysql.sql_value_str(date_list) + ') '
        # 老用户活跃人数
        sql_str = 'select mvip,count(uid) from(select uid,max(vip_level) as mvip from user_active_extend ' + sql_where + 'and regdate>=\"' + min(date_list) + '\" and uid not in (select uid from modernship_stat_busi.uid_block_list) group by uid)as a group by mvip;'
        self.cursor.execute(sql_str)
        all_data = self.cursor.fetchall()
        if all_data:
            for rec in all_data:
                data_dict_oldviprecharge['activepeople'][int(rec[0])] = rec[1]
                data_dict_oldviprechargetimes['activepeople'][int(rec[0])] = rec[1]
                data_dict_oldviprechargeratio['activepeople'][int(rec[0])] = rec[1]
        # 老用户付费
        sql_str = 'select mvip,count(a.uid),sum(money) from (select uid,sum(money/100) as money from pay_syn_day ' + sql_where + '  group by uid) as a inner join (select uid,max(vip_level) as mvip from user_active_extend ' + sql_where + 'and regdate>=\"' + min(date_list) + '\" group by uid) as b on a.uid=b.uid group by mvip;'
        self.cursor.execute(sql_str)
        all_data = self.cursor.fetchall()
        # | mvip | count(a.uid) | sum(money) |
        # +------+--------------+------------+
        # | 0 | 28 | 29.0000 |
        if all_data:
            for rec in all_data:
                data_dict_oldviprecharge['money'][int(rec[0])] = rec[2]
                data_dict_oldviprechargetimes['money'][int(rec[0])] = rec[2]
                data_dict_oldviprechargeratio['money'][int(rec[0])] = rec[2]
        # 新用户充值付费
        sql_where_item = sql_where + 'and itemid in (' + self.easy_mysql.sql_value_str(item_list) + ') '
        sql_str = 'select itemid,mvip,count(a.uid),sum(times),sum(money) from (select uid,itemid,count(uid) as times,sum(money/100) as money from pay_syn_day_extend' + sql_where_item + '  group by uid,itemid) as a inner join (select uid,max(vip_level) as mvip from user_active_extend ' + sql_where + 'and regdate>=\"' + min(date_list) + '\" group by uid) as b on a.uid=b.uid group by itemid,mvip;'
        print(sql_str)
        self.cursor.execute(sql_str)
        all_data = self.cursor.fetchall()
        if all_data:
            for rec in all_data:
                data_dict_oldviprecharge[int(rec[0])][int(rec[1])] = float(rec[2])
                data_dict_oldviprechargeratio[int(rec[0])][int(rec[1])] = float(rec[2])/float(data_dict_oldviprecharge['activepeople'][int(rec[1])])
                data_dict_oldviprechargetimes[int(rec[0])][int(rec[1])] = float(rec[3])

        #新用户fisrt vip档位购买
        sql_str = 'select mvip,count(uid) from (select uid,0 as mvip from user_active_extend '+ sql_where +' and uid not in (select uid from modernship_stat_busi.uid_block_list) and regdate>=\"' + min(date_list) + '\" group by uid) as a group by mvip;'
        print(sql_str)
        self.cursor.execute(sql_str)
        all_data = self.cursor.fetchall()
        for rec in all_data:
            if (dict_oldcoupon.has_key('activepeople')):
                dict_oldcoupon['activepeople'][0] = int(rec[1])

        sql_str = 'select mvip,itemid,count(distinct(a.uid)) from (select uid,0 as mvip from user_active_extend ' + sql_where + ' and uid not in (select uid from modernship_stat_busi.uid_block_list) and regdate>=\"' + min(date_list) + '\"group by uid) as a inner join (select uid,itemid from  pay_syn_day_extend ' + sql_where_item + ') as b on a.uid=b.uid group by mvip,itemid;'
        print(sql_str)
        self.cursor.execute(sql_str)
        all_data = self.cursor.fetchall()
        if all_data:
            for rec in all_data:
                if(dict_oldcoupon.has_key(int(rec[1]))):
                    dict_oldcoupon[int(rec[1])][0] = float(rec[2])
                    # dict_oldcouponratio[int(rec[1])][int(rec[0])] = float(rec[2])/float(data_dict_oldvipgiftbuy['activepeople'][int(rec[1])])

        #加入翻译
        for k in dict_oldcoupon.keys():
            dict_oldcoupon[k]['trans']=Y_trans[k]

        # 加入翻译
        for k in data_dict_oldviprecharge.keys():
            data_dict_oldviprecharge[k]['trans'] = Y_trans[k]
            data_dict_oldviprechargetimes[k]['trans'] = Y_trans[k]
            data_dict_oldviprechargeratio[k]['trans'] = Y_trans[k]
        res_dict_oldpeople = {'data_dict': data_dict_oldviprecharge, 'X_list': X_list, 'Y_list': Y_list,
                              'head_name': head_name + '人数', 'X_trans': X_trans, 'default_value': default_value}
        res_dict_oldpeople["note"] = "*新用户每期各VIP段的各充值档位人数*"
        res_dict_oldpeopleratio = {'data_dict': data_dict_oldviprechargeratio, 'X_list': X_list, 'Y_list': Y_list,
                                   'head_name': head_name + '占比', 'X_trans': X_trans, 'default_value': default_value}
        res_dict_oldpeopleratio["note"] = "*新用户每期各VIP段的各充值档位人数占比*"
        res_dict_oldpeople2 = {'data_dict': data_dict_oldviprechargetimes, 'X_list': X_list, 'Y_list': Y_list,
                               'head_name': head_name + '次数', 'X_trans': X_trans, 'default_value': default_value}
        dict_oldcoupon["note"] = "*新用户每期各VIP段的各充值档位次数*"
        dict_oldcoupon = {'data_dict': dict_oldcoupon, 'X_list': X_list, 'Y_list': Y_list,
                              'head_name': '充值前VIP人数', 'X_trans': X_trans, 'default_value': default_value}
        res_dict_oldpeople["note"] = "充值人数*"
        return [res_dict_oldpeople, res_dict_oldpeopleratio, res_dict_oldpeople2,dict_oldcoupon]

    def re_resultnewfirst(self, date_list, item_list, item_trans, headname):
        # viplist
        X_list = ["trans", 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]
        X_listtrans = ['翻译']
        for i in X_list[1:]:
            X_listtrans.append('VIP' + str(i))
        Y_list = ['activepeople', 'money'] + item_list
        Y_listtrans = ['活跃人数', '金额'] + item_trans
        X_trans = dict(zip(X_list, X_listtrans))
        Y_trans = dict(zip(Y_list, Y_listtrans))

        head_name = headname
        default_value = ''

        data_dict_oldvipfirst = dict()
        data_dict_oldvipfirstratio = dict()
        for i in Y_list:
            data_dict_oldvipfirst[i] = dict()
            data_dict_oldvipfirstratio[i] = dict()

        sql_where = ' where date in (' + self.easy_mysql.sql_value_str(date_list) + ') '
        # 老用户活跃人数
        sql_str = 'select mvip,count(uid) from(select uid,max(vip_level) as mvip from user_active_extend ' + sql_where + 'and regdate>=\"' + min(date_list) + '\" and uid not in (select uid from modernship_stat_busi.uid_block_list) group by uid)as a group by mvip;'
        self.cursor.execute(sql_str)
        all_data = self.cursor.fetchall()
        if all_data:
            for rec in all_data:
                data_dict_oldvipfirst['activepeople'][int(rec[0])] = rec[1]
                data_dict_oldvipfirstratio['activepeople'][int(rec[0])] = rec[1]
        # 老用户付费
        sql_str = 'select mvip,count(a.uid),sum(money) from (select uid,sum(money/100) as money from pay_syn_day ' + sql_where + '  group by uid) as a inner join (select uid,max(vip_level) as mvip from user_active_extend ' + sql_where + 'and regdate>=\"' + min(date_list) + '\" group by uid) as b on a.uid=b.uid group by mvip;'
        self.cursor.execute(sql_str)
        all_data = self.cursor.fetchall()
        # | mvip | count(a.uid) | sum(money) |
        # +------+--------------+------------+
        # | 0 | 28 | 29.0000 |
        if all_data:
            for rec in all_data:
                data_dict_oldvipfirst['money'][int(rec[0])] = rec[2]
                data_dict_oldvipfirstratio['money'][int(rec[0])] = rec[2]
        # recharge 老用户
        sql_where_item = sql_where + 'and itemid in (' + self.easy_mysql.sql_value_str(item_list) + ') '
        sql_str = 'select itemid,mvip,count(a.uid),sum(money) from (select uid,itemid,sum(money/100) as money from pay_syn_day_extend' + sql_where_item + 'and uid not in (select uid from pay_syn_day_extend where date<\"' + min(date_list) + '\")  group by uid,itemid) as a inner join (select uid,max(vip_level) as mvip from user_active_extend ' + sql_where + 'and regdate>=\"' + min(date_list) + '\" group by uid) as b on a.uid=b.uid group by itemid,mvip;'
        print(sql_str)
        self.cursor.execute(sql_str)
        all_data = self.cursor.fetchall()
        if all_data:
            for rec in all_data:
                data_dict_oldvipfirst[int(rec[0])][int(rec[1])] = float(rec[2])
                data_dict_oldvipfirstratio[int(rec[0])][int(rec[1])] = float(rec[2])/float(data_dict_oldvipfirst['activepeople'][int(rec[1])])
        # 加入翻译
        for k in data_dict_oldvipfirst.keys():
            data_dict_oldvipfirst[k]['trans']=Y_trans[k]
            data_dict_oldvipfirstratio[k]['trans']=Y_trans[k]
        res_dict_oldpeople = {'data_dict': data_dict_oldvipfirst, 'X_list': X_list, 'Y_list': Y_list, 'head_name': head_name+'人数', 'X_trans': X_trans, 'default_value': default_value}
        res_dict_oldpeople["note"] = "*新用户每期各VIP段的首次充值档位人数*"
        res_dict_oldpeopleratio = {'data_dict': data_dict_oldvipfirstratio, 'X_list': X_list, 'Y_list': Y_list, 'head_name': head_name+'占比', 'X_trans': X_trans, 'default_value': default_value}
        res_dict_oldpeopleratio["note"] = "*新用户每期各VIP段的首次充值档位人数占比*"
        return [res_dict_oldpeople,res_dict_oldpeopleratio]

    def run_xls(self,date_list,res_dict_list1,res_dict_list2,res_dict_list3,res_dict_list4,str1):
        new_sheet = self.xls_writer.new_sheet(str(date_list[0])+'期'+str1, self.wbk)
        new_sheet.col(0).width = 256 * 20
        new_sheet.col(1).width = 256 * 20
        line_num = [0]
        #增加写入情况
        for i in range(len(res_dict_list1)):
            write_standard_form(res_dict_list1[i],new_sheet,line_num,self.style)
            line_num[0]+=2
        for i in range(len(res_dict_list2)):
            write_standard_form(res_dict_list2[i],new_sheet,line_num,self.style)
            line_num[0]+=2
        for i in range(len(res_dict_list3)):
            write_standard_form(res_dict_list3[i],new_sheet,line_num,self.style)
            line_num[0]+=2
        for i in range(len(res_dict_list4)):
            write_standard_form(res_dict_list4[i],new_sheet,line_num,self.style)
            line_num[0]+=2

    #新玩家用券
    def use_couponnew(self,date_list,item_list,item_trans,headname):
        X_list = ["trans",0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,21,22,23,24,25]
        X_listtrans=['翻译']
        for i in X_list[1:]:
            X_listtrans.append('VIP'+ str(i))
        Y_list =item_list
        Y_listtrans = item_trans
        X_trans = dict(zip(X_list, X_listtrans))
        Y_trans = dict(zip(Y_list, Y_listtrans))

        head_name = headname
        default_value = ''

        dict_oldcoupon = dict()
        dict_oldcouponratio = dict()
        for i in Y_list:
            dict_oldcoupon[i] = dict()
            dict_oldcouponratio[i] = dict()
        sql_where = ' where date in (' + self.easy_mysql.sql_value_str(date_list) + ') '

        # dateminus30 = (datetime.datetime.strptime(min(date_list))-datetime.timedelta(days=30)).strftime("%Y-%m-%d")
        # sql_wherevip = 'where date>=\"' + dateminus30 + '\" '
        # dateminus1 = (datetime.datetime.strptime(min(date_list)) - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        # sql_wherevip += 'and date<=\"' + dateminus1 + '\" '

        #2 购买的vip
        # select mvip,itemid,count(distinct(a.uid)) from (select uid,max(vip_level) as mvip from modernship_gf_stat_base.user_active_extend where date<="2018-12-21" and uid not in (select uid from modernship_stat_busi.uid_block_list) group by uid) as a inner join (select uid,itemid from  modernship_stat_busi.diamond_coupon_needs where date>="2018-12-22") as b on a.uid=b.uid group by mvip,itemid;
        sql_str = 'select mvip,count(uid) from (select uid,0 as mvip from user_active_extend '+ sql_where +' and uid not in (select uid from modernship_stat_busi.uid_block_list) and regdate>=\"' + min(date_list) + '\" group by uid) as a group by mvip;'
        print(sql_str)
        self.cursor.execute(sql_str)
        all_data = self.cursor.fetchall()
        for rec in all_data:
            if (dict_oldcoupon.has_key('activepeople')):
                dict_oldcoupon['activepeople'][0] = int(rec[1])

        sql_str = 'select mvip,itemid,count(distinct(a.uid)) from (select uid,0 as mvip from user_active_extend '+ sql_where +' and uid not in (select uid from modernship_stat_busi.uid_block_list) and regdate>=\"' + min(date_list) + '\"group by uid) as a inner join (select uid,itemid from  modernship_stat_busi.diamond_coupon_needs '+sql_where+') as b on a.uid=b.uid group by mvip,itemid;'
        print(sql_str)
        self.cursor.execute(sql_str)
        all_data = self.cursor.fetchall()
        if all_data:
            for rec in all_data:
                if(dict_oldcoupon.has_key(int(rec[1]))):
                    dict_oldcoupon[int(rec[1])][0] = float(rec[2])
                    # dict_oldcouponratio[int(rec[1])][int(rec[0])] = float(rec[2])/float(data_dict_oldvipgiftbuy['activepeople'][int(rec[1])])

        #加入翻译
        for k in dict_oldcoupon.keys():
            dict_oldcoupon[k]['trans']=Y_trans[k]

        res_dict_oldpeople = {'data_dict': dict_oldcoupon, 'X_list': X_list, 'Y_list': Y_list,
                              'head_name': head_name, 'X_trans': X_trans, 'default_value': default_value}
        res_dict_oldpeople["note"] = "充值人数*"
        return [res_dict_oldpeople]

    def end_all(self):
        file_name = ConfParameters.ConfParameters().save_path + 'luckycat.xls'
        self.wbk.save(file_name)
        self.db.close()

    def executeold(self,date_list,item_list1,item_trans1,headname1,item_list2,item_trans2,headname2,item_list3,item_trans3,headname3,item_list4,item_trans4, headname4):
        res_oldvipgift = self.re_resultold(date_list,item_list1,item_trans1,headname1)
        res_olditembuy = self.re_resultoldrecharge(date_list,item_list2,item_trans2,headname2)
        res_oldfirstbuy = self.re_resultoldfirst(date_list, item_list3, item_trans3, headname3)
        res_use_couponold = self.use_couponold(date_list,item_list4,item_trans4, headname4)
        self.run_xls(date_list,res_oldvipgift,res_olditembuy,res_oldfirstbuy,res_use_couponold,'old')

    def executenew(self,date_list,item_list1,item_trans1,headname1,item_list2,item_trans2,headname2,item_list3,item_trans3,headname3,item_list4,item_trans4, headname4):
        res_newvipgift = self.re_resultnew(date_list,item_list1,item_trans1,headname1)
        res_newitembuy = self.re_resultnewrecharge(date_list,item_list2,item_trans2,headname2)
        res_newfirstbuy = self.re_resultnewfirst(date_list, item_list3, item_trans3, headname3)
        res_use_couponold = self.use_couponnew(date_list, item_list4, item_trans4, headname4)
        self.run_xls(date_list, res_newvipgift, res_newitembuy, res_newfirstbuy,res_use_couponold,'new')







if __name__ == '__main__':

    vipgift_list = [388,888,1588,2888,4888,8888,13888,18888,26888,35888]
    vipgift_trans= [1,2,3,4,5,6,7,8,9,10]
    recharge_list = [1,2,3,4,5,6,30,31,32,33,51,52,53]
    coupon_list = [38001,38002,38003,38004,38005,38006]
    coupon_trans = ["60钻石券","300钻石券","980钻石券","1980钻石券","3280钻石券","6480钻石券"]
    recharge_trans = ['60钻石','300钻石','980钻石','1980钻石','3280钻石','6480钻石','银星月卡','至尊月卡','永久卡','远洋通行证','19980钻石','49980钻石','超值周卡']
    luckycatobj = LuckyCat()
    date_list_four = ["2018-12-22","2018-12-23","2018-12-24","2018-12-25"]
    luckycatobj.executeold(date_list_four,vipgift_list,vipgift_trans,'招财档位',recharge_list,recharge_trans,'充值档位',recharge_list,recharge_trans,'首次充值',coupon_list,coupon_trans,'用券人数')
    luckycatobj.executenew(date_list_four,vipgift_list,vipgift_trans,'招财档位',recharge_list,recharge_trans,'充值档位',recharge_list,recharge_trans,'首次充值',coupon_list,coupon_trans,'用券人数')
    date_list_one = ["2018-11-09", "2018-11-10", "2018-11-11"]
    luckycatobj.executeold(date_list_one,vipgift_list,vipgift_trans,'招财档位',recharge_list,recharge_trans,'充值档位',recharge_list,recharge_trans,'首次充值',coupon_list,coupon_trans,'用券人数')
    luckycatobj.executenew(date_list_one,vipgift_list,vipgift_trans,'招财档位',recharge_list,recharge_trans,'充值档位',recharge_list,recharge_trans,'首次充值',coupon_list,coupon_trans,'用券人数')
    date_list_two = ["2018-10-04","2018-10-05","2018-10-06"]
    luckycatobj.executeold(date_list_two, vipgift_list, vipgift_trans, '招财档位', recharge_list, recharge_trans, '充值档位',recharge_list, recharge_trans, '首次充值',coupon_list,coupon_trans,'用券人数')
    luckycatobj.executenew(date_list_two, vipgift_list, vipgift_trans, '招财档位', recharge_list, recharge_trans, '充值档位',recharge_list, recharge_trans, '首次充值',coupon_list,coupon_trans,'用券人数')
    date_list_three = ["2018-08-15", "2018-08-16", "2018-08-17"]
    luckycatobj.executeold(date_list_three, vipgift_list, vipgift_trans, '招财档位', recharge_list, recharge_trans, '充值档位',recharge_list, recharge_trans, '首次充值',coupon_list,coupon_trans,'用券人数')
    luckycatobj.executenew(date_list_three, vipgift_list, vipgift_trans, '招财档位', recharge_list, recharge_trans, '充值档位',recharge_list, recharge_trans, '首次充值',coupon_list,coupon_trans,'用券人数')

    luckycatobj.end_all()

