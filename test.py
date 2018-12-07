#!/usr/bin/python
# -*- coding: UTF-8 -*-
from task.buyinCheckin import BuyinCheckin
from task.Settlement import Settlement
from config import config

t = BuyinCheckin(5)
t.setApi(config)
t.start()


t1 = Settlement(10)
t1.setApi(config)
t1.start()