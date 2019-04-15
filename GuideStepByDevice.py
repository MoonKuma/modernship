#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : GuideStepByDevice.py
# @Author: MoonKuma
# @Date  : 2018/9/3
# @Desc  : Guide step passing rate for different device type

import conf.ConfParameters as ConfParameters
import util.DateList as DateList
import util.EasyXls as EasyXls
import os
import MySQLdb
import xlwt


class GuideStepByDevice:
    def __init__(self):
        self.final_step = '1000601'
        self.channel = '1007'
        self.start_date = '2018-08-20'
        self.end_date = '2018-09-03'
        # initial mysql-db
        mysql_para = ConfParameters.ConfParameters().mysql_conf
        self.db = MySQLdb.connect(mysql_para['ip'], mysql_para['users'], mysql_para['password'], mysql_para['stat_userreg'])
        self.cursor = self.db.cursor()
        # initial xls writer
        self.wbk = xlwt.Workbook()
        return

    def set_channel(self, channel):
        self.channel = channel

    def set_date(self, date_tuple):
        self.start_date = date_tuple[0]
        self.end_date = date_tuple[1]

    # check if new device-code
    def check_old_device(self, device_id, date_str):
        sql_str = 'select count(deviceid) from (select * from user_device0 where date<\'' + date_str + '\' and deviceid=\''+device_id+'\''
        for i in range(1, 10):
            sql_str = sql_str + ' union select * from user_device'+str(i)+' where date<\'' + date_str + '\' and deviceid=\''+device_id+'\''
        sql_str = sql_str + ') as a'
        self.cursor.execute(sql_str)
        all_data = self.cursor.fetchall()
        result = 0
        if all_data:
            for rec in all_data:
                result = int(rec[0])
        return result

    # check guide step pass rate for given day
    def deviceid_pass_per_date(self, date_str):
        # 72510902066221321,861457033750324,1,1
        # {device_id : {enter:enter, passed:passed}}
        result_map = dict()
        log_path = ConfParameters.ConfParameters().log_conf['game_log_path_current']
        log_path = log_path.replace('$dateString$', date_str)
        cmd = 'grep -h -s -E \'DceGuide|Register\' ' + log_path + '|' 'awk -F \',\' \'{if($4==\"Register\" && $14==\"' + self.channel + '\"){device[$3]=$16};if($4==\"DceGuide\" && $14==\"' + self.channel + '\"){guideenter[$3]=1};if($4==\"DceGuide\" && $15==\"' + self.final_step + '\" && $14==\"' + self.channel + '\"){guidepass[$3]=1}} END {OFS=\",\";for(i in device)print i,device[i],guideenter[i]==\"\"?0:1,guidepass[i]==\"\"?0:1}\''
        print cmd
        val = os.popen(cmd).readlines()
        for line in val:
            line = line.strip()
            array = line.split(',')
            deviceid = str(array[1])
            entered = int(array[2])
            passed = int(array[3])
            key = deviceid  # _ is not acceptable for there may be '_' in device type
            if key not in result_map.keys():
                result_map[key] = dict()
                result_map[key]['entered'] = entered
                result_map[key]['passed'] = passed
        return result_map

    def deviceid_to_devicetype(self, date_str):
        # 863064037545227,HUAWEI_HUAWEI_MLA-AL10,1,0
        # {device_id : {device-type:device-type,web_response:web_response,game_connect:game_connect}}
        result_map = dict()
        today = DateList.DateList().get_today()
        if today == date_str:
            log_path = ConfParameters.ConfParameters().log_conf['stat_log_path'] + 'event.log'
        else:
            log_path = ConfParameters.ConfParameters().log_conf['stat_log_path'] + 'event.log.' + date_str
        cmd = 'grep \'context:0_\' ' + log_path + '|grep \'chanel:' + self.channel + '\'|awk -F \',\' \'{OFS=\":\";print $4,$5,$8}\'|awk -F \':\' \'{device[$4]=$6;enter[$4]=1;if($2==\"0_gameConnect_\"){pass[$4]=1};} END {OFS=\",\";for(i in device)print i,device[i],enter[i],pass[i]==\"\"?0:1}\''
        print cmd
        val = os.popen(cmd).readlines()
        for line in val:
            line = line.strip()
            array = line.split(',')
            deviceid = str(array[0])
            device_type = str(array[1])
            entered = int(array[2])
            passed = int(array[3])
            key = deviceid  # _ is not acceptable for there may be '_' in device type
            if key not in result_map.keys():
                result_map[key] = dict()
                result_map[key]['device_type'] = device_type
                result_map[key]['entered'] = entered
                result_map[key]['passed'] = passed
        return result_map

    def join_maps(self, date_str):
        guide_map = self.deviceid_pass_per_date(date_str)
        print date_str, ',len(guide_map):',len(guide_map)
        event_map = self.deviceid_to_devicetype(date_str)
        print date_str, ',len(event_map):', len(event_map)
        # {device_type:{sum(web_resp):sum(web_resp),sum(game_conn):sum(game_conn),sum(guide):sum(guide),sum(pass_guide):sum(pass_guide)}}
        result_map = dict()
        for device_id in event_map.keys():
            if self.check_old_device(device_id, date_str):
                continue
            device_type = event_map[device_id]['device_type']
            if device_type not in result_map.keys():
                result_map[device_type] = dict()
                result_map[device_type]['web_resp'] = 0
                result_map[device_type]['game_conn'] = 0
                result_map[device_type]['guide'] = 0
                result_map[device_type]['pass_guide'] = 0
            result_map[device_type]['web_resp'] = result_map[device_type].setdefault('web_resp', 0) + event_map[device_id]['entered']
            result_map[device_type]['game_conn'] = result_map[device_type].setdefault('game_conn', 0) + event_map[device_id]['passed']
            if device_id in guide_map.keys():
                result_map[device_type]['guide'] = result_map[device_type].setdefault('guide', 0) + guide_map[device_id]['entered']
                result_map[device_type]['pass_guide'] = result_map[device_type].setdefault('pass_guide', 0) + guide_map[device_id]['passed']
        return result_map

    def run_date_list(self):
        date_list = DateList.DateList().get_date_list(self.start_date, self.end_date)
        sheet_name = self.start_date + '_' + self.end_date
        sheet = self.wbk.add_sheet(unicode(sheet_name), cell_overwrite_ok=True)
        xls_writer = EasyXls.EasyXls()
        head_line = ['设备类型', '新增设备数', '通过启动加载项设备数', '开启新手引导设备数', '通过新手引导设备数', '启动加载项通过率', '新手引导通过率']
        line_num = [0]
        xls_writer.insert_xls(head_line, sheet, line_num)
        total_result = dict()
        device_list = list()
        for date in date_list:
            tmp_map = self.join_maps(date)
            for device in tmp_map.keys():
                if device not in device_list:
                    device_list.append(device)
                if device not in total_result.keys():
                    total_result[device] = dict()
                total_result[device]['web_resp'] = total_result[device].setdefault('web_resp',0) + tmp_map[device]['web_resp']
                total_result[device]['game_conn'] = total_result[device].setdefault('game_conn', 0) + tmp_map[device]['game_conn']
                total_result[device]['guide'] = total_result[device].setdefault('guide', 0) + tmp_map[device]['guide']
                total_result[device]['pass_guide'] = total_result[device].setdefault('pass_guide', 0) + tmp_map[device]['pass_guide']
        device_list = sorted(device_list, key=lambda x: -1*total_result[x]['web_resp'])
        for device in device_list:
            web_resp = total_result[device].setdefault('web_resp',0)
            game_conn = total_result[device].setdefault('game_conn', 0)
            guide = total_result[device].setdefault('guide', 0)
            pass_guide = total_result[device].setdefault('pass_guide', 0)
            rate1 = 0
            rate2 = 0
            if web_resp > 0:
                rate1 = str(int(1000*game_conn/web_resp)/10.0) + '%'
            if guide > 0:
                rate2 = str(int(1000*pass_guide/guide)/10.0) + '%'
            data_list = [device, web_resp, game_conn, guide, pass_guide, rate1, rate2]
            xls_writer.insert_xls(data_list, sheet, line_num)

    def test_run(self):
        file_name = ConfParameters.ConfParameters().save_path + 'DeviceEventGuide_' + self.channel + '_' + self.start_date + '_' + self.end_date + '.xls'
        self.run_date_list()
        self.db.close()
        self.wbk.save(file_name)


# test main
if __name__ == '__main__':
    GuideStepByDevice().test_run()










