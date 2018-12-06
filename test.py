#!/usr/bin/python
# -*- coding: UTF-8 -*-
from task.buyinCheckin import BuyinCheckin

t = BuyinCheckin(1)
t.setApi({
    'name': 'common-provider',
    'description': '通用提供商',
    'module': 'providers.implements.CommonProvider',
    'className': 'CommonProvider',
    'username': 'controller12',
    'password': '5589',
    'apiUrl': 'https://yqdp-manager689125.gakuen.fun/api',
})
# t.start()
# t.callback()