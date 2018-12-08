#!/usr/bin/python
# -*- coding: utf-8 -*-


import pymysql

def conn(config):
	return pymysql.connect(host=config['host'],
                   port=config['port'],
                   user=config['user'],
                   password=config['password'],
                   db=config['db'],
                   # charset=config['charset'],
                   cursorclass=pymysql.cursors.DictCursor,
                   autocommit=False)
