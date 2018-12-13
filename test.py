#!/usr/bin/python
# -*- coding: UTF-8 -*-
# from task.buyinCheckin import BuyinCheckin
# from task.Settlement import Settlement
# from config import config
# from providers import ProviderFactory

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


data = {
    'm': '1'
}

data['m'] = int(float(data['m']))
print(data)