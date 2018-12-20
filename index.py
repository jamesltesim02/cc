#!/usr/bin/python
# -*- coding: UTF-8 -*-
from task.buyinCheckin import BuyinCheckin
from task.Settlement import Settlement
from task.CmsBuyinCheckin import CmsBuyinCheckin
from task.CmsSettlement import CmsSettlement
from config import config

# 代理商自动审批任务, 每5秒执行一次
# t = BuyinCheckin(8)
# t.setApi(config)
# t.start()


# 代理商自动结算任务, 每10秒执行一次
# t1 = Settlement(10)
# t1.setApi(config)
# t1.start()


# CMS自动审批任务, 每5秒执行一次
# t2 = CmsBuyinCheckin(8)
# t2.setApi(config)
# t2.start()
# t2.callback()

# CMS代理商自动结算任务, 每10秒执行一次
t3 = CmsSettlement(10)
t3.setApi(config)
# t3.start()
t3.callback()