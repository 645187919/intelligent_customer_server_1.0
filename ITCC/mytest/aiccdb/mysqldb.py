#coding=utf-8
#
# con = pymysql.connect(host="192.168.112.200", user="root", password="root", database="test1", charset="utf8")
# cursor = con.cursor()
# try:
#     # 当id设置为主键，但是没有设置为自增时，则必须给id字段赋值，否则会报错。
#     sql = "select * from Teacher;"
#     cursor.execute(sql)
#     # 单使用一个fetchone会获取索引为0的记录，若使用多个fetchone时，会按照前一个的索引值继续向下获取记录
#     data1 = cursor.fetall()
#
# except Exception as e:
#     print("error")
# cursor.close()
# con.close()
# print(data1)
# print(data2)
# print(data3)

# 添加
# 创建testInsertWrap.py文件，使用封装好的帮助类完成插入操作
#encoding=utf8
# from MysqlHelper import *

# encoding=utf8

from mytest.aiccdb.mysqlhelper import MysqlHelper


class mysqldb:


    def __init__(self,keyword):
        self.kw=keyword


    def query(keyword):
        #第一个问题：not enough arguments for format string
        #出现这类问题，主要是字符串中包含了%号，python 认为它是转移符，而实际我们需要的就是%， 这个时候，可以使用%%来表示
        #第二个问题：/为转义字符，需要将这里的‘转义
        KW=keyword[0]
        print(KW)
        sql='select * from Teacher where Tname like \'%%'+ keyword[0] +'%%\''
        # sql='select * from Teacher'
        print(sql)
        helper=MysqlHelper('192.168.112.200',3306,'test1','root','root')
        one=helper.get_all(sql)
        print(one)
        # ((u'01', u'\u5f20\u4e09'), (u'04', u'\u5f20\u4e09\u4e30'))
        # (u'01', u'\u5f20\u4e09')
        for exmple in one:
            print(exmple)
            #问题三：将输出的转义码通过以下的eval方法转化为对应的中文
            print(eval("u"+"\'"+exmple[1]+"\'"))
            print(eval("u"+"\'"+exmple[0]+"\'"))




