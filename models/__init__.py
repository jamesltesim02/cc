#!/usr/bin/python
# -*- coding: utf-8 -*-


import pymysql

conn = pymysql.connect(host='54.213.203.214',
                       port=3306,
                       user='test',
                       password='10-9=1',
                       db='holdem',
                       charset='utf8',
                       cursorclass=pymysql.cursors.DictCursor)
