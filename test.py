#!/usr/bin/python
# -*- coding: UTF-8 -*-
from task.buyinCheckin import BuyinCheckin
from task.Settlement import Settlement

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


t1 = Settlement(1)
t1.setApi({
    'name': 'bzl-provider',
    'description': '通用提供商',
    'module': 'providers.implements.CommonProvider',
    'className': 'CommonProvider',
    'username': 'controller12',
    'password': '5589',
    'apiUrl': 'https://yqdp-manager689125.gakuen.fun/api',
})
t1.start()
# t1.callback()