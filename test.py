#!/usr/bin/python
# -*- coding: UTF-8 -*-
from task.buyinCheckin import BuyinCheckin
from task.CmsBuyinCheckin import CmsBuyinCheckin
from task.CmsSyncGaming import CmsSyncGaming
from task.Settlement import Settlement
from config import config
from providers import ProviderFactory
import requests

c = CmsBuyinCheckin(5)
c.setApi(config)
c.start()

# c = CmsSyncGaming(5)
# c.setApi(config)
# c.callback()

# t = BuyinCheckin(5)
# t.setApi(config)
# # t.start()
# t.callback()


# t1 = Settlement(10)
# t1.setApi(config)
# # t1.start()
# t1.callback()

# p = ProviderFactory.createProvider(config['cms-provider'], config['db'])
# print p.getBuyin()

# print(float(5)/100)