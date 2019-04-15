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


class WelfareBuy():
    def __init__(self):
        # self.conf_path = ConfParameters.ConfParameters().conf_path
        # initialize
        # # mysql
        # mysql_para = ConfParameters.ConfParameters().mysql_conf
        # self.db = MySQLdb.connect(mysql_para['ip'], mysql_para['users'], mysql_para['password'],
        #                           mysql_para['stat_pay'])
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


    def re_resultold(self,date_list,item_list,item_trans,headname):
        #viplist
        X_list = ["trans",0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,21,22,23,24,25]
        X_listtrans=['翻译']
        for i in X_list[1:]:
            X_listtrans.append('VIP'+ str(i))
        # X_listtrans = ['翻译']+map(lambda x: 'VIP' + str(x), X_list)
        Y_list = ['activepeople','money']+item_list
        Y_listtrans = ['活跃人数','金额']+item_trans
        X_trans = dict(zip(X_list, X_listtrans))
        Y_trans = dict(zip(Y_list, Y_listtrans))

        head_name = headname
        default_value = ''

        data_dict_oldpeople = dict()
        data_dict_oldmoney = dict()
        for i in Y_list:
            data_dict_oldpeople[i] = dict()
            data_dict_oldmoney[i] = dict()

        sql_where = ' where date in (' + self.easy_mysql.sql_value_str(date_list) + ') '
        #老用户活跃人数
        sql_str = 'select mvip,count(uid) from(select uid,max(vip_level) as mvip from user_active_extend '+sql_where+'and datediff(date,regdate)>=15 and uid not in (select uid from modernship_stat_busi.uid_block_list) group by uid)as a group by mvip;'
        print(sql_str)
        self.cursor.execute(sql_str)
        all_data = self.cursor.fetchall()
        if all_data:
            for rec in all_data:
                data_dict_oldpeople['activepeople'][int(rec[0])] = rec[1]
                data_dict_oldmoney['activepeople'][int(rec[0])] = rec[1]
        #老用户付费
        sql_str = 'select mvip,count(a.uid),sum(money) from (select uid,sum(money/100) as money from pay_syn_day '+sql_where+'  group by uid) as a inner join (select uid,max(vip_level) as mvip from user_active_extend '+sql_where+'and datediff(date,regdate)>=15 group by uid) as b on a.uid=b.uid group by mvip;'
        self.cursor.execute(sql_str)
        all_data = self.cursor.fetchall()
        # | mvip | count(a.uid) | sum(money) |
        # +------+--------------+------------+
        # | 0 | 28 | 29.0000 |
        if all_data:
            for rec in all_data:
                data_dict_oldpeople['money'][int(rec[0])] = rec[2]
                data_dict_oldmoney['money'][int(rec[0])] = rec[2]

        #
        sql_where_item = sql_where + 'and itemid in (' + self.easy_mysql.sql_value_str(item_list) + ') '
        sql_str = 'select itemid,mvip,count(a.uid),sum(money) from (select uid,itemid,sum(money/100) as money from pay_syn_day_extend' + sql_where_item + '  group by uid,itemid) as a inner join (select uid,max(vip_level) as mvip from user_active_extend ' + sql_where + 'and datediff(date,regdate)>=15 group by uid) as b on a.uid=b.uid group by itemid,mvip;'
        self.cursor.execute(sql_str)
        all_data = self.cursor.fetchall()
        if all_data:
            for rec in all_data:
                data_dict_oldpeople[int(rec[0])][int(rec[1])] = float(rec[2])/float(data_dict_oldpeople['activepeople'][int(rec[1])])
                data_dict_oldmoney[int(rec[0])][int(rec[1])] = float(rec[3])/float(data_dict_oldmoney['money'][int(rec[1])])
        #加入翻译
        for k in data_dict_oldpeople.keys():
            data_dict_oldpeople[k]['trans']=Y_trans[k]
        for k in data_dict_oldmoney.keys():
            data_dict_oldmoney[k]['trans']=Y_trans[k]

        res_dict_oldpeople = {'data_dict': data_dict_oldpeople, 'X_list': X_list, 'Y_list': Y_list, 'head_name': head_name+'人数占比', 'X_trans': X_trans,
                    'default_value': default_value}
        res_dict_oldpeople["note"] = "每期各VIP段的购买人数占比*"

        res_dict_oldmoney = {'data_dict': data_dict_oldmoney, 'X_list': X_list, 'Y_list': Y_list, 'head_name': head_name+'金额占比', 'X_trans': X_trans,
                    'default_value': default_value}
        res_dict_oldmoney["note"] = "每期各VIP段的付费占比*"

        return [res_dict_oldpeople,res_dict_oldmoney]

    def re_resultnew(self,date_list,item_list,item_trans,headname):
        #viplist
        X_list = ["trans",0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,21,22,23,24,25]
        X_listtrans=['翻译']
        for i in X_list[1:]:
            X_listtrans.append('VIP'+ str(i))
        # X_listtrans = ['翻译']+map(lambda x: 'VIP' + str(x), X_list)
        Y_list = ['activepeople','money']+item_list
        Y_listtrans = ['活跃人数','金额']+item_trans
        X_trans = dict(zip(X_list, X_listtrans))
        Y_trans = dict(zip(Y_list, Y_listtrans))

        head_name = headname
        default_value = ''

        data_dict_newpeople = dict()
        data_dict_newmoney = dict()
        for i in Y_list:
            data_dict_newpeople[i] = dict()
            data_dict_newmoney[i] = dict()

        sql_where = ' where date in (' + self.easy_mysql.sql_value_str(date_list) + ') '
        #老用户活跃人数
        sql_str = 'select mvip,count(uid) from(select uid,max(vip_level) as mvip from user_active_extend '+sql_where+'and datediff(date,regdate)<15 and uid not in (select uid from modernship_stat_busi.uid_block_list) group by uid)as a group by mvip;'

        self.cursor.execute(sql_str)
        all_data = self.cursor.fetchall()
        if all_data:
            for rec in all_data:
                data_dict_newpeople['activepeople'][int(rec[0])] = rec[1]
                data_dict_newmoney['activepeople'][int(rec[0])] = rec[1]
        #新用户付费
        sql_str = 'select mvip,count(a.uid),sum(money) from (select uid,sum(money/100) as money from pay_syn_day '+sql_where+'  group by uid) as a inner join (select uid,max(vip_level) as mvip from user_active_extend '+sql_where+'and datediff(date,regdate)<15 group by uid) as b on a.uid=b.uid group by mvip;'
        self.cursor.execute(sql_str)
        all_data = self.cursor.fetchall()
        # | mvip | count(a.uid) | sum(money) |
        # +------+--------------+------------+
        # | 0 | 28 | 29.0000 |
        if all_data:
            for rec in all_data:
                data_dict_newpeople['money'][int(rec[0])] = rec[2]
                data_dict_newmoney['money'][int(rec[0])] = rec[2]

        #
        sql_where_item = sql_where + 'and itemid in (' + self.easy_mysql.sql_value_str(item_list) + ') '
        sql_str = 'select itemid,mvip,count(a.uid),sum(money) from (select uid,itemid,sum(money/100) as money from pay_syn_day_extend' + sql_where_item + '  group by uid,itemid) as a inner join (select uid,max(vip_level) as mvip from user_active_extend ' + sql_where + 'and datediff(date,regdate)<15 group by uid) as b on a.uid=b.uid group by itemid,mvip;'
        self.cursor.execute(sql_str)
        all_data = self.cursor.fetchall()
        if all_data:
            for rec in all_data:
                data_dict_newpeople[int(rec[0])][int(rec[1])] = float(rec[2])/float(data_dict_newpeople['activepeople'][int(rec[1])])
                data_dict_newmoney[int(rec[0])][int(rec[1])] = float(rec[3])/float(data_dict_newmoney['money'][int(rec[1])])
        #加入翻译
        for k in data_dict_newpeople.keys():
            data_dict_newpeople[k]['trans']=Y_trans[k]
        for k in data_dict_newmoney.keys():
            data_dict_newmoney[k]['trans']=Y_trans[k]

        res_dict_newpeople = {'data_dict': data_dict_newpeople, 'X_list': X_list, 'Y_list': Y_list, 'head_name': head_name+'人数占比', 'X_trans': X_trans,
                    'default_value': default_value}
        res_dict_newpeople["note"] = "每期各VIP段的购买人数占比*"

        res_dict_newmoney = {'data_dict': data_dict_newmoney, 'X_list': X_list, 'Y_list': Y_list, 'head_name': head_name+'金额占比', 'X_trans': X_trans,
                    'default_value': default_value}
        res_dict_newmoney["note"] = "每期各VIP段的付费占比*"

        return [res_dict_newpeople,res_dict_newmoney]



    def run_xls(self,date_list,res_dict_list_old,res_dict_list_new):
        new_sheet = self.xls_writer.new_sheet(str(date_list[0])+'期', self.wbk)
        new_sheet.col(0).width = 256 * 20
        new_sheet.col(1).width = 256 * 20
        line_num = [0]
        #增加写入情况
        for i in range(len(res_dict_list_old)):
            write_standard_form(res_dict_list_old[i],new_sheet,line_num,self.style)
            line_num[0]+=2
        for i in range(len(res_dict_list_new)):
            write_standard_form(res_dict_list_new[i],new_sheet,line_num,self.style)
            line_num[0]+=2


    def end_all(self):
        file_name = ConfParameters.ConfParameters().save_path + 'welfarebuygather.xls'
        self.wbk.save(file_name)
        self.db.close()

    def execute(self,date_list,item_list_old,item_list_new,item_trans_old,item_trans_new,headname):
        res_dict_list_old = self.re_resultold(date_list,item_list_old,item_trans_old,headname)
        res_dict_list_new = self.re_resultnew(date_list,item_list_new,item_trans_new,headname)
        self.run_xls(date_list,res_dict_list_old,res_dict_list_new)




