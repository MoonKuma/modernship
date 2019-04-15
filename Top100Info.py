#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : Top100Info.py
# @Author: MoonKuma
# @Date  : 2018/9/20
# @Desc  : Top 100 payment users, basic information, ship/missile information, diamond information, diamond details and so on


import util.EasyXls as EasyXls
import util.EasyMysql as EasyMysql
import util.UserInfoCheck as UserInfoCheck
import util.ReadTable as ReadTable
import conf.ConfParameters as ConfParameters
import MySQLdb
import xlwt


class Top100Info:

    def __init__(self):
        # conf path
        self.conf_path = ConfParameters.ConfParameters().conf_path
        # initial mysql-db
        mysql_para = ConfParameters.ConfParameters().mysql_conf
        self.db = MySQLdb.connect(mysql_para['ip'], mysql_para['users'], mysql_para['password'], mysql_para['stat_base'])
        self.cursor = self.db.cursor()
        self.stat_pay = mysql_para['stat_pay']
        self.stat_base = mysql_para['stat_base']
        self.user_active_openid = mysql_para['user_active_openid']
        # initial xls writer
        self.wbk = xlwt.Workbook()
        self.xls_writer = EasyXls.EasyXls()
        self.style = xlwt.XFStyle()
        self.style.borders = self.xls_writer.borders
        # local parameter
        self.compute_date = '2018-09-13'
        self.limit_num = '100'
        self.eighteen_ships = self.__list_to_str([1001, 1002, 1003, 2001, 2002, 2003, 2004, 2005, 3001, 4001, 4002, 4003, 4004, 3004, 4030])
        self.sixteen_ships = self.__list_to_str([1004, 1005, 1006, 1007, 2007, 4005, 4008, 4009, 4013, 3005, 4031])
        self.fifteen_ships = self.__list_to_str([1008, 2006, 2008, 2009, 2010, 2011, 3002, 3003, 4006, 4007, 4010, 4011, 4012, 5012, 5013, 5014, 5015, 5016, 5017, 5018, 5019, 5020, 5021, 5022, 5025])
        file_name = self.conf_path + 'ship_exclusive.txt'
        self.ship_table = ReadTable.ReadTable(file_name).read_table_file()

    def __find_attribute(self, ship_id, key_name):
        # 'ship_rank','ship_name','exclusive','exclusive_name'
        key = str(ship_id) + '|' + key_name
        return self.ship_table.setdefault(key, ship_id)

    def __list_to_str(self, list_name):
        new_list = list()
        for item in list_name:
            new_list.append(str(item))
        return new_list

    def set_top_num(self, new_num):
        self.limit_num = new_num

    def get_top_list(self):
        top_list = list()
        sql_str = 'select uid,ceil(sum(money/100)) from ' + self.stat_pay + '.pay_syn_day where date<\'' + self.compute_date + '\' group by uid order by sum(money) desc limit ' + self.limit_num
        print sql_str
        self.cursor.execute(sql_str)
        all_data = self.cursor.fetchall()
        if all_data:
            for rec in all_data:
                uid = str(rec[0])
                if uid not in top_list:
                    top_list.append(uid)
        return top_list

    def get_basic_info(self, top_list):
        user_info_check = UserInfoCheck.UserInfoCheck(self.cursor)
        user_basic_info = dict()
        for uid in top_list:
            if uid not in user_basic_info.keys():
                user_basic_info[uid] = dict()
            user_info = user_info_check.get_reg_info(self.stat_base, self.user_active_openid, uid)
            user_basic_info[uid]['channel'] = user_info['channel']
            user_basic_info[uid]['zoneid'] = user_info['zoneid']
            user_basic_info[uid]['min_date'] = user_info['min_date']
            user_basic_info[uid]['max_date'] = user_info['max_date']
            user_basic_info[uid]['payment'] = user_info_check.get_total_payment(self.stat_pay, uid)
        return user_basic_info

    def get_diamond_info(self, top_list):
        top_str = EasyMysql.EasyMysql().sql_value_str(top_list)
        sql_str = 'select date,uid,sum(cost_diamond + cost_cash) from user_diamond where date < \'' + self.compute_date + '\' and uid in (' + top_str + ') group by date,uid'
        date_list = list()
        uid_diamond = dict()
        print sql_str
        self.cursor.execute(sql_str)
        all_data = self.cursor.fetchall()
        if all_data:
            for rec in all_data:
                date = str(rec[0])
                if date not in date_list:
                    date_list.append(date)
                uid = str(rec[1])
                cost = int(rec[2])
                if uid not in uid_diamond.keys():
                    uid_diamond[uid] = dict()
                uid_diamond[uid][date] = cost
        date_list = sorted(date_list)
        return [uid_diamond, date_list]

    def get_ship_info(self, top_list, ship_list):
        easy_sql = EasyMysql.EasyMysql()
        top_str = easy_sql.sql_value_str(top_list)
        ship_str = easy_sql.sql_value_str(ship_list)
        trans_dict = dict()
        missile_list = list()
        ship_star_result = dict()
        ship_grade_result = dict()
        for ship_id in ship_list:
            missile_id = self.__find_attribute(ship_id, 'exclusive')
            ship_name = self.__find_attribute(ship_id, 'ship_name')
            trans_dict[ship_id] = ship_name
            trans_dict[missile_id] = '[导]' + ship_name  # missile also use the name of its corresponding ship
            missile_list.append(missile_id)
        missile_str = easy_sql.sql_value_str(missile_list)
        x_list = ship_list + missile_list
        # ship_star
        sql_str = 'select ship_id,uid,max(ship_star) from user_ship_info where date = \'' + self.compute_date + '\' and uid in (' + top_str + ') and ship_id in (' + ship_str + ') group by ship_id,uid'
        print sql_str
        self.cursor.execute(sql_str)
        all_data = self.cursor.fetchall()
        if all_data:
            for rec in all_data:
                ship_id = str(rec[0])
                uid = str(rec[1])
                ship_star = int(rec[2])
                if uid not in ship_star_result.keys():
                    ship_star_result[uid] = dict()
                ship_star_result[uid][ship_id] = ship_star
        # ship_grade
        sql_str = 'select ship_id,uid,max(ship_grade) from user_ship_info where date = \'' + self.compute_date + '\' and uid in (' + top_str + ') and ship_id in (' + ship_str + ') group by ship_id,uid'
        print sql_str
        self.cursor.execute(sql_str)
        all_data = self.cursor.fetchall()
        if all_data:
            for rec in all_data:
                ship_id = str(rec[0])
                uid = str(rec[1])
                ship_grade = int(rec[2])
                if uid not in ship_grade_result.keys():
                    ship_grade_result[uid] = dict()
                ship_grade_result[uid][ship_id] = ship_grade
        # missile_count
        sql_str = 'select missile_id,uid,max(missile_count) from user_missile_info where date = \'' + self.compute_date + '\' and uid in (' + top_str + ') and missile_id in (' + missile_str + ') group by missile_id,uid'
        print sql_str
        self.cursor.execute(sql_str)
        all_data = self.cursor.fetchall()
        if all_data:
            for rec in all_data:
                missile_id = str(rec[0])
                uid = str(rec[1])
                missile_count = int(rec[2])
                if uid not in ship_grade_result.keys():
                    ship_grade_result[uid] = dict()
                if uid not in ship_star_result.keys():
                    ship_star_result[uid] = dict()
                ship_grade_result[uid][missile_id] = missile_count
                ship_star_result[uid][missile_id] = missile_count
        return [ship_grade_result, ship_star_result, x_list, trans_dict]

    def get_diamond_detail_info(self, top_list):
        # initial mysql-db big_data_test(this is a special version, only acceptable for modernship cn)
        easy_sql = EasyMysql.EasyMysql()
        mysql_para_bd_test = ConfParameters.ConfParameters().mysql_conf_bd_test
        db_bd_test = MySQLdb.connect(mysql_para_bd_test['ip'], mysql_para_bd_test['users'], mysql_para_bd_test['password'], mysql_para_bd_test['stat_base'])
        cursor_bd_test = db_bd_test.cursor()
        top_str = easy_sql.sql_value_str(top_list)
        sql_str = 'select uid,date,moneytype,sum(cash+diamond) from diamond_pay_users where uid in (' + top_str + ') group by uid,date,moneytype'
        cursor_bd_test.execute(sql_str)
        all_data = cursor_bd_test.fetchall()
        date_list = list()
        money_type_list = list()
        result_dict = dict()
        if all_data:
            for rec in all_data:
                uid = str(rec[0])
                date = str(rec[1])
                if date not in date_list:
                    date_list.append(date)
                money_type = str(rec[2])
                if money_type not in money_type_list:
                    money_type_list.append(money_type)
                if uid not in result_dict.keys():
                    result_dict[uid] = dict()
                if money_type not in result_dict[uid].keys():
                    result_dict[uid][money_type] = dict()
                result_dict[uid][money_type][date] = int(rec[3])
        date_list = sorted(date_list)
        money_type_list = sorted(money_type_list, key=lambda x: int(x))
        db_bd_test.close()
        return [money_type_list, date_list, result_dict]

    def write_data_sheet(self, top_list, info_dict, data_dict, data_axis, sheet_name, head_name, *trans_dict):
        sheet = self.xls_writer.new_sheet(sheet_name, self.wbk)
        sheet.col(0).width = 256 * 20
        line_num = [0]
        name_list = [sheet_name]
        self.xls_writer.insert_xls_style(name_list, sheet, line_num, self.style)
        line_num[0] = line_num[0] + 2
        head_line = [head_name, '排名', '渠道', '服务器', '注册时间', '最后登录时间', '合计付费金额']
        for x in data_axis:
            if len(trans_dict) == 0:
                head_line.append(x)
            else:
                head_line.append(trans_dict[0].setdefault(x, x))
        self.xls_writer.insert_xls_style(head_line, sheet, line_num, self.style)
        rank = 1
        for uid in top_list:
            data_line = list()
            data_line.append(uid)
            data_line.append(rank)
            rank += 1
            if uid not in info_dict.keys():
                data_line = data_line + [' ', ' ', ' ', ' ', ' ']
            else:
                data_line.append(info_dict[uid]['channel'])
                data_line.append(info_dict[uid]['zoneid'])
                data_line.append(info_dict[uid]['min_date'])
                data_line.append(info_dict[uid]['max_date'])
                data_line.append(info_dict[uid]['payment'])
            for x in data_axis:
                if uid not in data_dict.keys():
                    data_line.append(' ')
                else:
                    data_line.append(data_dict[uid].setdefault(x, ' '))
            self.xls_writer.insert_xls_style(data_line, sheet, line_num, self.style)
        return 1

    def diamond_xls(self):
        top_list = self.get_top_list()
        basic_info = self.get_basic_info(top_list)
        diamond_info, date_list = self.get_diamond_info(top_list)
        sheet_name = '付费TOP100钻石'
        head_name = 'UID-日钻石消耗'
        self.write_data_sheet(top_list, basic_info, diamond_info, date_list, sheet_name, head_name)
        return 1

    def ship_xls(self, ship_list, name):
        top_list = self.get_top_list()
        basic_info = self.get_basic_info(top_list)
        ship_grade_result, ship_star_result, x_list, trans_dict = self.get_ship_info(top_list, ship_list)
        print '***len(ship_grade_result):', len(ship_grade_result),'***len(ship_star_result):', len(ship_star_result)
        sheet_name = 'TOP100_' + str(name) + '船星级与导弹'
        head_name = 'UID-' + str(name) + '船星级-导弹数量'
        self.write_data_sheet(top_list, basic_info, ship_star_result, x_list, sheet_name, head_name, trans_dict)
        sheet_name = 'TOP100_' + str(name) + '船阶级与导弹'
        head_name = 'UID-' + str(name) + '船阶级-导弹数量'
        self.write_data_sheet(top_list, basic_info, ship_grade_result, x_list, sheet_name, head_name, trans_dict)

    def diamond_detail_xls(self):
        self.set_top_num(20)
        top_list = self.get_top_list()

        return

    def execute(self):
        file_name = ConfParameters.ConfParameters().save_path + 'Top100_ship_' + self.compute_date + '.xls'
        # self.diamond_xls()
        self.ship_xls(self.eighteen_ships, '18')
        self.ship_xls(self.sixteen_ships, '16')
        self.ship_xls(self.fifteen_ships, '15')
        self.wbk.save(file_name)
        self.db.close()

    def execute_diamond_detail(self):
        file_name = ConfParameters.ConfParameters().save_path + 'Top100_ship_' + self.compute_date + '.xls'
        self.diamond_detail_xls()
        self.wbk.save(file_name)
        self.db.close()

# test main
if __name__ == '__main__':
    Top100Info().execute()













