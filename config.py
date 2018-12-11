#!/usr/bin/python
# -*- coding: UTF-8 -*-


config = {
	'bzl-provider':{
		'name': 'bzl-provider',
	    'description': '通用提供商',
	    'module': 'providers.implements.CommonProvider',
	    'className': 'CommonProvider',
	    'serviceCode': 4,
	    'apiUrl': 'https://yqdp-manager689125.gakuen.fun/api',
		'localDataPath': 'C:/workspace/cc/task/upload/'
	},
	'cms-provider':{
		'name': 'cms-provider',
	    'description': '通用提供商',
	    'module': 'providers.implements.CmsProvider',
	    'className': 'CmsProvider',
	    'serviceCode': 6,
	    'apiUrl': 'http://cms.pokermanager.club',
	},
	"db":{
		"host":"54.213.203.214",
		"port":3306,
		"user":'test',
		"password":'10-9=1',
		"db":'holdem',
		"charset":'utf8',
	}
}