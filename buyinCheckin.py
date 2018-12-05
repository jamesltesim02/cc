#!/usr/bin/python
# -*- coding: UTF-8 -*-

from providers import ProviderFactory
from models import purse,conn,buyin

# print purse.getBuyin('11', '11')
# conn.close()
# exit(0)
cp = ProviderFactory.createProvider({
    'name': 'common-provider',
    'description': '通用提供商',
    'module': 'providers.implements.CommonProvider',
    'className': 'CommonProvider',
    'username': 'controller12',
    'password': '5589',
    'apiUrl': 'https://yqdp-manager689125.gakuen.fun/api',
})
list =  cp.getBuyin()
for item in list:
    if ['suggest']) > -2:
        purseInfo = purse.getPurseInfoByGameId(item['pccid'])
        if purseInfo:
            data = {
                'club_name':item["club_name"], 
                'pccid':item["pccid"],
                'pccname':item["pccname"],
                'room_uuid':item["room_uuid"],
                'stack':item["stack"],
                'amounts':item["amounts"]
            }
            if int(purseInfo['cash']) >= int(item['amounts']):
                code = cp.acceptBuyin(data)
                if code == 200:              
                    try:
                        buyin.addBuyinLog(purseInfo, item, 'accept')
                        purse.updatePurse(purseInfo, -int(item['amounts']))
                        conn.commit()
                    finally:
                        conn.rollback()
                    continue
            else:               
                code = cp.denyBuyin(data)
                if code == 200:
                    buyin.addBuyinLog(purseInfo, item, 'deny')
                    conn.commit()

        else:
            code = cp.denyBuyin(data)
            if code == 200:
                purseInfo = {}
                purseInfo['frontend_user_id'] = 'no purse'
                purseInfo['frontend_user_auth'] = 'no purse'
                purseInfo['game_vid'] = item["pccid"]
                buyin.addBuyinLog(purseInfo, item, 'deny')
                conn.commit()