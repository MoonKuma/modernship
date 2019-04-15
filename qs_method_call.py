#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : qs_method_call.py
# @Author: MoonKuma
# @Date  : 2019/1/4
# @Desc  :

import time
import traceback

from qs.qs_table1 import execute

month_list = ['2018-03','2018-04','2018-05','2018-06','2018-07','2018-08','2018-09','2018-10','2018-11','2018-12']

module_list = [execute]

for module in module_list:
    now_time = time.time()
    try:
        msg = 'Try running ' + module.__name__
        print(msg)
        module(month_list)
        msg = 'Finish running ' + module.__name__ + ',time cost:' + str(time.time() - now_time)
        print(msg)
    except Exception:
        msg = 'Error in running' + module.__name__+ ',time cost:' + str(time.time() - now_time)
        print(msg)
        print traceback.format_exc()

