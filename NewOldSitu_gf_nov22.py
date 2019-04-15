#!/usr/bin/env python
# -*- coding: utf-8 -*-






import conf.ConfParameters as ConfParameters
import util.DateList as DateList
import util.EasyXls as EasyXls
import os
import MySQLdb
import xlwt
import sys
import calendar
import datetime




class NewOldSituation():
    def __init__(self):
        self.channel = ''
        #olduser
        self.totaldict = dict()
        self.peopledict = dict()
        self.paydict = dict()
        self.moneydict = dict()

        self.stayratio = dict()
        self.payratio = dict()
        #newuser
        self.newnumdict=dict()
        # self.new_firstdaydict=dict()
        # self.new_sevendaydict = dict()

        self.viplist=["0","1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16","17","18","19","20","21"]
        # initial mysql-db
        mysqlStatInfo = {'host': '10.66.127.43', 'port': 3306, 'user': 'root', 'passwd': 'r00tr00t'}

        self.db = MySQLdb.connect(host=mysqlStatInfo['host'], port=mysqlStatInfo['port'], user=mysqlStatInfo['user'],
                             passwd=mysqlStatInfo['passwd'], db='modernship_gf_stat_base', charset='utf8')

        self.cursor = self.db.cursor()
        # initial xls writer
        self.wbk = xlwt.Workbook()
        self.sheet = ''
        # self.itemlist=[30,31,32,33,47,48,49,50,53,34,35,36,37,38,39,40,41,42,43,44,45]
        self.itemlist = [80,81]
        self.itembuyratio=dict()
        self.itemavgtimes=dict()
        self.itembuypeople=dict()
        self.activepeople=dict()
        return

    def allchannel(self):
        self.channel=''


    def formalchannel(self):
        self.channel = 'and channel not in (1099, 109902, 109903, 1105, 1098, 109802, 1100, 1104, 1101,1099,1098,1100,1101,12003,109802,1102,1103,1104,1104,1104,1104,1104,1104,1104,1104,1104,109902,109903,1104,1104,1105,109902,109906,109913,109907,109911,109910,1200,1200,1200,1200,1200,1200,1200,1200,1200,1200,1200,1200,1098,109914,1100)'
        self.zoneid = '$2<50000 &&'

    def yiyouchannel(self):
        self.channel = 'and channel in (1099, 109902, 109903,1098, 109802,1099,1098,109802,109902,109903,109902,109906,109913,109907,109911,109910,1098,109914)'
        self.zoneid = '($2>50000 && $2<55000) &&'

    def jinyouchannel(self):
        self.channel = 'and channel in (1100,1104,1101,1200,1105)'
        self.zoneid = '$2>55000 &&'
