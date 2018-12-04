#!/usr/bin/python
# -*- coding: UTF-8 -*-

from providers import ProviderFactory

bzlProvider = ProviderFactory.createProvider({
    'name': 'bzl-provider',
    'description': '宝芝林提供商(通用提供商)',
    'module': 'providers.implements.CommonProvider',
    'className': 'CommonProvider',
    'username': 'controller12',
    'password': '5589',
    'apiUrl': 'https://yqdp-manager689125.gakuen.fun/api/',

    # 'loginApi': 'https://yqdp-manager689125.gakuen.fun/api/login_admin',
    # 'buyinApi': 'https://yqdp-manager689125.gakuen.fun/api/club_buyin',
    # 'acceptApi': 'https://yqdp-manager689125.gakuen.fun/api/control_cms/accept_buy',
    # 'denyApi': 'https://yqdp-manager689125.gakuen.fun/api/control_cms/deny_buy',
    # 'queryUserBoardApi': 'https://yqdp-manager689125.gakuen.fun/api/control_cms/query_user_board',
})
bzlProvider.getBuyin()

# cmsProvider =  ProviderFactory.createProvider({
#     'name': 'cms-provider',
#     'description': '自建CMS的提供商',
#     'module': 'providers.implements.cmsprovider.CmsProvider',
#     'className': 'CmsProvider',
#     'username': '18206774149',
#     'password': 'aa8888',
#     ''
# })
# cmsProvider.getBuyin()