if __name__ == '__main__':
    # date_list_one = ["2018-11-01","2018-11-02"]
    # date_list_one = ["2018-11-01","2018-11-07"]
    date_list_one = DateList.DateList().get_date_list("2018-11-01","2018-11-07")
    item_list_old = [17,20,21,24]
    item_trans_old = ['初级科技选择箱','高级航母科技随机包','15导弹选择箱','15战舰30碎片选择箱']
    item_list_new = [14,15,16,19,22,23]
    item_trans_new = ['001碎片','051C碎片','001碎片','高级航母科技随机包','052C碎片','爱宕碎片']
    welfareobj = WelfareBuy()
    welfareobj.execute(date_list_one, item_list_old, item_list_new, item_trans_old, item_trans_new, '1101-1107')
    # date_list_one = ["2018-10-15", "2018-10-22"]
    date_list_one = DateList.DateList().get_date_list("2018-10-15", "2018-10-22")
    welfareobj.execute(date_list_one, item_list_new, item_list_new, item_trans_new, item_trans_new, '1015-1022')

    # welfareobj.execute(date_list_one, item_list_old, item_list_new, item_trans_old, item_trans_new,'1101-1102')
    # date_list_one = ["2018-11-03", "2018-11-04"]
    # welfareobj.execute(date_list_one,  item_list_old, item_list_new, item_trans_old, item_trans_new,'1103-1104')
    # date_list_one = ["2018-11-05", "2018-11-06"]
    # welfareobj.execute(date_list_one, item_list_old, item_list_new, item_trans_old, item_trans_new, '1105-1106')
    # date_list_one = ["2018-11-07", "2018-11-08"]
    # welfareobj.execute(date_list_one, item_list_old, item_list_new, item_trans_old, item_trans_new, '1107-1108')
    # date_list_one = ["2018-10-03", "2018-10-05"]
    # welfareobj.execute(date_list_one, item_list_new, item_list_new, item_trans_new, item_trans_new, '1003-1005')
    # date_list_one = ["2018-10-06", "2018-10-08"]
    # welfareobj.execute(date_list_one, item_list_new, item_list_new, item_trans_new, item_trans_new, '1006-1008')
    # date_list_one = ["2018-10-09", "2018-10-11"]
    # welfareobj.execute(date_list_one, item_list_new, item_list_new, item_trans_new, item_trans_new, '1009-1011')
    # date_list_one = ["2018-10-12", "2018-10-14"]
    # welfareobj.execute(date_list_one, item_list_new, item_list_new, item_trans_new, item_trans_new, '1012-1014')
    # date_list_one = ["2018-10-15", "2018-10-17"]
    # welfareobj.execute(date_list_one, item_list_new, item_list_new, item_trans_new, item_trans_new, '1015-1017')
    # date_list_one = ["2018-10-18", "2018-10-19"]
    # welfareobj.execute(date_list_one, item_list_new, item_list_new, item_trans_new, item_trans_new, '1018-1019')
    # date_list_one = ["2018-10-20", "2018-10-21"]
    # welfareobj.execute(date_list_one, item_list_new, item_list_new, item_trans_new, item_trans_new, '1020-1021')
    # date_list_one = ["2018-10-22", "2018-10-23"]
    # welfareobj.execute(date_list_one, item_list_new, item_list_new, item_trans_new, item_trans_new, '1022-1023')


    welfareobj.end_all()

