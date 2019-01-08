#!/usr/bin/python
#-- coding: utf-8 --

from providers import ProviderFactory
from config import config

def getCurrentGameList():
    cmsProvider = ProviderFactory.createProvider(config['cms-provider'], config['db'])
    return cmsProvider.getCurrentGameList()

if __name__ == "__main__":
    result = getCurrentGameList()
    print ('gameList:', result)