####olduser
    def lost_ratio(self):
        self.begindate = datetime.datetime.strptime(sys.argv[1],'%Y-%m-%d')
        self.enddate = datetime.datetime.strptime(sys.argv[2],'%Y-%m-%d')
        self.datelist = []
        while self.begindate < self.enddate - datetime.timedelta(days=7):
            self.totaldict[self.begindate.strftime('%Y-%m-%d')] = dict()
            self.peopledict[self.begindate.strftime('%Y-%m-%d')] = dict()
            sqlstr='select c.vip_level,c.total,d.reten,concat(round((c.total-d.reten)/c.total*100,2),"%") as lostratio from (select vip_level,count(distinct(uid)) as total from user_active_extend where date=\"'+self.begindate.strftime('%Y-%m-%d')+'\" and regdate<=\"'+(self.begindate-datetime.timedelta(days=7)).strftime('%Y-%m-%d')+'\" and uid not in (select uid from modernship_stat_busi.uid_block_list)'+self.channel+' group by vip_level) as c left join (select b.vip_level,count(b.uid) as reten from (select distinct(uid) as uid from user_active where date between \"'+(self.begindate+datetime.timedelta(days=1)).strftime('%Y-%m-%d')+'\" and \"'+(self.begindate+datetime.timedelta(days=7)).strftime('%Y-%m-%d')+'\" and uid in (select uid from user_active_extend where date=\"'+self.begindate.strftime('%Y-%m-%d')+'\" and regdate<=\"'+(self.begindate-datetime.timedelta(days=7)).strftime('%Y-%m-%d')+'\") and uid not in (select uid from modernship_stat_busi.uid_block_list)'+self.channel+') as a inner join (select uid,vip_level from user_active where date=\"'+self.begindate.strftime('%Y-%m-%d')+'\") as b on a.uid=b.uid group by b.vip_level) as d on c.vip_level=d.vip_level;'

            self.cursor.execute(sqlstr)
            alldata = self.cursor.fetchall()
            if alldata:
                for rec in alldata:
                    viplevel = str(rec[0])
                    lastratio = rec[3]
                    num = rec[1]
                    self.totaldict[self.begindate.strftime('%Y-%m-%d')][viplevel] = lastratio
                    self.peopledict[self.begindate.strftime('%Y-%m-%d')][viplevel] = num
            self.datelist.append(self.begindate.strftime('%Y-%m-%d'))
            self.begindate += datetime.timedelta(days=1)

    def pay_ratio(self):
        self.begindate = datetime.datetime.strptime(sys.argv[1],'%Y-%m-%d')
        self.enddate = datetime.datetime.strptime(sys.argv[2],'%Y-%m-%d')
        self.datelist = []
        while self.begindate < self.enddate:
            self.paydict[self.begindate.strftime('%Y-%m-%d')] = dict()
            self.moneydict[self.begindate.strftime('%Y-%m-%d')] = dict()
            sqlstr = 'select c.vip_level,c.total,d.paynum,concat(round(d.paynum/c.total*100,2),"%"),d.money from(select vip_level,count(distinct(uid)) as total from user_active_extend where date=\"'+self.begindate.strftime('%Y-%m-%d')+'\" and regdate<=\"'+(self.begindate-datetime.timedelta(days=7)).strftime('%Y-%m-%d')+'\" and uid not in (select uid from modernship_stat_busi.uid_block_list) '+self.channel+'group by vip_level) as c left join(select b.vip_level,count(a.uid) as paynum,sum(a.money) as money from(select uid,sum(money/100) as money from pay_syn_day where date=\"'+self.begindate.strftime('%Y-%m-%d')+'\"'+self.channel+' group by uid) as a inner join(select uid,vip_level from user_active_extend where date=\"'+self.begindate.strftime('%Y-%m-%d')+'\" and regdate<=\"'+(self.begindate-datetime.timedelta(days=7)).strftime('%Y-%m-%d')+'\")as b on a.uid=b.uid group by b.vip_level) as d on c.vip_level=d.vip_level;'
            self.cursor.execute(sqlstr)
            alldata = self.cursor.fetchall()
            if alldata:
                for rec in alldata:
                    viplevel = str(rec[0])
                    payratio = rec[3]
                    money = rec[4]
                    self.paydict[self.begindate.strftime('%Y-%m-%d')][viplevel] = payratio
                    self.moneydict[self.begindate.strftime('%Y-%m-%d')][viplevel] = money
            self.datelist.append(self.begindate.strftime('%Y-%m-%d'))
            self.begindate += datetime.timedelta(days=1)
            # print(sqlstr)
#somkeys as writeindex
#somedict as


