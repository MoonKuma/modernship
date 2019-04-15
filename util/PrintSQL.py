#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : PrintSQL.py
# @Author: MoonKuma
# @Date  : 2019/1/4
# @Desc  : print out sql in a excel sheet



def print_sql(sql,cursor,sheet,linenum):

    print(sql)

    cursor.execute(sql)
    all_data = cursor.fetchall()

    if all_data:
        for rec in all_data:
            pass
    else:
        print '[Warning]No data found in sql string:', sqlstr
