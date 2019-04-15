#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : ShipMissileInfo.py
# @Author: MoonKuma
# @Date  : 2018/9/12
# @Desc  : Ship and missile info for modernship players
#          telnet ip port
#          startRecordPlayerDetail,a,Unix_time_stamp1,Unix_time_stamp2,sid
#          eg : telnet 10.135.126.46 12001
#          eg : startRecordPlayerDetail,a,1543395600,1543482000,1
#

import util.LogQuery as LogQuery
import conf.ConfParameters as ConfParameters
import os
import MySQLdb
import sys


class ShipMissileInfo:

    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.ship_log_key = 'shipInfoTotal'
        self.ship_table_name = 'user_ship_info'
        self.missile_table_name = 'user_missile_info'
        self.missile_log_key = 'missleInfoTotal'
        # initial mysql-db
        mysql_para = ConfParameters.ConfParameters().mysql_conf
        self.db = MySQLdb.connect(mysql_para['ip'], mysql_para['users'], mysql_para['password'], mysql_para['stat_base'])
        self.cursor = self.db.cursor()

    def __set_date(self, date_tuple):
        if len(date_tuple) == 2:
            self.start_date = date_tuple[0]
            self.end_date = date_tuple[1]

    def __query_log_file(self, log_key):
        file_str = LogQuery.LogQuery(self.start_date, self.end_date).log_file_str()
        cmd = 'grep -h -s -E \'' + log_key + '\' ' + file_str + '|awk -F \',\' \'{OFS=\",\";print $3,$14,$2,$12,$15}\'|awk -F \',\' \'{last[$1\",\"$2\",\"$3]=$4\",\"$5} END {OFS=\",\";for(i in last)print i,last[i]}\''
        print cmd
        val = os.popen(cmd).readlines()
        return val

    def __sql_value_str(self, value_list):
        value_str = '\'' + str(value_list[0]) + '\''
        if len(value_list) > 1 :
            for value_index in range(1, len(value_list)):
                value_str = value_str + ',\'' + str(value_list[value_index]) + '\''
        return value_str

    def batch_commit(self, sql_str_list, cursor, db):
        print '[Batch Commit] Start committing to db with ' + str(len(sql_str_list)) + ' commend lines'
        cycle = 100
        count = 0
        list_len = len(sql_str_list)
        for line in sql_str_list:
            count += 1
            cursor.execute(line)
            if count % cycle == 0 or count >= list_len:
                db.commit()
        db.commit()

    def load_ship_table(self):
        table_name = self.ship_table_name
        sql_str = 'CREATE TABLE IF NOT EXISTS `' + table_name + '`(`date` date NOT NULL,`uid` bigint(20) NOT NULL,`vip_level` int(11) NOT NULL,`zoneid` int(11) NOT NULL,`channel` varchar(16) NOT NULL,`ship_id` int(11) NOT NULL,`ship_star` int(11) NOT NULL,`ship_grade` int(11) NOT NULL,PRIMARY KEY (`date`,`uid`,`ship_id`), KEY `i_zoneid` (`zoneid`), KEY `i_channel` (`channel`), KEY `i_vip_level` (`vip_level`))'
        print sql_str
        self.cursor.execute(sql_str)
        self.db.commit()
        sql_str = 'DELETE FROM `' + table_name + '` WHERE DATE=\'' + self.end_date + '\''
        print sql_str
        self.cursor.execute(sql_str)
        self.db.commit()
        data_file = self.__query_log_file(self.ship_log_key)
        data_dict = dict()
        date = self.end_date
        for line in data_file:
            line = line.strip()
            array = line.split(',')
            uid = array[0]
            channel = array[1]
            zoneid = array[2]
            vip_level = array[3]
            ship_info = array[4].split('|')
            for ship in ship_info:
                ship = ship.strip()
                ship_array = ship.split(';')
                ship_id = ship_array[0]
                ship_star = ship_array[1]
                ship_grade = ship_array[2]
                key = date + '|' + uid + '|' + ship_id # Caution: using - as splitter will accidentally split date(2018-09-19) as well
                data_dict[key] = dict()
                data_dict[key]['channel'] = channel
                data_dict[key]['zoneid'] = zoneid
                data_dict[key]['vip_level'] = vip_level
                data_dict[key]['ship_star'] = ship_star
                data_dict[key]['ship_grade'] = ship_grade
        sql_str_list = list()
        for key in data_dict.keys():
            key_array = key.split('|')
            insert_date = key_array[0]
            uid= key_array[1]
            ship_id = key_array[2]
            channel = data_dict[key]['channel']
            zoneid = data_dict[key]['zoneid']
            vip_level = data_dict[key]['vip_level']
            ship_star = data_dict[key]['ship_star']
            ship_grade = data_dict[key]['ship_grade']
            value_list = [insert_date, uid, vip_level, zoneid, channel, ship_id, ship_star, ship_grade]
            value_str = self.__sql_value_str(value_list)
            sql_str = 'INSERT INTO `' + table_name + '` (date,uid,vip_level,zoneid,channel,ship_id,ship_star,ship_grade) values (' + value_str + ')'
            sql_str_list.append(sql_str)
        self.batch_commit(sql_str_list, self.cursor, self.db)

    def load_missile_table(self):
        table_name = self.missile_table_name
        sql_str = 'CREATE TABLE IF NOT EXISTS `' + table_name + '`(`date` date NOT NULL,`uid` bigint(20) NOT NULL,`vip_level` int(11) NOT NULL,`zoneid` int(11) NOT NULL,`channel` varchar(16) NOT NULL,`missile_id` int(11) NOT NULL,`missile_count` int(11) NOT NULL,PRIMARY KEY (`date`,`uid`,`missile_id`), KEY `i_zoneid` (`zoneid`), KEY `i_channel` (`channel`))'
        print sql_str
        self.cursor.execute(sql_str)
        self.db.commit()
        sql_str = 'DELETE FROM `' + table_name + '` WHERE DATE=\'' + self.end_date + '\''
        print sql_str
        self.cursor.execute(sql_str)
        self.db.commit()
        data_file = self.__query_log_file(self.missile_log_key)
        data_dict = dict()
        date = self.end_date
        for line in data_file:
            line = line.strip()
            array = line.split(',')
            uid = array[0]
            channel = array[1]
            zoneid = array[2]
            vip_level = array[3]
            if array[4] == '':
                continue
            missile_info = array[4].split('|')
            for ship in missile_info:
                ship = ship.strip()
                ship_array = ship.split(';')
                ship_id = ship_array[0]
                ship_count = ship_array[1]
                key = date + '|' + uid + '|' + ship_id  # Caution: using - as splitter will accidentally split date(2018-09-19) as well
                data_dict[key] = dict()
                data_dict[key]['channel'] = channel
                data_dict[key]['zoneid'] = zoneid
                data_dict[key]['vip_level'] = vip_level
                data_dict[key]['ship_count'] = ship_count
        sql_str_list = list()
        for key in data_dict.keys():
            key_array = key.split('|')
            insert_date = key_array[0]
            uid = key_array[1]
            ship_id = key_array[2]
            channel = data_dict[key]['channel']
            zoneid = data_dict[key]['zoneid']
            vip_level = data_dict[key]['vip_level']
            ship_count = data_dict[key]['ship_count']
            value_list = [insert_date, uid, vip_level, zoneid, channel, ship_id, ship_count]
            value_str = self.__sql_value_str(value_list)
            sql_str = 'INSERT INTO `' + table_name + '` (date,uid,vip_level,zoneid,channel,missile_id,missile_count) values (' + value_str + ')'
            sql_str_list.append(sql_str)
        self.batch_commit(sql_str_list, self.cursor, self.db)

    def execute(self):
        self.load_ship_table()
        self.load_missile_table()


# test main
if __name__ == '__main__':
    start_date = None
    end_date = None
    try:
        start_date = sys.argv[1]
        end_date = sys.argv[2]
    except:
        print 'Require date input in form like: 2018-10-18 2018-10-19'
    if start_date is not None and end_date is not None:
        ShipMissileInfo(start_date, end_date).execute()