#####write xlwt
    def xls_writeone_list(self,sheet,name,somekeys, somedict, indexi=0, indexj=0):
        # xls_writer = EasyXls.EasyXls()
        defaultencoding = 'utf-8'
        if sys.getdefaultencoding() != defaultencoding:
            reload(sys)
            sys.setdefaultencoding(defaultencoding)

        sheet.write(indexi, indexj, unicode(name))
        indexi += 1
        for i in range(len(somekeys)):
            sheet.write(indexi + i, 0, somekeys[i])
            dictlist = somedict[somekeys[i]].split(",")
            for j in range(len(dictlist)):
                sheet.write(i + indexi, j + indexj + 1, eval(dictlist[j]))

    def sheetadd(self,strsheet):
        # strsheet is a string
        self.sheet = self.wbk.add_sheet(strsheet, cell_overwrite_ok=True)

    def xls_writetwo_dict(self, sheet, name, somekeyy, somekeyx, somedict, indexi=0, indexj=0):
        # sheet is func sheetadd's return
        # name is what you want to write
        # somekey is the index you want to write
        # some dict is the content you wang to write
        defaultencoding = 'utf-8'
        if sys.getdefaultencoding() != defaultencoding:
            reload(sys)
            sys.setdefaultencoding(defaultencoding)

        sheet.write(indexi, indexj, unicode(name))
        indexi += 2
        for i in range(len(somekeyy)):
            sheet.write(i + indexi, indexj, unicode(somekeyy[i]))
        for j in range(len(somekeyx)):
            sheet.write(indexi - 1, j + 1 + indexj, somekeyx[j])
            for i in range(len(somekeyy)):
                try:
                    sheet.write(i + indexi, j + 1 + indexj, somedict[somekeyx[j]].setdefault(somekeyy[i], ''))
                except:
                    sheet.write(i + indexi, j + 1 + indexj, '')

    def end_all(self):
        file_name =ConfParameters.ConfParameters().save_path+ 'lostandpay' + self.channel[0:20] + '.xls'
        self.db.close()
        self.wbk.save(file_name)



    def runwrite(self):
        self.lost_ratio()
        self.sheetadd('sheet1')
        self.xls_writetwo_dict(self.sheet,unicode('老玩家流失率'),self.viplist,self.datelist,self.totaldict)
        self.xls_writetwo_dict(self.sheet, unicode('老玩家活跃人数'), self.viplist, self.datelist, self.peopledict,25,0)
        self.pay_ratio()
        self.sheetadd('sheet2')
        self.xls_writetwo_dict(self.sheet,unicode('老玩家付费率'),self.viplist,self.datelist,self.paydict)
        self.xls_writetwo_dict(self.sheet, unicode('老玩家付费金额'), self.viplist, self.datelist, self.moneydict,25,0)
        self.new_lostratio()
        self.sheetadd('sheet3')
        self.xls_writeone_list(self.sheet,unicode('新玩家情况'),self.datelist,self.newnumdict)
        # self.itembuy('2018-09-25','2018-10-18')
        # self.sheetadd('itembuy')
        # self.xls_writetwo_dict(self.sheet,'itembuyratio0925-1018',self.itemlist,self.viplist,self.itembuyratio)
        # self.xls_writetwo_dict(self.sheet, 'itemavg0925-1018', self.itemlist, self.viplist, self.itemavgtimes,25,0)
        # self.xls_writetwo_dict(self.sheet, 'itembuypeople0925-1018', self.itemlist, self.viplist, self.itembuypeople, 50, 0)
        # self.xls_writetwo_dict(self.sheet, 'activepeople0925-1018', self.itemlist, self.viplist, self.activepeople,75, 0)
        self.itembuy('2018-11-22','2018-12-11')
        self.xls_writetwo_dict(self.sheet,'itembuyratio1122-1211',self.itemlist,self.viplist,self.itembuyratio,0,26)
        self.xls_writetwo_dict(self.sheet, 'itemavg1122-1211', self.itemlist, self.viplist, self.itemavgtimes,25,26)
        self.xls_writetwo_dict(self.sheet, 'itembuypeople1122-1211', self.itemlist, self.viplist, self.itembuypeople, 50, 26)
        self.xls_writetwo_dict(self.sheet, 'activepeople1122-1211', self.itemlist, self.viplist, self.activepeople, 75, 26)

        self.end_all()

    def runall(self):
        self.allchannel()
        self.runwrite()

    def runformalold(self):
        self.formalchannel()
        self.runwrite()

    def runjinyou(self):
        self.jinyouchannel()
        self.runwrite()

    def runyiyou(self):
        self.yiyouchannel()
        self.runwrite()

