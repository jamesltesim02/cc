#!/usr/bin/python
# -*- coding: UTF-8 -*-


from models import purse,conn,buyin
from .task import Task
import json

class BuyinCheckin(Task):

    def callback(self):
        list =  self.api.getBuyin()
        for item in list:
            if int(item['suggest']) > -2:
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
                        code = self.api.acceptBuyin(data)
                        if code == 200:              
                            try:
                                buyin.addBuyinLog(purseInfo, item, 'accept')
                                purse.updatePurse(purseInfo, -int(item['amounts']))
                                conn.commit()
                            except Exception as e:
                                print e
                                conn.rollback()
                            continue
                    else:               
                        code = self.api.denyBuyin(data)
                        if code == 200:
                            buyin.addBuyinLog(purseInfo, item, 'deny')
                            conn.commit()

                else:
                    code = self.api.denyBuyin(data)
                    if code == 200:
                        purseInfo = {}
                        purseInfo['frontend_user_id'] = 'no purse'
                        purseInfo['frontend_user_auth'] = 'no purse'
                        purseInfo['game_vid'] = item["pccid"]
                        buyin.addBuyinLog(purseInfo, item, 'deny')
                        conn.commit()