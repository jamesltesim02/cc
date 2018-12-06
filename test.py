#!/usr/bin/python
# -*- coding: UTF-8 -*-
from task.buyinCheckin import BuyinCheckin

t = BuyinCheckin(10)
print t
t.setApi({
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
t.start()