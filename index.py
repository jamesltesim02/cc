#!/usr/bin/python
# -*- coding: UTF-8 -*-

from providers import ProviderFactory
from models import purse,conn

print purse.getBuyin('11', '11')
conn.close()
exit(0)

bzlProvider = ProviderFactory.createProvider({
    'name': 'bzl-provider',
    'description': '宝芝林提供商(通用提供商)',
    'module': 'providers.implements.CommonProvider',
    'className': 'CommonProvider',
    'username': 'controller12',
    'password': '5589',
    'loginApi': 'https://yqdp-manager689125.gakuen.fun/api/login_admin',
    'buyinApi': 'https://yqdp-manager689125.gakuen.fun/api/club_buyin',
    'acceptApi': 'https://vnt-ceo861.strong.zone/api/control_cms/accept_buy',
    'denyApi': 'https://vnt-ceo861.strong.zone/api/control_cms/deny_buy',
    'gameDetailsApi': 'http://api.bzpk44.com/index.php?c=export'
    'transferCurrentGames': False,
    'apiUrl': 'https://yqdp-manager689125.gakuen.fun/api',
})
bzlProvider.getBuyin()

cmsProvider =  ProviderFactory.createProvider({
    'name': 'cms-provider',
    'description': '自建CMS的提供商',
    'module': 'providers.implements.cmsprovider.CmsProvider',
    'className': 'CmsProvider',
    'username': '18206774149',
    'password': 'aa8888',
    'transferCurrentGames': True,
    'apiUrl': 'http://cms.pokermanager.club/cms-api',
})
cmsProvider.getBuyin()
