#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : qs_table1.py
# @Author: MoonKuma
# @Date  : 2019/1/4
# @Desc  : table1 of qs table

import MySQLdb
import re
import xlwt
import sys

from conf import ConfParameters


defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)



conf = ConfParameters.ConfParameters()

mysql_para = conf.mysql_conf
save_path = conf.save_path
gameName = conf.project_name
currency_list = [conf.currency]
pay_ratio = 100


file_name = save_path + 'modernship_cn_qs_table1.xls' # save
stat_base = mysql_para['stat_base']
stat_pay = mysql_para['stat_pay']
stat_userreg = mysql_para['stat_userreg']
user_active_openid = mysql_para['user_active_openid']
#
wbk = None
db = None
cursor = None

zh_pattern = re.compile(u'[\u4e00-\u9fa5]+')

def contain_zh(word):
    #判断中文
    global zh_pattern
    match = zh_pattern.search(unicode(word))
    return match

def insertXls(datalist,sheet,linenum):
    #按行写入xls
    line = linenum[0]
    for col in range(0,len(datalist)):
        if contain_zh(datalist[col]):
            sheet.write(line,col,unicode(datalist[col]))
        else:
            sheet.write(line,col,datalist[col])
    linenum[0] = line +1
    return

def compute_mau(month):
    global cursor
    global stat_base
    global user_active_openid
    #
    data = 0
    sqlstr = 'select count(distinct openid) from ' + stat_base + '.' + user_active_openid + ' where date like \'' + month + '%\''
    print sqlstr
    cursor.execute(sqlstr)
    alldata = cursor.fetchall()
    if alldata:
        for rec in alldata:
            data = int(rec[0])
            return data
    else:
        print '[Warning]No data found in sql string:',sqlstr

def compute_new(month):
    global cursor
    global stat_userreg
    data = 0
    for i in range(0,10):
        sqlstr = 'select count(distinct openid) from ' + stat_userreg + '.user_register_openid' + str(i) + ' where date like \'' + month + '%\''
        print sqlstr
        cursor.execute(sqlstr)
        alldata = cursor.fetchall()
        if alldata:
            for rec in alldata:
                data = data + int(rec[0])
        else:
            print '[Warning]No data found in sql string:',sqlstr
    return data        


def compute_new_pay(month):
    global cursor
    global stat_pay
    data = 0
    # select count(distinct openid) from (select openid,min(date) as fisrtday from pay_syn_day group by openid)a where fisrtday like '2018-03%';
    sqlstr = 'select count(distinct openid) from (select openid,min(date) as fisrtday from ' + stat_pay + '.pay_syn_day group by openid)a  where fisrtday like \'' + month + '%\''
    print sqlstr
    cursor.execute(sqlstr)
    alldata = cursor.fetchall()
    if alldata:
        for rec in alldata:
            data = int(rec[0])
            return data
    else:
        print '[Warning]No data found in sql string:',sqlstr        

def compute_pay_users(month):
    global cursor
    global stat_pay
    data = 0
    sqlstr = 'select count(distinct openid) from ' + stat_pay + '.pay_syn_day where date like \'' + month + '%\''
    print sqlstr
    cursor.execute(sqlstr)
    alldata = cursor.fetchall()
    if alldata:
        for rec in alldata:
            data = int(rec[0])
            return data
    else:
        print '[Warning]No data found in sql string:',sqlstr        

def compute_money_list(month):
    global cursor
    global stat_pay
    global currency_list
    data = list()
    for currency in currency_list:
        sqlstr = 'select sum(rawmoney/'+ str(pay_ratio) +') from '+ stat_pay + '.pay_syn_day where date like \'' + month + '%\' and currency like \'' + currency + '%\''
        print sqlstr
        cursor.execute(sqlstr)
        alldata = cursor.fetchall()
        if alldata:
            for rec in alldata:
                data.append(float(rec[0]))
        else:
            print '[Warning]No data found in sql string:',sqlstr
    return data        

def compute_reten_list(month):
    global cursor
    global stat_base
    data = list()
    sqlstr = 'select sum(c.R1)/count(c.R1),sum(c.R2)/count(c.R2),sum(c.R3)/count(c.R3),sum(c.R4)/count(c.R4) from (select substr(b.date,1,7) as month, CountP1/CountP0 as R1, CountP2/CountP0 as R2, CountP6/CountP0 as R3, CountP29/CountP0 as R4 from (select date,sum(case period when 0 then Count else 0 end) as CountP0,sum(case period when 1 then Count else 0 end) as CountP1,sum(case period when 2 then Count else 0 end) as CountP2,sum(case period when 6 then Count else 0 end) as CountP6,sum(case period when 29 then Count else 0 end) as CountP29 from (select date,sum(count) as Count,period from '+ stat_base + '.user_reten_openid where date like \''+month+'%\' group by date,period)a group by date)b)c group by c.month'
    print sqlstr
    cursor.execute(sqlstr)
    alldata = cursor.fetchall()
    if alldata:
        for rec in alldata:
            data.append(float(rec[0]))
            data.append(float(rec[1]))
            data.append(float(rec[2]))
            data.append(float(rec[3]))
    else:
        print '[Warning]No data found in sql string:',sqlstr
    return data        

