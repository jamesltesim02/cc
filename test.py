#!/usr/bin/python
# -*- coding: UTF-8 -*-
from task.buyinCheckin import BuyinCheckin
from task.CmsBuyinCheckin import CmsBuyinCheckin
from task.CmsSyncGaming import CmsSyncGaming
from task.Settlement import Settlement
from task.CocoAutoTask import CocoAutoTask
from config import config
from providers import ProviderFactory
import requests
import time

# c = CmsBuyinCheckin(5)
# c.setApi(config)
# c.start()

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
# print(int(time.time() * 1000))

t3 = CocoAutoTask(2)
t3.setApi(config)
# t3.callback()
t3.start()
