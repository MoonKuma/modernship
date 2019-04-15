#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : EasySocketBatch.py
# @Author: MoonKuma
# @Date  : 2018/11/29
# @Desc  : long connection with one listener keep monitoring sk.receive
# ( This may be not that safe, java has more sophistic way in realizing this )


# this is where python3 is required,
# threading.semaphore do not accept "timeout"
# ,yet semaphore of multiprocessing is not capable to be used here, for (all threads in) one processing share one semaphore
# which means one timeout all timeout
# besides, multiprocessing.Process(target=func, argv = (arg, )) run funcs in different processing,
# where variables are not directly shared
# in all, avoid using multiprocessing
# other component inside threading is not suitable for this mission too (like Condition/Event)
# fail to work on Python2,use python 3 instead


import socket
import threading
import multiprocessing
import json
import EasyLog
import time
import sys
# print sys.version_info.major


# # this part is to allow applying multiprocessing of current module(need to be pickled/serialized before multiprocessing)
'''
import copy_reg
import types
def _pickle_method(m):
    if m.im_self is None:
        return getattr, (m.im_class, m.im_func.func_name)
    else:
        return getattr, (m.im_self, m.im_func.func_name)


copy_reg.pickle(types.MethodType, _pickle_method)
# 
'''


# # this part is an example for singleton, which is not very much useful here for the connections ceased as with the request
'''
class EasySocketBatch(object):

    # example of singleton
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(EasySocketBatch, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.handler_map = dict()
        self.log = EasyLog.EasyLog(self.__class__.__name__, 'socket')
        pass

    def get_socket_connection(self, ip, port):
        key = str(ip) + str(port)
        if key in self.handler_map.keys():
            return self.handler_map[key]
        else:
            self.__new_connection(key, ip, port)
            return self.handler_map[key]

    def report(self):
        print(self.handler_map)

    def __new_connection(self, key, ip, port):
        msg = 'Adding a new connection with ' + str(ip) + ':' + str(port)
        self.log.info(msg)
        new_net = NetConnection(ip, port)
        self.handler_map[key] = new_net
'''

# NetConnection is applied for sending through multiple threads and receiving simultaneously

'''
class NetConnection(object):
    def __init__(self, ip, port):
        msg = 'Adding a new connection with ' + str(ip) + ':' + str(port)
        self.log = EasyLog.EasyLog(self.__class__.__name__, 'socket')
        self.log.info(msg)
        self.sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ip_port = (ip, int(port))
        self.sk.connect(ip_port)
        self.sk.setblocking(0)
        # quit
        self.quit_signal = dict()
        # request_dict
        self.request_dict = dict()
        # result_dict
        self.result_dict = dict()
        # sid
        self.sid = 1
        # receiving thread(this should be initialed in the last place) and quit by hand
        self.receive_thread = threading.Thread(target=self.__receive_connect, args=(self.sk,))
        self.receive_thread.start()
        # semaphore
        self.sem_lock = threading.Semaphore(1)

    def send_cmd(self, cmd):
        cmd = cmd.strip()
        sid_int = self.sid
        cs = ConnSem(sid_int, cmd)
        self.sem_lock.acquire()
        self.result_dict[sid_int] = cs
        self.sem_lock.release()
        current_sid = str(self.sid)
        cmd = cmd + ',' + current_sid + '\n'
        # self.log.info(cmd)
        self.request_dict[current_sid] = cmd
        self.sid += 1
        self.sk.send(cmd)
        if cs.try_acquire():
            # self.log.info(str(cs.get_json))
            # time.sleep(1) # use for testify
            return cs.get_json()
        # receive
        # start_receive = time.time()
        # while not self.result_dict[sid_int]: # directly request from the dict structure will block the threading
        #     # time.sleep(0.1)
        #     if time.time() - start_receive > 5:
        #         print 'No result for sid:', current_sid
        #         break

    def get_all_result(self):
        return self.result_dict

    def get_all_request(self):
        return self.request_dict

    def quit_receive(self):
        self.quit_signal['isQuit'] = 1

    def __receive_connect(self, sk):
        total_length = 0
        current_string = ''
        waiting_head = 1
        time_start = time.time()
        while True:
            try:
                data = sk.recv(512)
                # print(data)
                [current_string, waiting_head, total_length] = self.__compute_string(data, current_string, waiting_head, total_length)
            except Exception:
                pass
            if 'isQuit' in self.quit_signal.keys():
                msg = 'Quit receiving as requested, total receiving time:' + str(time.time() - time_start)
                print(msg)
                break
        self.sk.close()

    def __compute_string(self, string_data, current_string, waiting_head, total_length):
        current_string = current_string + string_data
        if waiting_head == 1:
            string_length = current_string[0:current_string.find('{')]
            total_length = int(string_length, 16)
            waiting_head = 0
        try_patch = current_string[current_string.find("{"): current_string.find("}")+1]
        if len(try_patch) >= total_length:
            result = json.loads(try_patch)
            sid = int(result['sid'])
            self.result_dict[sid].set_json(result)
            current_string = current_string[current_string.find("}")+1:]
            waiting_head = 1
        return [current_string, waiting_head, total_length]



class ConnSem(object):
    def __init__(self, sid, cmd):
        self.sid = sid
        self.cmd = cmd
        # self.local_sem = multiprocessing.Semaphore(0) # not ok, all threads in one processing share multiprocessing.Semaphore (time out at the same time)
        # self.local_sem = threading.Lock() # not ok, python 2 offer no timeout solution for Lock
        # self.local_sem = threading.Semaphore() # not ok, python 2 offer no timeout solution for Semaphore
        self.local_sem = threading.Condition() #
        # self.local_sem = threading.Event()
        self.json_result = dict()
        pass

    def set_json(self, json_dict):
        # print('Now setting', json_dict)
        self.json_result = json_dict
        self.notify_lock()
        # print('After setting', self.json_result)

    def get_json(self):
        # print('Now getting', self.json_result)
        return self.json_result

    def notify_lock(self):
        self.local_sem.acquire()
        self.local_sem.notify()
        self.local_sem.release()

    def release_lock(self):
        # print('Now releasing',  self.json_result)
        self.local_sem.release()

    def try_acquire(self):
        # print('Now acquiring', self.json_result)
        time_start = time.time()
        # hold here
        self.local_sem.acquire()
        acq = self.local_sem.wait(timeout=4)
        self.local_sem.release()
        msg = 'Acquire state:' + str(acq) + ', at time cost:' + str(time.time() - time_start)
        print('After acquiring', self.json_result)
        print(msg)
        return True

    # validity testify
    @staticmethod
    def test_thread_func(cs, seconds):
        time.sleep(seconds)
        cs.set_json({cs.sid: "success"})

    @staticmethod
    def test_exe():
        time_in = time.time()
        cs1 = ConnSem(1, 1)
        t1 = threading.Thread(target=ConnSem.test_thread_func, args=(cs1,3,))
        t1.start()

        cs = ConnSem(2, 1)
        t = threading.Thread(target=ConnSem.test_thread_func, args=(cs, 10,))
        t.start()

        if cs1.try_acquire():
            print cs1.get_json()
        if cs.try_acquire():
            print cs.get_json()
        time_out = time.time() - time_in
        print 'time out:', time_out

#
'''

# test ConnSem
if __name__ == '__main__':
    pass
    # ConnSem.test_exe()