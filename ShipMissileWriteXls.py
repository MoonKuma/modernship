#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : ShipMissileWriteXls.py
# @Author: MoonKuma
# @Date  : 2018/9/13
# @Desc  : Write ship and missile data into .xls files

import MySQLdb
import xlwt
import conf.ConfParameters as ConfParameters
import util.EasyXls as EasyXls
import util.ReadTable as ReadTable
import util.EasyMysql as EasyMysql
import sys

class ShipMissileWriteXls:

    def __init__(self, compute_date):
        self.compute_date = compute_date
        # conf path
        self.conf_path = ConfParameters.ConfParameters().conf_path
        # initial mysql-db
        mysql_para = ConfParameters.ConfParameters().mysql_conf
        self.db = MySQLdb.connect(mysql_para['ip'], mysql_para['users'], mysql_para['password'], mysql_para['stat_base'])
        self.cursor = self.db.cursor()
        # initial xls writer
        self.wbk = xlwt.Workbook()
        self.xls_writer = EasyXls.EasyXls()
        self.borders = xlwt.Borders()
        self.style = xlwt.XFStyle()
        self.__load_borders()
        self.style.borders = self.borders
        # local parameter
        self.ship_table = dict()
        self.read_table()
        self.ship_table_name = 'user_ship_info'
        self.missile_table_name = 'user_missile_info'
        self.eighteen_ships = [1001, 1002, 1003, 2001, 2002, 2003, 2004, 2005, 3001, 4001, 4002, 4003, 4004, 3004, 4030]
        self.sixteen_ships = [1004, 1005, 1006, 1007, 2007, 4005, 4008, 4009, 4013, 3005, 4031]
        self.fifteen_ships = [1008, 2006, 2008, 2009, 2010, 2011, 3002, 3003, 4006, 4007, 4010, 4011, 4012, 5012, 5013, 5014, 5015, 5016, 5017, 5018, 5019, 5020, 5021, 5022, 5025]
        self.zoneid_list_0512 = [10001, 40001, 20001, 40002, 20002, 30001, 20003, 30002, 20004, 40003, 10002, 20005, 30003, 20006, 20007, 30004, 20008, 20009, 20010, 30005, 20011, 20012, 20013, 20014, 30006, 40004, 10003, 20015, 10004, 20016, 20017, 40005, 20018, 10005, 20019, 20020]
        self.zoneid_list_0731 = [20021, 30007, 20022, 20023, 20024, 40006, 20025, 20026, 20027, 10006, 20028, 30008, 20029, 20030, 40007, 20031, 20032, 20033, 20034]
        self.zoneid_list_0913 = [20035, 30009, 40008, 10007, 20036, 20037, 20038, 20039, 20040, 20041, 50001, 20042, 10008, 20043, 55001, 20044, 20045, 20046, 30010, 40009, 20047, 55002, 20048, 55003, 55004]

    def read_table(self):
        file_name = self.conf_path + 'ship_exclusive.txt'
        self.ship_table = ReadTable.ReadTable(file_name).read_table_file()

    def __load_borders(self):
        self.borders.left = 1
        self.borders.right = 1
        self.borders.top = 1
        self.borders.bottom = 1
        self.borders.bottom_colour = 0x3A

    def __find_attribute(self, ship_id, key_name):
        key = str(ship_id) + '|' + key_name
        return self.ship_table.setdefault(key, ship_id)

    def __load_attribute(self, result_list, key_name, key_value):
        return

    def __compute_sql_and_load_xls(self, sql_str, sheet, line_num, head_name, *is_trans):
        print sql_str
        self.cursor.execute(sql_str)
        all_data = self.cursor.fetchall()
        result = dict()
        vip_list = list()
        type_list = list()
        if all_data:
            for rec in all_data:
                vip = str(rec[0])
                if vip not in vip_list:
                    vip_list.append(vip)
                type_name = str(rec[1])
                if type_name not in type_list:
                    type_list.append(type_name)
                count = float(rec[2])
                key = vip + '|' + type_name
                if key not in result.keys():
                    result[key] = count
        if len(is_trans) == 2:
            index_list = is_trans[1]
            type_list = sorted(type_list, key=lambda x: index_list.index(x))
        else:
            type_list = sorted(type_list, key=lambda x: int(x))
        vip_list = sorted(vip_list, key=lambda x: int(x))
        head_list = [head_name]
        if len(is_trans) == 0:
            head_list = head_list + type_list
        elif len(is_trans) == 1:
            for type_id in type_list:
                head_list.append(self.__find_attribute(type_id, is_trans[0]))
        self.xls_writer.insert_xls_style(head_list, sheet, line_num, self.style)
        for vip in vip_list:
            data_list = [vip]
            for type_name in type_list:
                key = vip + '|' + type_name
                value = result.setdefault(key, ' ')
                data_list.append(value)
            self.xls_writer.insert_xls_style(data_list, sheet, line_num, self.style)
        return

    def compute_total_sheet(self, zoneid_list, ship_list, sheet_name):
        ship_str = EasyMysql.EasyMysql().sql_value_str(ship_list)
        zone_str = ''
        if len(zoneid_list) > 0:
            zone_str = EasyMysql.EasyMysql().sql_value_str(zoneid_list)
        sheet = self.xls_writer.new_sheet(sheet_name, self.wbk)
        sheet.col(0).width = 256 * 20
        line_num = [0]
        name_list = [sheet_name]
        self.xls_writer.insert_xls_style(name_list, sheet, line_num, self.style)
        line_num[0] = line_num[0] + 2
        # compute users
        head_name = 'VIP-船-拥有人数'
        sql_str = 'select vip_level,ship_id,count(distinct uid) from user_ship_info where ship_id in (' + ship_str + ') and date=\'' + self.compute_date +'\' and uid not in (select uid from user_ban_statistic) '
        if zone_str != '':
            sql_str = sql_str + 'and zoneid in (' + zone_str + ')'
        sql_str = sql_str + ' group by vip_level,ship_id;'
        self.__compute_sql_and_load_xls(sql_str, sheet, line_num, head_name, 'ship_name')
        line_num[0] = line_num[0] + 2
        # compute average stars
        head_name = 'VIP-船-平均星级'
        sql_str = 'select vip_level,ship_id,format(sum(ship_star)/count(distinct uid),2) from user_ship_info where ship_id in (' + ship_str + ') and date=\'' + self.compute_date +'\' and uid not in (select uid from user_ban_statistic) '
        if zone_str != '':
            sql_str = sql_str + 'and zoneid in (' + zone_str + ')'
        sql_str = sql_str + ' group by vip_level,ship_id;'
        self.__compute_sql_and_load_xls(sql_str, sheet, line_num, head_name, 'ship_name')
        line_num[0] = line_num[0] + 2
        # compute average grades
        head_name = 'VIP-船-平均阶级'
        sql_str = 'select vip_level,ship_id,format(sum(ship_grade)/count(distinct uid),2) from user_ship_info where ship_id in (' + ship_str + ') and date=\'' + self.compute_date +'\' and uid not in (select uid from user_ban_statistic) '
        if zone_str != '':
            sql_str = sql_str + 'and zoneid in (' + zone_str + ')'
        sql_str = sql_str + ' group by vip_level,ship_id;'
        self.__compute_sql_and_load_xls(sql_str, sheet, line_num, head_name, 'ship_name')
        # compute missile count
        # head_name = 'VIP-对应导弹-数量合计'
        # missile_list = list()

        return 1

    def compute_certain_ship(self, ship_id, zoneid_list):
        zone_str = ''
        if len(zoneid_list) > 0:
            zone_str = EasyMysql.EasyMysql().sql_value_str(zoneid_list)
        ship_name = self.__find_attribute(ship_id, 'ship_name')
        sheet_name = 'Ship_' + str(ship_id) + '_' + ship_name
        sheet = self.xls_writer.new_sheet(sheet_name, self.wbk)
        sheet.col(0).width = 256*20
        line_num = [0]
        # ship name
        name_list = [ship_name, str(ship_id)]
        self.xls_writer.insert_xls_style(name_list, sheet, line_num, self.style)
        line_num[0] = line_num[0] + 2
        # start computing ship-stars
        head_name = 'VIP-船星级'
        sql_str = 'select vip_level,ship_star,count(distinct uid) from user_ship_info where ship_id=\'' + ship_id + '\' and date=\''+ self.compute_date +'\' and uid not in (select uid from user_ban_statistic) '
        if zone_str != '':
            sql_str = sql_str + 'and zoneid in (' + zone_str + ')'
        sql_str = sql_str + ' group by vip_level,ship_star;'
        self.__compute_sql_and_load_xls(sql_str, sheet,  line_num, head_name)
        line_num[0] = line_num[0] + 2
        head_name = 'VIP-船阶级'
        sql_str = 'select vip_level,ship_grade,count(distinct uid) from user_ship_info where ship_id=\'' + ship_id + '\' and date=\''+ self.compute_date +'\' and uid not in (select uid from user_ban_statistic) '
        if zone_str != '':
            sql_str = sql_str + 'and zoneid in (' + zone_str + ')'
        sql_str = sql_str + ' group by vip_level,ship_grade;'
        self.__compute_sql_and_load_xls(sql_str, sheet, line_num, head_name)
        line_num[0] = line_num[0] + 2
        head_name = 'VIP-船对应导弹数量'
        missile_id = self.__find_attribute(ship_id, 'exclusive')
        sql_str = 'select vip_level,missile_count,count(distinct uid) from user_missile_info where missile_id=\'' + missile_id + '\' and date=\''+ self.compute_date +'\' and uid not in (select uid from user_ban_statistic) '
        if zone_str != '':
            sql_str = sql_str + 'and zoneid in (' + zone_str + ')'
        sql_str = sql_str + ' group by vip_level,missile_count;'
        self.__compute_sql_and_load_xls(sql_str, sheet, line_num, head_name)

    def execute(self, zoneid_list, name):
        file_name = ConfParameters.ConfParameters().save_path + name + '_ship_16_info_' + self.compute_date + '.xls'
        ship_list = self.sixteen_ships
        for ship_id in ship_list:
            self.compute_certain_ship(str(ship_id), zoneid_list)
        self.wbk.save(file_name)

        self.wbk = xlwt.Workbook()
        file_name = ConfParameters.ConfParameters().save_path + name + '_ship_18_info_' + self.compute_date + '.xls'
        ship_list = self.eighteen_ships
        for ship_id in ship_list:
            self.compute_certain_ship(str(ship_id), zoneid_list)
        self.wbk.save(file_name)

        self.wbk = xlwt.Workbook()
        file_name = ConfParameters.ConfParameters().save_path + name + '_ship_15_info_' + self.compute_date + '.xls'
        ship_list = self.fifteen_ships
        for ship_id in ship_list:
            self.compute_certain_ship(str(ship_id), zoneid_list)
        self.wbk.save(file_name)
        self.db.close()

    def execute_total(self, zoneid_list, name):
        file_name = ConfParameters.ConfParameters().save_path + name + '_ship_total_info_' + self.compute_date + '.xls'
        ship_list = self.fifteen_ships
        sheet_name = '15评级船'
        self.compute_total_sheet(zoneid_list, ship_list, sheet_name)
        ship_list = self.sixteen_ships
        sheet_name = '16评级船'
        self.compute_total_sheet(zoneid_list, ship_list, sheet_name)
        ship_list = self.eighteen_ships
        sheet_name = '18评级船'
        self.compute_total_sheet(zoneid_list, ship_list, sheet_name)
        self.wbk.save(file_name)


# test main
if __name__ == '__main__':
    #
    start_date = None
    try:
        start_date = sys.argv[1]
    except:
        print 'Require date input in form like: 2018-10-18 2018-10-19'
    if start_date is not None :
        zoneid_tmp = list()
        ShipMissileWriteXls(start_date).execute_total(zoneid_tmp, '_total_')
        ShipMissileWriteXls(start_date).execute(zoneid_tmp, '_total_')





