#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : UserRetenVipLevel.py
# @Author: MoonKuma
# @Date  : 2018/9/14
# @Desc  : User reten data grouped by vip and levels

import MySQLdb
import conf.ConfParameters as ConfParameters
import datetime


class UserRetenVipLevel:

    def __init__(self):
        # initial mysql-db
        mysql_para = ConfParameters.ConfParameters().mysql_conf
        self.db = MySQLdb.connect(mysql_para['ip'], mysql_para['users'], mysql_para['password'], mysql_para['stat_base'])
        self.cursor = self.db.cursor()
        # local parameter
        self.date_start = '2018-08-28'
        self.date_end = '2018-09-23'
        self.date_length = 4
        self.channel = ''

    def __reform_date(self, date_str):
        return (datetime.datetime.strptime(date_str, '%Y-%m-%d')).strftime('%Y%m%d')

    def __draw_date(self, date_str):
        return datetime.datetime.strptime(date_str, '%Y-%m-%d')

    def create_table(self):
        channel = ''
        if self.channel != '':
            channel = '_' + self.channel
        table_name = 'user_reten_lv_vip' + channel
        sql_str = 'CREATE TABLE IF NOT EXISTS `' + table_name + '`(`date` date NOT NULL,`level` int(11) NOT NULL,`vip_level` int(11) NOT NULL,`activeUsers` int(11) NOT NULL,`retenUsers` int(11) NOT NULL,PRIMARY KEY (`date`,`level`,`vip_level`))'
        print sql_str
        self.cursor.execute(sql_str)
        self.db.commit()
        return table_name

    def load_table(self):
        channel = self.channel
        date_start = self.date_start
        date_end = self.date_end
        date_length = self.date_length
        where_channel = ''
        if channel != '':
            where_channel = ' where channel = ' + channel
            channel = '_' + channel
        table_name = 'user_reten_lv_vip' + channel
        date_list = list()
        maximum_legal_date = (datetime.datetime.now() - datetime.timedelta(date_length)).strftime('%Y-%m-%d')
        d1 = datetime.datetime.strptime(date_start, '%Y-%m-%d')
        if date_end > maximum_legal_date:
            print 'date_end is larger than the maximum date:', maximum_legal_date, ',date_end is modified automatically'
            date_end = maximum_legal_date
        d2 = datetime.datetime.strptime(date_end, '%Y-%m-%d')
        day_diff = (d2 - d1).days
        while day_diff >= 0:
            date_list.append(d1.strftime('%Y-%m-%d'))
            d1 = d1 + datetime.timedelta(days=1)
            day_diff = (d2 - d1).days
        for date_index in range(0, len(date_list)):
            date = date_list[date_index]
            compute_table = 'user_active_' + self.__reform_date(date)
            refer_date_list = list()
            for k in range(1, date_length):
                refer_date = (self.__draw_date(date) + datetime.timedelta(days=k)).strftime('%Y-%m-%d')
                refer_table = 'user_active_' + self.__reform_date(refer_date)
                refer_date_list.append(refer_table)
            refer_str = 'select uid from ' + refer_date_list[0]
            for i in range(1, len(refer_date_list)):
                refer_str = refer_str + ' union select uid from ' + refer_date_list[i]
            sql_str = 'DELETE FROM ' + table_name + ' WHERE date = \'' + date + '\''
            self.cursor.execute(sql_str)
            self.db.commit()
            sql_str = 'INSERT INTO ' + table_name + '(date,level,vip_level,activeUsers,retenUsers) select \'' + date + '\' as date, level,vip_level,count(uid) as activeUsers,sum(case when uid in (' + refer_str + ') then 1 else 0 end) as retenUsers from ' + compute_table + ' ' + where_channel + ' group by level,vip_level'
            self.cursor.execute(sql_str)
            self.db.commit()

    def execute(self, start_date, end_date):
        self.date_start = start_date
        self.date_end = end_date
        self.create_table()
        self.load_table()


# test main
if __name__ == '__main__':
    UserRetenVipLevel().execute('2018-09-08', '2018-09-22')