def compute_diamond_list(month):
    sql_str = 'select sum(add_cash),sum(add_diamond),sum(cost_cash),sum(cost_diamond) from user_diamond where date like \''+ month +'%\''
    print(sql_str)
    cursor.execute(sql_str)
    all_data = cursor.fetchall()
    if all_data:
        for rec in all_data:
            return list(rec)

def table1_month(month):
    global gameName
    #month 2018-01
    #月份    游戏名称    月注册账户数    月活跃账户数    月新增注册账户数    月新增付费账户数    月付费账户数    月均每账户充值金额    月付费转化率    充值流水（USD） 充值流水（RMB）    充值消耗比    次日留存（%）    3日留存（%）    7日留存（%）    30日留存（%）
    data_list = list()
    data_list.append(month)
    data_list.append(gameName)
    data_list.append(' ')
    data_list.append(compute_mau(month))
    data_list.append(compute_new(month))
    data_list.append(compute_new_pay(month))
    data_list.append(compute_pay_users(month))
    data_list.append(' ')
    data_list.append(' ')
    data_list = data_list + compute_money_list(month)
    data_list.append(' ')
    data_list = data_list + compute_reten_list(month)
    return data_list


def table3_month(month):
    global gameName
    #month 2018-01
    #月份    游戏名称    月注册账户数    月活跃账户数    月新增注册账户数    月新增付费账户数    月付费账户数    月均每账户充值金额    月付费转化率    充值流水（USD） 充值流水（RMB）    充值消耗比    次日留存（%）    3日留存（%）    7日留存（%）    30日留存（%）
    data_list = list()
    data_list.append(month)
    data_list.append(gameName)
    data_list.append(' ')
    data_list.append(' ')
    data_list.append('钻石')
    data_list.append(' ')
    data_list = data_list + compute_money_list(month)
    data_list.append(' ')
    data_list.append(' ')
    data_list = data_list + compute_diamond_list(month)
    data_list.append(' ')
    data_list.append(' ')
    return data_list


def write_table_1(month_list):
    global currency_list
    #
    # month_list.append('2018-01')
    # month_list.append('2018-02')
    # month_list.append('2018-03')
    # month_list.append('2018-04')
    # month_list.append('2018-05')
    # month_list.append('2018-06')

    head_line  = ['月份','游戏名称','月注册账户','月活跃账户数','月新增注册账户数','月新增付费账户数','月付费账户数','月均每账户充值金额','月付费转化率']
    for currency in currency_list:
        value = '充值金额(' + currency + ')'
        head_line.append(value)
    head_line = head_line + ['充值消耗比','次日留存','三日留存','7日留存','30日留存']

    sheet = wbk.add_sheet(unicode('表1按月汇总数据OPENID'),cell_overwrite_ok=True)
    linenum = [0]
    insertXls(head_line,sheet,linenum)
    for month in month_list:
        data_list = table1_month(month)
        insertXls(data_list,sheet,linenum)


def write_table_2(month_list):
    min_month = '\'' + month_list[0] + '\''
    max_month = '\'' + month_list[len(month_list)-1] + '\''
    # /100 is not necessary for modernship_korea

    head_line = ['月份', '游戏名称', '国家', '渠道', '货币', '月付费账户数', '月付费金额（通用货币）', '月付费金额（原始币种）', '分成比例', '手续费比例']
    sheet = wbk.add_sheet(unicode('表2收入明细'), cell_overwrite_ok=True)
    linenum = [0]
    insertXls(head_line, sheet, linenum)

    sql_cmd = 'select substring(date,1,7) as month, \'\' as game_name,  \'\' as country, channel, substring(currency,1,3) as curr, count(distinct openid), sum(money/'+ str(pay_ratio) +'),sum(rawmoney/'+ str(pay_ratio) +'),\'\' as ratio,\'\' as r2 from ' + stat_pay + '.pay_syn_day group by month,channel,curr having month between ' + min_month + ' and ' + max_month
    print(sql_cmd)
    cursor.execute(sql_cmd)
    all_data = cursor.fetchall()
    if all_data:
        for rec in all_data:
            insertXls(rec, sheet, linenum)


def write_table_3(month_list):
    head_line = ['月份','游戏','国家','渠道','代币','代币兑换率']
    for currency in currency_list:
        value = '充值金额(' + currency + ')'
        head_line.append(value)
    head_line = head_line + ['期初购买代币','期初系统代币','付费钻石增加','免费钻石增加','付费钻石消耗','免费钻石消耗','期末购买代币','期末系统代币']
    sheet = wbk.add_sheet(unicode('表3虚拟货币明细'), cell_overwrite_ok=True)
    linenum = [0]
    insertXls(head_line, sheet, linenum)
    for month in month_list:
        data_list = table3_month(month)
        insertXls(data_list,sheet,linenum)


def execute(month_list):
    global wbk
    global db
    global cursor
    wbk = xlwt.Workbook()

    db = MySQLdb.connect(host=mysql_para['ip'], port=mysql_para['port'], user=mysql_para['users'],
                         passwd=mysql_para['password'], db=mysql_para['stat_base'])
    cursor = db.cursor()

    write_table_1(month_list)
    write_table_2(month_list)
    write_table_3(month_list)

    wbk.save(file_name)
    db.close()

