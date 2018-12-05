#!/usr/bin/python
# -*- coding: UTF-8 -*-

from providers import ProviderFactory
from task.Settlement import Settlement
from models import purse,conn

import time
import datetime

# print purse.getBuyin('11', '11')
# conn.close()
# exit(0)
# now = datetime.datetime.now()
# nowstr = now.strftime('%Y-%m-%d %H:%M:%S')
# print(nowstr)

# delta = datetime.timedelta(days=-3)
# n_days = now + delta
# n_daysstr = n_days.strftime('%Y-%m-%d %H:%M:%S')
# print(n_daysstr)

# bzlProvider = ProviderFactory.createProvider({
#     'name': 'bzl-provider',
#     'description': '宝芝林提供商(通用提供商)',
#     'module': 'providers.implements.CommonProvider',
#     'className': 'CommonProvider',
#     'username': 'controller12',
#     'password': '5589',
#     'apiUrl': 'https://yqdp-manager689125.gakuen.fun/api',
#     'transferCurrentGames': False,
# })

# settlement = Settlement(bzlProvider)

# settlement.settlement()

t = datetime.datetime.strptime('2018-12-03 18:32:43','%Y-%m-%d %H:%M:%S')
t = t + datetime.timedelta(seconds = -60)

print(str(t))

# bzlProvider.getBuyin()

# cmsProvider =  ProviderFactory.createProvider({
#     'name': 'cms-provider',
#     'description': '自建CMS的提供商',
#     'module': 'providers.implements.cmsprovider.CmsProvider',
#     'className': 'CmsProvider',
#     'username': '18206774149',
#     'password': 'aa8888',
#     'transferCurrentGames': True,
#     'apiUrl': 'http://cms.pokermanager.club/cms-api',
# })
# cmsProvider.getBuyin()

# print({'name': 'aaa'})
