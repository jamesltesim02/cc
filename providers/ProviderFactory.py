#!/usr/bin/python
# -*- coding: UTF-8 -*-

from ProviderInterface import ProviderInterface

def createProvider(conf):
    providerModule = __import__(conf['module'])
    moduleNames = conf['module'].split('.')
    moduleNames.pop(0)
    for mname in moduleNames:
        providerModule = getattr(providerModule, mname)
    providerType = getattr(providerModule, conf['className'])

    if issubclass(providerType, ProviderInterface):
        return providerType(conf)

    raise Exception('provider必须继承自ProviderInterface')