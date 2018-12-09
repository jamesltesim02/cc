#!/usr/bin/python
# -*- coding: UTF-8 -*-
from task.buyinCheckin import BuyinCheckin
from task.Settlement import Settlement
from config import config

# 代理商自动审批任务, 每5秒执行一次
t = BuyinCheckin(5)
t.setApi(config)
# t.start()
t.callback()

# 代理商自动结算任务, 每10秒执行一次
t1 = Settlement(10)
t1.setApi(config)
# t1.start()