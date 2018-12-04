#!/usr/bin/python
# -*- coding: UTF-8 -*-

from providers import ProviderFactory
from models import purse,conn

print purse.getBuyin('11', '11')
conn.close()
exit(0)
cp = ProviderFactory.createProvider({
    'name': 'common-provider',
    'description': '通用提供商',
    'module': 'providers.implements.CommonProvider',
    'className': 'CommonProvider',
    'username': 'boss',
    'password': 'asdf',
    'loginApi': 'https://vnt-ceo861.strong.zone/api/login_boss',
    'buyinApi': 'https://vnt-ceo861.strong.zone/api/club_buyin',
    'acceptApi': 'https://vnt-ceo861.strong.zone/api/control_cms/accept_buy',
    'denyApi': 'https://vnt-ceo861.strong.zone/api/control_cms/deny_buy',
    'gameDetailsApi': 'http://api.bzpk44.com/index.php?c=export'
})
cp.getBuyin()