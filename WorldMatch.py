#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : WorldMatch.py
# @Author: MoonKuma
# @Date  : 2018/9/6
# @Desc  : world match related data (rank, shop and others)

import conf.ConfParameters as ConfParameters
import util.DateList as DateList
import util.EasyXls as EasyXls
import util.UserInfoCheck as UserInfoCheck
import util.ReadTable as ReadTable
import os
import MySQLdb
import xlwt


class WorldMatch:

    def __init__(self):
        conf = ConfParameters.ConfParameters().log_conf
        self.log_path = conf['game_log_path_current']
        self.world_path = conf['world_log_path']
        self.start_date = '2018-08-17'
        self.end_date = '2018-08-26'
        self.period = '1'
        # data
        # {uid:{world:world,rank:rank,item1:count1,other_attr...}}
        self.top_map = dict()
        self.item_list = ['50064', '50023', '50060', '50044', '50045', '50046', '50047', '40049', '50030']
        self.item_dict = dict()  # here keep the maximum item count which users are capable to exchange
        self.__load_item()
        # initial mysql-db
        mysql_para = ConfParameters.ConfParameters().mysql_conf
        self.db = MySQLdb.connect(mysql_para['ip'], mysql_para['users'], mysql_para['password'], mysql_para['stat_base'])
        self.stat_pay = mysql_para['stat_pay']
        self.stat_base = mysql_para['stat_base']
        self.user_reg = mysql_para['stat_userreg']
        self.user_active_openid = mysql_para['user_active_openid']
        self.cursor = self.db.cursor()
        # initial xls writer
        self.wbk = xlwt.Workbook()
        self.xls_writer = EasyXls.EasyXls()
        # user info check
        self.user_info = UserInfoCheck.UserInfoCheck(self.cursor)

    def __load_item(self):
        file_name = ConfParameters.ConfParameters().conf_path + 'WorldMatch.txt'
        self.item_dict = ReadTable.ReadTable(file_name).read_table_file()

    def set_date(self, date_tuple):
        self.start_date = date_tuple[0]
        self.end_date = date_tuple[1]

    def set_period(self, period):
        self.period = str(period)

    def load_top_map(self):
        # grep -h -s 'ASW_KO' /data/stat/Log_common/msworld*_*|awk -F ',' '{OFS=",";if($6<=32)print $6,$4}'
        # grep -h -s 'ASW_CHAMPION' /data/stat/Log_common/msworld*_*|awk -F ',' '{OFS=",";print 1,$4}'
        data_map = self.top_map
        # {uid:{rank:rank,world_type:world_type}}
        date_list = DateList.DateList().get_date_list(self.start_date, self.end_date)
        file_str = ''
        for date in date_list:
            file_name = ' ' + self.world_path.replace('$dateString$', date)
            file_str += file_name
        # others
        # cmd = 'grep -h -s \'ASW_KO\'' + file_str + '|awk -F \',\' \'{OFS=\",\";if($6<=32)print $4,$2,$6}\''
        cmd = 'grep -h -s \'ASW_KO\'' + file_str + '|awk -F \',\' \'{OFS=\",\";print $4,$2,$6}\''
        print cmd
        val = os.popen(cmd).readlines()
        for line in val:
            line = line.strip()
            array = line.split(',')
            uid = array[0]
            world_type = array[1]
            rank = array[2]
            if uid not in data_map.keys():
                data_map[uid] = dict()
                data_map[uid]['world_type'] = world_type
                data_map[uid]['rank'] = rank
        # champion
        cmd = 'grep -h -s \'ASW_CHAMPION\'' + file_str + '|awk -F \',\' \'{OFS=\",\";print $4,$2,1}\''
        print cmd
        val = os.popen(cmd).readlines()
        for line in val:
            line = line.strip()
            array = line.split(',')
            uid = array[0]
            world_type = array[1]
            rank = array[2]
            if uid not in data_map.keys():
                data_map[uid] = dict()
                data_map[uid]['world_type'] = world_type
                data_map[uid]['rank'] = rank
        return data_map

    def show_top_map(self, *file_name):
        data_map = self.top_map
        if len(data_map) == 0:
            print 'No top map exist, please load first'
            return
        for uid in data_map.keys():
            world_type = data_map[uid]['world_type']
            rank = data_map[uid]['rank']
            str_wri = world_type + ',' + rank + ',' + uid
            print str_wri
        if len(file_name) == 1:
            file_op = open(file_name, 'w')
            for uid in data_map.keys():
                world_type = data_map[uid]['world_type']
                rank = data_map[uid]['rank']
                str_wri = world_type + ',' + rank + ',' + uid + '\n'
                print str_wri
                file_op.write(str_wri)

    def top_shop_buy(self):
        data_map = self.top_map
        # {uid:{world:world,rank:rank,item1:count1,item2:count2...}}
        if len(data_map) == 0:
            print 'No top map exist, please load first'
            return
        date_list = DateList.DateList().get_date_list(self.start_date, self.end_date)
        file_str = ''
        for date in date_list:
            file_name = ' ' + self.log_path.replace('$dateString$', date)
            file_str += file_name
        cmd = 'grep -h -s \',AddProp,\' ' + file_str + '|awk -F \',\' \'{OFS=\",\";if($15==80)print $3,$16,$17}\'|awk -F \',\' \'{sum[$1\",\"$2]=sum[$1\",\"$2]+$3} END {OFS=\",\";for(i in sum)print i,sum[i]}\''
        print cmd
        val = os.popen(cmd).readlines()
        for line in val:
            line = line.strip()
            array = line.split(',')
            uid = array[0]
            item = array[1]
            count = array[2]
            if uid in data_map.keys():
                data_map[uid][item] = count
        return data_map

    def load_data(self):
        self.load_top_map()
        self.top_shop_buy()

    def write_xls(self, sheet, *is_percent):
        data_map = self.top_map
        if len(data_map) == 0:
            print 'No top map exist, please load first'
            return
        line_num = [0]
        head_line = ['uid', '大区', '排名']
        # head_line = ['uid', '大区', '排名', '渠道', '服务器', '注册日期', '最后登录日期', '付费合计']
        for item in self.item_list:
            head_line.append(item)
        self.xls_writer.insert_xls(head_line, sheet, line_num)
        for uid in data_map.keys():
            data_list = list()
            data_list.append(uid)
            data_list.append(data_map[uid]['world_type'])
            data_list.append(int(data_map[uid]['rank']))
            # reg_info = self.user_info.get_reg_info(self.stat_base, self.user_active_openid, uid)
            # data_list.append(reg_info['channel'])
            # data_list.append(reg_info['zoneid'])
            # data_list.append(reg_info['min_date'])
            # data_list.append(reg_info['max_date'])
            # total_money = self.user_info.get_total_payment(self.stat_pay, uid)
            # data_list.append(total_money)
            for item in self.item_list:
                value = int(data_map[uid].setdefault(item, 0))
                if len(is_percent) == 1 and is_percent[0] == 1:
                    refer_key = item + '|' + str(data_map[uid]['rank'])
                    refer_value = float(self.item_dict.setdefault(refer_key, '0.0'))
                    if int(refer_value) != 0:
                        value = value/refer_value
                data_list.append(value)
            self.xls_writer.insert_xls(data_list, sheet, line_num)

    def execute(self):
        # sheet 1 : 兑换数量
        # sheet 1 : 兑换比例
        self.load_data()
        file_name = ConfParameters.ConfParameters().save_path + 'WorldMatch_' + self.start_date + '_' + self.end_date + '.xls'
        sheet_name = '兑换数量'
        sheet1 = self.xls_writer.new_sheet(sheet_name, self.wbk)
        self.write_xls(sheet1)
        # sheet_name = '兑换比例'
        # sheet2 = self.xls_writer.new_sheet(sheet_name, self.wbk)
        # self.write_xls(sheet2, 1)
        self.db.close()
        self.wbk.save(file_name)
        return


if __name__ == '__main__':
    # execute
    WorldMatch().execute()
