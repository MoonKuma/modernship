#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : SocketDeleteItem.py
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


class SocketDeleteItem(object):
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

    def get_item_count(self, uid_list, item_id_list):
        # playerinfo,u72339077604641602,48742804
        uid_item_list = list()
        msg = 'Start get_item_count with len(uid)' + str(len(uid_list)) + ' and itemid len=' + str(len(item_id_list))
        success = 0
        failure = 0
        self.easy_log.info(msg)
        for uid in uid_list:
            self.sid += 1
            cmd = 'playerinfo,u' + str(uid) + ',' + str(self.sid) + '\n'
            self.easy_log.info(cmd)
            try:
                socket_res = self.easy_sock.send_cmd_message(cmd, self.sk)
                msg = str(socket_res)
                self.easy_log.info(msg)
                item = (socket_res["items".encode('utf-8')]).decode('utf-8')
                item_array = item.split("|")
                # self.easy_log.info(str(item_array))
                for each_item in item_array:
                    each_item = str(each_item.decode('utf-8'))
                    if not each_item.__contains__(";"):
                        continue
                    sing_item = each_item.split(";")[0]
                    count = each_item.split(";")[1]
                    if sing_item in item_id_list:
                        key = uid + ',' + sing_item + ',' + count
                        uid_item_list.append(key)
                    success += 1
            except:
                self.easy_log.error(cmd)
                failure += 1
        msg = 'Finish querying sever with [' + str(success) + '] success and [' + str(failure) + '] failure'
        self.easy_log.info(msg)
        print str(uid_item_list)
        return uid_item_list

    def delete_by_uid_list(self, uid_item_list):
        # delitem,u72339077604641602,20036,11,0530280
        msg = 'Start querying sever:delete_by_uid_dict with len(uid_dict)' + str(len(uid_item_list))
        success = 0
        failure = 0
        self.easy_log.info(msg)
        for uid_str in uid_item_list:
            self.sid += 1
            cmd = 'delitem,u' + uid_str + ',' + str(self.sid) + '\n'
            self.easy_log.info(cmd)
            try:
                socket_res = self.easy_sock.send_cmd_message(cmd, self.sk)
                msg = str(socket_res)
                self.easy_log.info(msg)
                success += 1
            except:
                self.easy_log.error(cmd)
                failure += 1
        msg = 'Finish querying sever:delete_by_uid_dict with [' + str(success) + '] success and [' + str(failure) + '] failure'
        self.easy_log.info(msg)


# test main
if __name__ == '__main__':
    # get uid list
    file_name = sys.argv[1]
    item_id_list = ['64031', '64013','64005','64008','64009','62007','50040','40123','40122','40120','40119']
    uid_list = list()
    file_open = open(file_name, 'r')
    for line in file_open.readlines():
        line = line.strip()
        if line not in uid_list:
            uid_list.append(line)
    sock_obj = SocketDeleteItem()
    msg = 'Length uid_list = ' + str(len(uid_list))
    uid_item_list = sock_obj.get_item_count(uid_list, item_id_list)
    sock_obj.delete_by_uid_list(uid_item_list)