###newuser
    #newuser firstday reten sevenday reten
    def new_lostratio(self):
        self.begindate = datetime.datetime.strptime(sys.argv[1], '%Y-%m-%d')
        self.enddate = datetime.datetime.strptime(sys.argv[2], '%Y-%m-%d')
        self.datelist = []
        sqlstr='select date,sum(case period when 0 then count else 0 end)as day0,sum(case period when 1 then count else 0 end)/sum(case period when 0 then count else 0 end) as day1ratio,sum(case period when 6 then count else 0 end)/sum(case period when 0 then count else 0 end) as day7ratio,sum(case period when 6 then payusers else 0 end) as payusers7,sum(case period when 6 then money else 0 end) as money7,sum(case period when 6 then payusers else 0 end)/sum(case period when 0 then count else 0 end) as payratio7,sum(case period when 6 then money else 0 end)/sum(case period when 0 then count else 0 end) as arpu7,sum(case period when 6 then money else 0 end)/sum(case period when 6 then payusers else 0 end) as arppu7 from(select date,period,sum(count) as count,sum(money/100) as money,sum(payusers) as payusers from user_reten_pay where period in (0,1,6) and date between \"'+self.begindate.strftime('%Y-%m-%d')+'\" and \"'+self.enddate.strftime('%Y-%m-%d')+'\" '+self.channel+' group by date,period) as a group by date;'

    # | date | day0 | day1ratio | day7ratio | payusers7 | money7 | payratio7 | arpu7 | arppu7 |
    # +------------+-------+-----------+-----------+-----------+-------------+-----------+-------------+--------------+
    # | 2018 - 07 - 01 | 2648 | 0.1469 | 0.0540 | 115 | 51478.0000 | 0.0434 | 19.44033233 | 447.63478261 |


        self.cursor.execute(sqlstr)
        alldata = self.cursor.fetchall()
        if alldata:
            for rec in alldata:
                keydate = str(rec[0])
                newnumber = str(rec[1])
                firstdayratio = str(rec[2])
                sevendayratio = str(rec[3])
                self.newnumdict[keydate] = newnumber+","+firstdayratio+","+sevendayratio+","+ str(rec[4])+","+str(rec[5])+","+str(rec[6])+","+str(rec[7])+","+str(rec[8])
                # self.new_firstdaydict[keydate]= firstdayratio
                # self.new_sevendaydict[keydate]= sevendayratio
                self.datelist.append(keydate)

    def itembuy(self,itembegindate,itemenddate):

        for i in self.viplist:
            self.itembuyratio[i]=dict()
            self.itemavgtimes[i]=dict()
            self.itembuypeople[i]=dict()
            self.activepeople[i]=dict()
        sqlstr ='select itemid,e.mvip,sum(uid),sum(times),e.totalnums,sum(uid)/e.totalnums as buyratio,sum(times)/sum(uid) as avgtimes from (select itemid,c.mvip,count(uid) as uid,sum(times) as times from (select a.uid,a.itemid,a.times,b.mvip from (select uid,itemid,count(uid) as times from modernship_gf_stat_base.pay_syn_day_extend where date between \"'+itembegindate+'\" and \"'+ itemenddate +'\" '+self.channel+' and itemid in (80,81) and uid not in (select uid from modernship_stat_busi.uid_block_list) group by uid,itemid) as a inner join (select uid,max(vip_level) as mvip from modernship_gf_stat_base.user_active_extend where date between \"'+itembegindate+'\" and \"'+ itemenddate +'\" '+self.channel+' and uid not in (select uid from modernship_stat_busi.uid_block_list)  group by uid) as b on a.uid=b.uid) as c group by itemid,mvip) as f inner join (select mvip,count(uid) as totalnums from (select uid,max(vip_level) as mvip from modernship_gf_stat_base.user_active_extend where date between \"'+itembegindate+'\" and \"'+ itemenddate +'\" '+self.channel+' and uid not in (select uid from modernship_stat_busi.uid_block_list) group by uid) as d group by mvip) as e on f.mvip=e.mvip group by mvip,itemid;'

        self.cursor.execute(sqlstr)
        alldata = self.cursor.fetchall()
    # | itemid | mvip | sum(uid) | sum(times) | totalnums | buyratio | avgtimes |
    # +--------+------+----------+------------+-----------+----------+----------+
    # | 53 | 1 | 78 | 93 | 3340 | 0.0234 | 1.1923 |
    # | 30 | 2 | 30 | 30 | 635 | 0.0472 | 1.0000 |
    # | 47 | 2 | 11 | 17 | 635 | 0.0173 | 1.5455 |
    # | 53 | 2 | 31 | 46 | 635 | 0.0488 | 1.4839 |

        if alldata:
            for rec in alldata:
                self.itembuyratio[str(rec[1])][rec[0]]=rec[5]
                self.itemavgtimes[str(rec[1])][rec[0]]=rec[6]
                self.itembuypeople[str(rec[1])][rec[0]]=rec[2]
                self.activepeople[str(rec[1])][rec[0]]=rec[4]

    # def vipgiftbuy(self):
    #     cmdstr=''
    #     val = os.popen(cmdStr).readlines()
    #     for line in val:
    #         line = line.strip()
    #         line = line.split(",")


if __name__ == '__main__':
    # NewOldSituation().runformalold()
    # NewOldSituation().runjinyou()
    # NewOldSituation().runyiyou()
    NewOldSituation().runall()