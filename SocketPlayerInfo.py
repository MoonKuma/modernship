#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : SocketPlayerInfo.py
# @Author: MoonKuma
# @Date  : 2018/10/29
# @Desc  : check player info from a given list

import conf.ConfParameters as ConfParameters
import util.EasySocketCmd as EasySocketCmd
import socket
import copy
from util.Tools import try_b64_decode



class SocketPlayerInfo(object):
    def __init__(self):
        # initial socket
        self.sk_conf = ConfParameters.ConfParameters().socket_conf
        self.sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ip_port = (self.sk_conf['ip'], self.sk_conf['port'])
        self.sk.settimeout(2)
        self.sk.connect(ip_port)
        # local parameter
        self.receive_list = ['openid', 'region', 'channel', 'level', 'viplevel', 'logintime', 'cash', 'recharge', 'max_power', 'name', 'mbname']
        self.write_list = copy.copy(self.receive_list)
        self.easy_sock = EasySocketCmd.EasySocketCmd()
        self.count = 0

    def set_receive_list(self, new_receive_list):
        self.receive_list = new_receive_list
        return

    def set_write_list(self, new_write_list):
        self.write_list = new_write_list
        return

    def get_player_info(self, uid_list):
        result_dict = dict()
        msg = 'Start querying sever with ' + str(len(uid_list))
        print(msg)
        for uid in uid_list:
            if uid in result_dict.keys():
                continue
            result_dict[uid] = dict()
            cmd = 'playerinfo,u' + str(uid) + ',' + str(self.count) + '\n'
            socket_res = dict()
            try:
                socket_res = self.easy_sock.send_cmd_message(cmd, self.sk)
            except:
                pass
            if len(socket_res)>0:
                for key in self.receive_list:
                    result_dict[uid][key] = socket_res[key]
        msg = 'Finish querying sever with ' + str(len(result_dict.keys()))
        print(msg)
        return result_dict

    def test_report(self, res_dict, write_file):
        file_open = open(write_file, 'w')
        try:
            str_wri = 'uid'
            for key in self.write_list:
                    str_wri = str_wri + ',' + key
            str_wri += '\n'
            file_open.write(str_wri)
            for uid in res_dict.keys():
                str_wri = uid
                for key in self.write_list:
                    str_wri = str_wri + ',' + try_b64_decode(res_dict[uid].setdefault(key, ' '))
                str_wri += '\n'
                file_open.write(str_wri)
        finally:
            file_open.close()


# test main
if __name__ == '__main__':
    # get uid list
    uid_list = list()
    uid_dict = dict()
    file_open = open('/data/tmpStatistic/specious_uid_20181029.txt', 'r')
    try:
        for line in file_open.readlines():
            line = line.strip()
            array = line.split('\t')
            uid = array[0]
            if uid == 'uid':
                continue
            if uid not in uid_list:
                uid_list.append(uid)
                uid_dict[uid] = dict()
                max_time = array[5]
                min_time = array[6]
                uid_dict[uid]['max_time'] = max_time
                uid_dict[uid]['min_time'] = min_time
    finally:
        file_open.close()

    new_socket = SocketPlayerInfo()
    res_dict = new_socket.get_player_info(uid_list)
    for uid in res_dict.keys():
        res_dict[uid]['max_time'] = uid_dict[uid].setdefault('max_time', ' ')
        res_dict[uid]['min_time'] = uid_dict[uid].setdefault('min_time', ' ')
    write_list = new_socket.write_list
    write_list.append('max_time')
    write_list.append('max_time')
    write_file_name = ConfParameters.ConfParameters().save_path + 'test_socket_playerinfo.txt'
    new_socket.test_report(res_dict, write_file_name)


