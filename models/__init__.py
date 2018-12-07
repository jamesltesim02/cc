#!/usr/bin/python
# -*- coding: utf-8 -*-


import pymysql

def conn(config):
	return pymysql.connect(host=config['db']['host'],
                   port=config['db']['port'],
                   user=config['db']['user'],
                   password=config['db']['password'],
                   db=config['db']['host'],
                   charset=config['db']['host'],
                   cursorclass=pymysql.cursors.DictCursor,
                   autocommit=False)
