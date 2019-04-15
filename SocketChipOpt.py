#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : SocketChipOpt.py
# @Author: MoonKuma
# @Date  : 2018/10/29
# @Desc  : # chipOpt,uid,opt(del/dall),val(no use when opt is to delete),chipUid(0 for delete all),sid
# delete certain chip: chipOpt,u72339073312121768,del,0,4298137411,22222
# delete all chips: chipOpt,u72339073312121768,dall,0,0,2222

import conf.ConfParameters as ConfParameters
import util.EasySocketCmd as EasySocketCmd
import util.EasyLog as EasyLog
import socket
import sys


class SocketChipOpt(object):
    def __init__(self):
        # initial socket
        self.sk_conf = ConfParameters.ConfParameters().socket_conf_xf
        self.sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ip_port = (self.sk_conf['ip'], self.sk_conf['port'])
        self.sk.settimeout(2)
        self.sk.connect(ip_port)
        # log module
        self.easy_log = EasyLog.EasyLog(self.__class__.__name__, 'socket')
        # local parameter
        self.easy_sock = EasySocketCmd.EasySocketCmd()
        # sid
        self.sid = 1000

    def uid_chip_out_total(self, uid_list):
        msg = 'Start querying sever with ' + str(len(uid_list))
        success = 0
        failure = 0
        self.easy_log.info(msg)
        for uid in uid_list:
            self.sid += 1
            cmd = 'chipOpt,u' + str(uid) + ',dall,0,0,' + str(self.sid) + '\n'
            self.easy_log.info(cmd)
            try:
                socket_res = self.easy_sock.send_cmd_message(cmd, self.sk)
                msg = str(socket_res)
                self.easy_log.info(msg)
                success += 1
            except:
                self.easy_log.error(cmd)
                failure += 1
        msg = 'Finish querying sever with [' + str(success) + '] success and [' + str(failure) + ']'
        self.easy_log.info(msg)


# test main
if __name__ == '__main__':
    # get uid list
    file_name = sys.argv[1]
    uid_list = list()
    file_open = open(file_name, 'r')
    for line in file_open.readlines():
        line = line.strip()
        if line not in uid_list:
            uid_list.append(line)
    sock_obj = SocketChipOpt()
    msg = 'Length uid_list = ' + str(len(uid_list)) + ' ,continue?(y/n)'
    receive = raw_input(msg)
    if receive.lower() == 'y':
        sock_obj.uid_chip_out_total(uid_list)




