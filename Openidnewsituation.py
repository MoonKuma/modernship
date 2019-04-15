



import conf.ConfParameters as ConfParameters
import util.DateList as DateList
import util.EasyXls as EasyXls
import os
import MySQLdb
import xlwt
import sys
import calendar
import datetime

class Openidnewsituation:
    def __init__(self):
        self.channel=''
        self.start_date = '2018-09-01'
        self.end_date = '2018-09-30'
        self.channel_notin=(1099, 109902, 109903, 1105, 1098, 109802, 1100, 1104, 1101)
        self.month=[]
        self.stayratio=dict()
        self.payratio=dict()
        # initial mysql-db
        mysql_para = ConfParameters.ConfParameters().mysql_conf
        self.db = MySQLdb.connect(mysql_para['ip'], mysql_para['users'], mysql_para['password'],mysql_para['stat_base'])

        self.cursor = self.db.cursor()
        # initial xls writer
        self.wbk = xlwt.Workbook()
        self.sheet = self.wbk.add_sheet('Sheet1', cell_overwrite_ok=True)
        return

    def set_channel(self,new_channel):
        return 'and channel='+str(new_channel)

    # def run_sql(self,start_date,end_date,channel):
    #     # select sum(case period when 0 then count else 0 end) as totalnew,sum(case period when 1 then count else 0 end) as onedaylast,sum(case period when 6 then count else 0 end) as sevendaylast from  user_reten_openid where date>="2018-09-01" and channel=1007
    #     sql_str='select sum(case period when 0 then count else 0 end) as totalnew,sum(case period when 1 then count else 0 end) '
    #     sql_str+='as onedaylast,sum(case period when 6 then count else 0 end) as sevendaylast,sum(case period when 1 then count else 0 end)/sum(case period when 0 then count else 0 end) as onedayratio,sum(case period when 6 then count else 0 end)/sum(case period when 0 then count else 0 end) as sevendayratio from  user_reten_openid where date>='
    #     sql_str+=start_date + 'and date<='+end_date +channel+';'
    #     self.cursor.execute(sql_str)
    #     all_data=self.cursor.fetchall()
    #     result=0
    #     if(all_data):
    #         rec=all_data
    #     print(rec)
    #     return rec


    def stay_ratio(self,channel):
        sqlstr='select substr(date,1,7) as month,sum(case period when 0 then count else 0 end) as totalnew,sum(case period when 1 then count else 0 end) as onedaylast,sum(case period when 6 then count else 0 end) as sevendaylast,sum(case period when 1 then count else 0 end)/sum(case period when 0 then count else 0 end) as onedayratio,sum(case period when 6 then count else 0 end)/sum(case period when 0 then count else 0 end) as sevendayratio from  stat_base.user_reten_openid where channel not in'+str(self.channel_notin)+str(channel)+' group by month;'

        self.cursor.execute(sqlstr)
        all_data = self.cursor.fetchall()
        result = 0
        if (all_data):
            for rec in all_data:
                if rec[0]>'2018-03':
                    self.stayratio[rec[0]] =str(rec[1])+","+str(rec[4])+","+str(rec[5])
                    self.month.append(rec[0])
                    print(self.stayratio[rec[0]])
         # return
    def pay_ratio(self):
        print(self.month)
        for i in self.month:
            interval= calendar.monthrange(int(i[0:4]),int(i[5:7]))
            i= datetime.datetime.strptime(i,"%Y-%m")
            enddate=i+datetime.timedelta(days=interval[1])
            enddate=datetime.datetime.strftime(enddate,"%Y-%m-%d")
            begindate=datetime.datetime.strftime(i,"%Y-%m-%d")
            sqlstr='select substr(date,1,7) as month,count(distinct(openid)),sum(money/100) from stat_pay.pay_syn_day where date>=\"'+begindate+'\" and date<\"'+enddate+'\" and channel not in '+str(self.channel_notin)+' and openid in (select openid from stat_userreg.user_register_openid where date>=\"'+begindate+'\" and date<\"'+enddate+'\" and channel not in '+str(self.channel_notin)+');'
            self.cursor.execute(sqlstr)
            all_data = self.cursor.fetchall()

            if (all_data):
                for rec in all_data:
                        self.payratio[rec[0]] = str(rec[1]) + "," + str(rec[2])
                        print(self.payratio[rec[0]])


#write onelevel dict
    def xls_writeone(self,somekeys,somedict,name,indexi=0,indexj=0):
        # xls_writer = EasyXls.EasyXls()


        defaultencoding = 'utf-8'
        if sys.getdefaultencoding() != defaultencoding:
            reload(sys)
            sys.setdefaultencoding(defaultencoding)

        self.sheet.write(indexi, indexj, unicode(name))
        indexi+=1
        for i in range(len(somekeys)):
            self.sheet.write(indexi+i,0,somekeys[i])
            dictlist=somedict[somekeys[i]].split(",")
            for j in range(len(dictlist)):

                self.sheet.write(i + indexi, j+indexj+1, eval(dictlist[j]))



    def end_all(self):
        file_name='/data/tmpStatistic/monthchange.xls'
        self.db.close()
        self.wbk.save(file_name)

if __name__ == '__main__':
    objone=Openidnewsituation()
    objone.stay_ratio()
    objone.pay_ratio()
    objone.xls_writeone(objone.month,objone.stayratio,'openidstayratio')
    objone.xls_writeone(objone.month,objone.payratio, 'openidpayratio',0,4)
    objone.end_all()




