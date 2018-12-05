#!/usr/bin/python
# -*- coding: UTF-8 -*-

from providers import ProviderFactory
from task.Settlement import Settlement
from models import purse,conn

# print purse.getBuyin('11', '11')
# conn.close()
# exit(0)

bzlProvider = ProviderFactory.createProvider({
    'name': 'bzl-provider',
    'description': '宝芝林提供商(通用提供商)',
    'module': 'providers.implements.CommonProvider',
    'className': 'CommonProvider',
    'username': 'controller12',
    'password': '5589',
    'apiUrl': 'https://yqdp-manager689125.gakuen.fun/api',
    'transferCurrentGames': False,
})

settlement = Settlement(bzlProvider)

settlement.aaa()
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

