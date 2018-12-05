#!/usr/bin/python
# -*- coding: UTF-8 -*-

from providers import ProviderFactory
# from models import purse,conn

# print purse.getBuyin('11', '11')
# conn.close()
# exit(0)
cp = ProviderFactory.createProvider({
    'name': 'common-provider',
    'description': '通用提供商',
    'module': 'providers.implements.CommonProvider',
    'className': 'CommonProvider',
    'username': 'controller12',
    'password': '5589',
    'loginApi': 'https://yqdp-manager689125.gakuen.fun/api/login_admin',
    'buyinApi': 'https://yqdp-manager689125.gakuen.fun/api/club_buyin',
    'acceptApi': 'https://vnt-ceo861.strong.zone/api/control_cms/accept_buy',
    'denyApi': 'https://vnt-ceo861.strong.zone/api/control_cms/deny_buy',
    'gameDetailsApi': 'http://api.bzpk44.com/index.php?c=export'
})
list =  cp.getBuyin()
for item in list:
    print item
# cp.getHistoryGameDetails({'startdate':'2018-12-01', 'enddate':'2018-12-09'})