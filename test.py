#!/usr/bin/python
# -*- coding: UTF-8 -*-
from task.buyinCheckin import BuyinCheckin
from task.Settlement import Settlement
from config import config

t = BuyinCheckin(1)
t.setApi(config)
# t.start()
t.callback()


t1 = Settlement(1)
t1.setApi(config)
# t1.start()
# t1.callback()