#!/usr/bin/python
# -*- coding: UTF-8 -*-


config = {
	'bzl-provider': {
		'name': 'bzl-provider',
	    'description': '通用提供商',
	    'module': 'providers.implements.CommonProvider',
	    'className': 'CommonProvider',
	    'serviceCode': 4,
	    'apiUrl': 'https://yqdp-manager689125.gakuen.fun/api',
		'localDataPath': '/Volumes/rey/work/PHP/Holdem/Uploads/settlement/'
	},
	'cms-provider': {
		'name': 'cms-provider',
	    'description': 'CMS提供商',
	    'module': 'providers.implements.CmsProvider',
	    'className': 'CmsProvider',
	    'serviceCode': 6,
		'cloubId': '21647880',
	    'apiUrl': 'http://cms.pokermanager.club',
	},
	'coco-provider': {
		'name': 'coco-provider',
	    'description': 'coco提供商',
	    'module': 'providers.implements.CocoProvider',
	    'className': 'CocoProvider',
	    'serviceCode': 7,
	    'apiUrl': 'https://www.cmsweb.club',
		'wsUrl': 'https://www.cmsweb.club:8000'
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